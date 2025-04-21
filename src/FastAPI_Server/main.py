from fastapi import FastAPI, HTTPException
import json
import faiss
import time
from pydantic import BaseModel
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.llms import Ollama
import numpy as np
import datetime

# Constants
USER_MEMORY_INDEX = "user_memory.index"
USER_METADATA_FILE = "user_metadata.json"

class QueryRequest(BaseModel):
    prompt: str
    user_id: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]

# Initialize components
def intialize_components():
    try:
        faiss_index = faiss.read_index("knowledge_base_python.index")
        with open("metadata.json", "r", encoding="utf-8") as f:
            metadata = json.load(f)

        documents = [Document(
            page_content=f"Topic:{item['topic']}\nExplanation:{item['explanation']}\nExample:{item['example']['code']}",
            metadata={"source": item.get("source", "")}
        ) for item in metadata]

        embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        index_to_docstore_id = {i: str(i) for i in range(len(documents))}
        docstore = InMemoryDocstore(dict(zip(index_to_docstore_id.values(), documents)))

        retriever = FAISS(
            embedding_function=embedding_function,
            index=faiss_index,
            docstore=docstore,
            index_to_docstore_id=index_to_docstore_id,
        )

        return retriever.as_retriever(search_type='similarity', search_kwargs={"k": 3}), documents, embedding_function, faiss_index, retriever

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize components: {str(e)}")

retriever, document_list, embedding_function, faiss_index, vectorstore = intialize_components()
ollama_llm = Ollama(model='deepseek-r1:1.5b')

# Initialize user memory index
user_memory_index = faiss.IndexFlatL2(384)
user_query_metadata = []

# Store user query
def store_user_query(query: str, user_id: str):
    try:
        vector = embedding_function.embed_query(query)
        user_memory_index.add(np.array([vector], dtype=np.float32))
        user_query_metadata.append({
            "user_id": user_id,
            "query": query,
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
        faiss.write_index(user_memory_index, USER_MEMORY_INDEX)
        with open(USER_METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(user_query_metadata, f, indent=2)
    except Exception as e:
        print(f"Error storing user query: {e}")

# Get similar user queries
def get_similar_user_queries(prompt: str, k: int = 3):
    if user_memory_index.ntotal == 0:
        return []

    vector = embedding_function.embed_query(prompt)
    distances, indices = user_memory_index.search(np.array([vector], dtype=np.float32), k)

    results = []
    for i in indices[0]:
        if i < len(user_query_metadata):
            results.append(user_query_metadata[i]["query"])
    return results

# FastAPI app
app = FastAPI()

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        start_time = time.time()

        # Retrieve relevant documents from FAISS
        local_docs = retriever.get_relevant_documents(request.prompt)
        local_answer = "\n\n".join([doc.page_content for doc in local_docs]).strip()
        local_sources = [doc.metadata.get("source", "Unknown") for doc in local_docs]
        local_sources = [s for s in local_sources if s != "Unknown"]

        # Fetch past similar user queries
        similar_queries = get_similar_user_queries(request.prompt, k=3)

        # Combine the relevant documents and past queries to refine the prompt
        context = f"use the following context to answer the question:\n\n{local_answer}\n\nPast similar queries:\n"
        context += "\n".join(similar_queries) if similar_queries else "No past queries found."

        # Refine the prompt by adding the current query to the context
        prompt = f"{context}\n\nQuestion: {request.prompt}"

        # Invoke Ollama with the refined prompt
        try:
            response = ollama_llm.invoke(prompt)
        except Exception as e:
            print("Error invoking Ollama LLM:", e)
            raise HTTPException(status_code=500, detail="Error invoking LLM")

        return QueryResponse(
            answer=response,
            sources=local_sources
        )
    except Exception as e:
        print("🔥 error in /query:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

