from langchain_community.document_loaders import PyPDFDirectoryLoader
import boto3
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.embeddings import Embeddings
import tiktoken
from langchain_community.vectorstores import FAISS


class AmazonTitanEmbedding(Embeddings):
    def __init__(self, model_id="amazon.titan-embed-text-v2:0", region_name="us-east-1"):
        self.model_id = model_id
        self.client = boto3.client("bedrock-runtime", region_name=region_name)  
        self.max_tokens = 8000
        self.tokenizer=tiktoken.get_encoding("cl100k_base")

    def _safe_truncate(self, text):
        tokens = self.tokenizer.encode(text)
        if len(tokens) > self.max_tokens:
            tokens = tokens[:self.max_tokens]
        return self.tokenizer.decode(tokens)
    
    def embed_query(self, text):
        truncated_text = self._safe_truncate(text)
        request_body = {
            "inputText": truncated_text
        }
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(request_body)
        )
        response_body = json.loads(response['body'].read())
        return response_body['embedding']
    
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        embeddings = []
        for text in texts:
            try:
                safe_text = self._safe_truncate(text)
                embedding=self.embed_query(safe_text)
                embeddings.append(embedding)
            except Exception as e:
                print(f"Error embedding text: {e}")
        return embeddings


def initialize_vectorstore():
    """Initialize vector store with documents from the docs folder."""
    embedding_function = AmazonTitanEmbedding()
    
    loader = PyPDFDirectoryLoader("docs/")
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)
    
    # Use FAISS instead of Chroma to avoid sqlite3 issues
    vectorstore = FAISS.from_documents(docs, embedding_function)
    
    return vectorstore


client = boto3.client("bedrock-runtime", region_name="us-east-1")
MODEL_ID = "us.amazon.nova-pro-v1:0"

def get_response(question, vectorstore=None):
    """Get AI response based on the question and relevant documents from vectorstore."""
    if vectorstore is None:
        raise ValueError("Vectorstore not initialized. Call initialize_vectorstore() first.")
    
    docs_from_vectorstore = vectorstore.similarity_search(question, k=3)
    context = "\n\n".join([doc.page_content for doc in docs_from_vectorstore])
    
    prompt = f"""
You are a helpful assistant. Use the following context to answer the user's question.

Context: {context}

User's question: {question}
    """
    
    message_list = [
        {"role": "user", "content": [{"text": prompt}]}
    ]
    
    inference_params = {"maxTokens": 300, "topP": 0.1, "topK": 20, "temperature": 0}
    
    request_body = {
        "schemaVersion": "messages-v1",
        "messages": message_list,
        "inferenceConfig": inference_params,
        "system": [{"text": "You are a helpful assistant."}]
    }
    
    response = client.invoke_model(modelId=MODEL_ID, body=json.dumps(request_body))
    response_body = json.loads(response['body'].read())
    return response_body


if __name__ == "__main__":
    # Only run this code when the script is executed directly, not when imported
    vectorstore = initialize_vectorstore()
    result = get_response("What are the COVID-19 policies of airlines?")
    print(result['output']['message']['content'][0]['text'])

            