from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain_community.docstore.in_memory import InMemoryDocstore
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Define request model
class QueryRequest(BaseModel):
    prompt: str

# Define response model
class QueryResponse(BaseModel):
    answer: str
    sources: List[str]

# Initialize components
def initialize_components():
    # Load FAISS Index
    faiss_index = faiss.read_index("knowledge_base_python.index")
    with open("metadata.json", "r", encoding="utf-8") as f:
        metadata = json.load(f)

    # Prepare Documents for LangChain
    documents = [
        Document(
            page_content=f"Topic: {item['topic']}\nExplanation: {item['explanation']}\nExample: {item['example']['code']}",
            metadata={"source": item.get("source", "")}
        )
        for item in metadata
    ]

    # Embedding function
    embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Prepare FAISS metadata
    index_to_docstore_id = {i: str(i) for i in range(len(documents))}
    docstore = InMemoryDocstore(dict(zip(index_to_docstore_id.values(), documents)))

    # LangChain FAISS Vector Store
    vectorstore = FAISS(
        embedding_function=embedding_function,
        index=faiss_index,
        docstore=docstore,
        index_to_docstore_id=index_to_docstore_id,
    )

    # Load Ollama model
    llm = OllamaLLM(model="mistral")

    # Retrieval-based QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(search_type="similarity", k=3),
        return_source_documents=True
    )

    return qa_chain

# Initialize components at startup
qa_chain = initialize_components()

@app.post("/rag", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    print("Received request:", request)
    print("Request prompt:", request.prompt)
    try:
        result = qa_chain({"query": request.prompt})
        return QueryResponse(
            answer=result["result"],
            sources=[doc.metadata.get("source", "Unknown") for doc in result["source_documents"]]
        )
    except Exception as e:
        print("Error processing query:", str(e))
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)