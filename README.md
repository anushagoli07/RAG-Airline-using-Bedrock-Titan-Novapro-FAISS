# Airline RAG Chatbot using Bedrock, Titan, Nova Pro & FAISS

A Retrieval-Augmented Generation (RAG) chatbot that answers questions about airline policies using AWS Bedrock, Amazon Titan embeddings, and FAISS vector database.

![Python](https://img.shields.io/badge/Python-3.13+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![AWS](https://img.shields.io/badge/AWS-Bedrock-orange)
![License](https://img.shields.io/badge/License-MIT-green)

## Features

✨ **RAG Architecture** - Retrieves relevant documents before generating responses  
🤖 **AWS Bedrock Integration** - Uses Amazon Nova Pro for LLM and Titan for embeddings  
🔍 **FAISS Vector Store** - Fast semantic search over PDF documents  
🎯 **Streamlit UI** - Simple, interactive web interface  
📄 **PDF Processing** - Automatically loads and processes airline documents  
⚡ **Production-Ready** - Error handling, token management, and safe text truncation  

## Architecture

```
User Question
     ↓
Vector Embedding (Titan Embed)
     ↓
FAISS Similarity Search
     ↓
Retrieve Top 3 Documents
     ↓
Create Prompt with Context
     ↓
Amazon Nova Pro LLM
     ↓
Chatbot Response
```

## Project Structure

```
airline-rag-chatbot/
├── main.py              # Core RAG logic and embedding class
├── app.py               # Streamlit chatbot interface
├── test_basic.py        # AWS connectivity test
├── 01_setup_s3.py       # S3 setup (optional)
├── docs/                # PDF documents for RAG
│   ├── contract-of-carriage.pdf
│   ├── Baggage_Southwest_Airlines.pdf
│   └── ... (9 airline documents total)
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── .gitignore          # Git ignore rules
```

## Requirements

- Python 3.10+
- AWS Account with Bedrock access
- AWS credentials configured locally
- 2GB+ free disk space

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/anushagoli07/RAG-Airline-using-Bedrock-Titan-Novapro-FAISS.git
cd airline-rag-chatbot
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure AWS Credentials

Set up AWS credentials (choose one method):

**Option A: AWS CLI**
```bash
aws configure
# Enter your Access Key ID and Secret Access Key
```

**Option B: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

**Option C: ~/.aws/credentials file**
```
[default]
aws_access_key_id=your_access_key
aws_secret_access_key=your_secret_key
region=us-east-1
```

### 5. Ensure Bedrock Access

Make sure your AWS account has access to Bedrock models:
- `amazon.titan-embed-text-v2:0` (embeddings)
- `us.amazon.nova-pro-v1:0` (LLM)

Enable them in the AWS Bedrock console if needed.

## Usage

### Local Development

```bash
# Start the Streamlit app
streamlit run app.py
```

The app will open at `http://localhost:8501`

### Using the Chatbot

1. Open the Streamlit app in your browser
2. Enter your question about airline policies
3. Click "Ask" button
4. Get an AI-generated response based on your documents

**Example Queries:**
- "What are the COVID-19 policies?"
- "How much baggage can I take?"
- "What are the refund policies?"
- "What are passenger rights?"

### Testing AWS Connection

```bash
python test_basic.py
```

This will verify:
- AWS credentials are valid
- Bedrock API is accessible
- Models are available

## How It Works

### 1. **Document Processing** (`initialize_vectorstore()`)
   - Loads all PDFs from `docs/` folder
   - Splits documents into 1000-character chunks with 200-char overlap
   - Generates embeddings using Amazon Titan Embed Text v2

### 2. **Vector Store** (FAISS)
   - Indexes embeddings in FAISS for fast similarity search
   - Stores full text alongside embeddings

### 3. **Query Processing** (`get_response()`)
   - Embeds user question
   - Searches for 3 most similar documents
   - Creates context from retrieved documents

### 4. **Response Generation**
   - Combines context + question into prompt
   - Sends to Amazon Nova Pro LLM
   - Returns natural language answer

## Configuration

### Adjustable Parameters in `main.py`

```python
# Embedding truncation (tokens)
self.max_tokens = 8000

# Document chunk size (characters)
chunk_size=1000
chunk_overlap=200

# Search parameters
k=3  # Number of documents to retrieve

# LLM parameters
maxTokens=300
temperature=0
topP=0.1
topK=20
```

## API Models Used

### Embeddings
- **Model**: `amazon.titan-embed-text-v2:0`
- **Input**: Text up to ~8000 tokens
- **Output**: 1024-dimensional embeddings

### LLM
- **Model**: `us.amazon.nova-pro-v1:0`
- **Context**: ~200K tokens
- **Output**: Up to 300 tokens per response

## Deployment

### Streamlit Cloud (Recommended)

1. Push code to GitHub
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
3. Click "New app"
4. Select your GitHub repo
5. Add AWS credentials as secrets:
   ```toml
   # .streamlit/secrets.toml
   [AWS]
   access_key = "your_key"
   secret_key = "your_secret"
   region = "us-east-1"
   ```

### AWS EC2

```bash
# Launch EC2 instance
# SSH into instance
sudo apt-get update
sudo apt-get install python3-pip
git clone <repo>
cd airline-rag-chatbot
pip install -r requirements.txt
streamlit run app.py --server.port 80
```

### Docker

```bash
docker build -t airline-chatbot .
docker run -p 8501:8501 airline-chatbot
```

## Troubleshooting

### AWS Credential Errors
```
Error: NoCredentialsError: Unable to locate credentials
```
**Solution**: Configure AWS credentials (see Installation step 4)

### Bedrock Access Denied
```
Error: User: ... is not authorized to perform: bedrock:InvokeModel
```
**Solution**: Enable models in AWS Bedrock console

### Embedding Errors
```
Error: ValidationException - Malformed input request
```
**Solution**: Update code to use correct input format (uses `inputText` not `input`)

### SQLITE3 DLL Error
```
Error: DLL load failed while importing _sqlite3
```
**Solution**: Code uses FAISS instead of Chroma to avoid this issue

## Cost Estimates (AWS Bedrock)

**Embeddings**: ~$0.02 per 1M tokens
- Processing ~2MB of PDFs ≈ $0.01

**LLM Inference**: ~$0.60 per 1M input tokens + $1.80 per 1M output tokens
- 100 queries × 300 tokens output ≈ $0.05

**Total Monthly** (10K queries): ~$3-5

## Performance

- **Embedding Time**: ~2-5 seconds for all documents (one-time)
- **Query Latency**: ~2-3 seconds per question
- **Vector Store Size**: ~8MB for ~40K text chunks
- **Concurrent Users**: Scales with Streamlit Cloud (100+ recommended)

## Environment Variables

```bash
AWS_ACCESS_KEY_ID          # AWS access key
AWS_SECRET_ACCESS_KEY      # AWS secret key
AWS_DEFAULT_REGION         # AWS region (default: us-east-1)
```

## Dependencies

- `langchain` - LLM framework
- `langchain-community` - Community integrations
- `boto3` - AWS SDK
- `faiss-cpu` - Vector database
- `streamlit` - Web UI
- `tiktoken` - Token counting
- `pypdf` - PDF loading

## License

MIT License - see LICENSE file

## Author

[Anusha Jonnadula](https://github.com/anushagoli07)

## Support

For issues or questions:
1. Check [GitHub Issues](https://github.com/anushagoli07/RAG-Airline-using-Bedrock-Titan-Novapro-FAISS/issues)
2. Review AWS Bedrock documentation
3. Check Streamlit documentation

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Acknowledgments

- AWS Bedrock for models
- LangChain for RAG framework
- FAISS for vector search
- Streamlit for UI framework
