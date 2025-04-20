import faiss
import json
import os
import numpy as np
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from sklearn.preprocessing import normalize

# ✅ Change this path if your metadata.json is in a different location
metadata_path = "src\FastAPI_Server\metadata.json"

if not os.path.exists(metadata_path):
    raise FileNotFoundError(f"❌ File not found: {metadata_path}. Please check the path.")

# Load metadata
with open(metadata_path, "r", encoding="utf-8") as f:
    metadata = json.load(f)

# Prepare documents
documents = [
    Document(
        page_content=f"Topic: {item['topic']}\nExplanation: {item['explanation']}\nExample: {item['example']['code']}",
        metadata={"source": item.get("source", "")}
    )
    for item in metadata
]

# Initialize embedding model
embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Get and normalize embeddings
embeddings = [embedding_function.embed_query(doc.page_content) for doc in documents]
embedding_matrix = np.array(embeddings, dtype="float32")
embedding_matrix = normalize(embedding_matrix, axis=1)  # Normalize for cosine similarity

# Create FAISS index using cosine similarity (IndexFlatIP)
index = faiss.IndexFlatIP(embedding_matrix.shape[1])
index.add(embedding_matrix)

# Save the index
faiss.write_index(index, "knowledge_base_python.index")

print("✅ FAISS index built and saved successfully using cosine similarity.")
