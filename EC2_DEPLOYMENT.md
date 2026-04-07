# AWS EC2 Deployment Guide

Complete guide to deploy the Airline RAG Chatbot on AWS EC2.

## Prerequisites

- AWS Account with EC2 access
- AWS CLI configured locally (optional)
- SSH key pair downloaded
- Domain name (optional, for custom URL)

## Step 1: Launch EC2 Instance

### Using AWS Console

1. Go to **EC2 Dashboard** → **Instances** → **Launch Instances**

2. **Choose AMI**:
   - Select: **Ubuntu Server 24.04 LTS** (free tier eligible)
   - Architecture: **64-bit (x86)**

3. **Instance Type**:
   - Select: **t2.micro** (free tier) or **t2.small** (recommended for better performance)

4. **Configure Instance**:
   - Number of instances: **1**
   - Subnet: default VPC
   - Auto-assign public IP: **Enable**

5. **Storage**:
   - Size: **30 GB** (free tier allows up to 30GB)
   - Type: **gp3** (General Purpose SSD)
   - Delete on Termination: **Yes**

6. **Security Group** (Create New):
   - Name: `airline-rag-chatbot-sg`
   - Description: Security group for RAG chatbot
   
   **Inbound Rules**:
   ```
   Type              | Protocol | Port | Source
   SSH               | TCP      | 22   | 0.0.0.0/0 (or your IP)
   HTTP              | TCP      | 80   | 0.0.0.0/0
   HTTPS             | TCP      | 443  | 0.0.0.0/0
   Custom TCP        | TCP      | 8501 | 0.0.0.0/0 (Streamlit)
   ```

7. **Key Pair**:
   - Create new key pair, download `.pem` file
   - Save securely!

8. **Review & Launch**
   - Click **Launch Instances**
   - Wait for instance to be **running**

## Step 2: Connect to EC2

### Get Public IP

```bash
# From AWS Console: Instances → Copy "Public IPv4 address"
# Example: 54.123.45.67
```

### SSH Connection

```bash
# Change permissions (one-time)
chmod 400 your-key.pem

# Connect
ssh -i your-key.pem ubuntu@54.123.45.67
```

## Step 3: Install Dependencies

Run these commands on the EC2 instance:

```bash
# Update system packages
sudo apt update
sudo apt upgrade -y

# Install Python and pip
sudo apt install -y python3 python3-pip python3-venv git

# Install system dependencies for data science libraries
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev

# Verify installation
python3 --version
pip3 --version
```

## Step 4: Clone Repository

```bash
# Clone the repo
git clone https://github.com/anushagoli07/RAG-Airline-using-Bedrock-Titan-Novapro-FAISS.git
cd RAG-Airline-using-Bedrock-Titan-Novapro-FAISS

# List files to verify
ls -la
```

## Step 5: Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python3 -c "import streamlit; import boto3; print('✓ All dependencies installed')"
```

## Step 6: Configure AWS Credentials

### Option A: Using IAM User (Recommended)

1. **Create IAM User in AWS Console**:
   - Go to **IAM** → **Users** → **Create user**
   - Name: `airline-rag-bot`
   - Attach policy: `AmazonBedrockFullAccess`
   - Create **Access Key** (CLI)
   - Download CSV with credentials

2. **On EC2, configure credentials**:
   ```bash
   # Create credentials file
   mkdir -p ~/.aws
   nano ~/.aws/credentials
   ```

3. **Paste this content**:
   ```
   [default]
   aws_access_key_id = YOUR_ACCESS_KEY
   aws_secret_access_key = YOUR_SECRET_KEY
   region = us-east-1
   ```

4. **Save** (Ctrl+O, Ctrl+X)

5. **Set permissions**:
   ```bash
   chmod 600 ~/.aws/credentials
   ```

### Option B: Using Environment Variables

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

### Test Credentials

```bash
python3 -c "import boto3; client = boto3.client('bedrock-runtime', region_name='us-east-1'); print('✓ AWS credentials working')"
```

## Step 7: Run Streamlit App

### Option A: Direct (Temporary)

```bash
# Activate venv if not already
source venv/bin/activate

# Run app
streamlit run app.py --server.port 80 --server.address 0.0.0.0
```

Access at: `http://54.123.45.67:8501`

### Option B: Using Systemd (Permanent)

Create service file:

```bash
sudo nano /etc/systemd/system/airline-rag.service
```

Paste this:

```ini
[Unit]
Description=Airline RAG Chatbot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/RAG-Airline-using-Bedrock-Titan-Novapro-FAISS
Environment="PATH=/home/ubuntu/RAG-Airline-using-Bedrock-Titan-Novapro-FAISS/venv/bin"
ExecStart=/home/ubuntu/RAG-Airline-using-Bedrock-Titan-Novapro-FAISS/venv/bin/streamlit run app.py --server.port 80 --server.address 0.0.0.0 --logger.level=info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable airline-rag
sudo systemctl start airline-rag

# Check status
sudo systemctl status airline-rag

# View logs
sudo journalctl -u airline-rag -f
```

### Option C: Using PM2 (Recommended for Production)

```bash
# Install PM2 globally
sudo npm install -g pm2
# Or use Python equivalents through pip

# Create app start script
cat > start.sh << 'EOF'
#!/bin/bash
cd /home/ubuntu/RAG-Airline-using-Bedrock-Titan-Novapro-FAISS
source venv/bin/activate
streamlit run app.py --server.port 80 --server.address 0.0.0.0
EOF

chmod +x start.sh

# Run with PM2
pm2 start start.sh --name airline-rag
pm2 save
pm2 startup
```

## Step 8: Set Up Reverse Proxy with Nginx (Optional but Recommended)

```bash
# Install Nginx
sudo apt install -y nginx

# Create Nginx config
sudo nano /etc/nginx/sites-available/airline-rag
```

Paste:

```nginx
server {
    listen 80;
    server_name 54.123.45.67;  # Replace with your IP or domain

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support for Streamlit
    location /_stcore/stream {
        proxy_pass http://localhost:8501/_stcore/stream;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_buffering off;
    }
}
```

Enable:

```bash
sudo ln -s /etc/nginx/sites-available/airline-rag /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Now access at: `http://54.123.45.67` (port 80)

## Step 9: Set Up HTTPS with Let's Encrypt (Optional)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate (need domain name)
sudo certbot certonly --nginx -d yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

Update Nginx config:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8501;
        # ... rest of config
    }
}
```

## Step 10: Monitor Application

```bash
# Check if app is running
curl http://localhost:8501

# Monitor system resources
top

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# View Streamlit logs
sudo journalctl -u airline-rag -f
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8501
sudo lsof -i :8501
sudo kill -9 <PID>
```

### Streamlit Not Accessible

```bash
# Check if running
ps aux | grep streamlit

# Check firewall
sudo ufw status

# Allow ports
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8501
```

### AWS Credentials Not Working

```bash
# Test credentials
aws s3 ls

# Check environment variables
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY

# View IAM user permissions
# Go to AWS Console → IAM → Users → Check policies
```

### Out of Memory

```bash
# Check memory usage
free -h

# Upgrade instance type (requires stop/start)
# EC2 Console → Instance → Instance Settings → Change Instance Type
```

## Cost Optimization

**Free Tier (12 months)**:
- t2.micro: 750 hours/month
- 30GB EBS storage
- 100GB data transfer out

**Estimated Monthly Cost**:
- EC2 (t2.small beyond free tier): ~$10
- EBS storage: ~$1
- Data transfer: ~$5-10 (depends on usage)
- **Total**: ~$15-20/month

**Reduce Costs**:
1. Use t2.micro (free tier)
2. Stop instance when not needed
3. Use RDS free tier backup
4. Set up auto-shutdown script

## Update Application

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-ip

# Navigate to app
cd RAG-Airline-using-Bedrock-Titan-Novapro-FAISS

# Pull latest code
git pull

# Restart service
sudo systemctl restart airline-rag
```

## Backup and Recovery

```bash
# Create AMI (image) of instance
# EC2 Console → Instance → Image & Templates → Create Image
# Useful for quick recovery or scaling

# Backup data
tar -czf backup.tar.gz ~/RAG-Airline-using-Bedrock-Titan-Novapro-FAISS
```

## Summary

Your Airline RAG Chatbot is now running on AWS EC2!

**Access URL**: `http://your-public-ip:8501`

**Key Commands**:
- Status: `sudo systemctl status airline-rag`
- Restart: `sudo systemctl restart airline-rag`
- Logs: `sudo journalctl -u airline-rag -f`
- Stop: `sudo systemctl stop airline-rag`

## Next Steps

1. Custom domain + HTTPS
2. Database for conversation history
3. User authentication
4. Analytics dashboard
5. Scheduled updates
