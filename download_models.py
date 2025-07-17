from sentence_transformers import SentenceTransformer, CrossEncoder
import os

# Create models directory if it doesn't exist
os.makedirs('./models', exist_ok=True)

# Define model names from the document
embedding_model_name = 'sentence-transformers/all-MiniLM-L6-v2'
reranker_model_name = 'cross-encoder/ms-marco-MiniLM-L-6-v2'

# Download and save the embedding model
print(f"Downloading {embedding_model_name}...")
embedder = SentenceTransformer(embedding_model_name)
embedder.save('./models/all-MiniLM-L6-v2')
print("Embedding model saved.")

# Download and save the cross-encoder reranking model
print(f"Downloading {reranker_model_name}...")
reranker = CrossEncoder(reranker_model_name)
reranker.save('./models/cross-encoder-ms-marco-MiniLM-L6-v2')
print("Reranker model saved.")

print("All models downloaded and saved successfully!")