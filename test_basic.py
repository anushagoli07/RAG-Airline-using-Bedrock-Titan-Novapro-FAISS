#!/usr/bin/env python
"""
Test script to verify basic functionality without chromadb dependency.
"""
import boto3
import json

try:
    print("Testing AWS Bedrock connection...")
    client = boto3.client("bedrock-runtime", region_name="us-east-1")
    MODEL_ID = "us.amazon.nova-pro-v1:0"
    
    # Test with a simple prompt
    message_list = [
        {"role": "user", "content": [{"text": "Hello, who are you?"}]}
    ]
    
    inference_params = {"maxTokens": 100, "topP": 0.9, "topK": 20, "temperature": 0.7}
    
    request_body = {
        "schemaVersion": "messages-v1",
        "messages": message_list,
        "inferenceConfig": inference_params,
        "system": [{"text": "You are a helpful assistant."}]
    }
    
    print("Invoking Bedrock model...")
    response = client.invoke_model(modelId=MODEL_ID, body=json.dumps(request_body))
    response_body = json.loads(response['body'].read())
    
    print("✓ AWS Bedrock connection successful!")
    print(f"Response: {response_body['output']['message']['content'][0]['text']}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
