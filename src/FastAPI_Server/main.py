import os
import json
import faiss
import numpy as np
import asyncio
import uvicorn
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.llms import Ollama
from utils.youtube import search_youtube
from utils.stackoverflow import search_stackoverflow
from sklearn.preprocessing import normalize

class QueryRequest(BaseModel):
    prompt: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]

def initialize_components():
    try:
        faiss_index = faiss.read_index("knowledge_base_python.index")
        with open("metadata.json", "r", encoding="utf-8") as f:
            metadata = json.load(f)

        documents = [
            Document(
                page_content=f"Topic: {item['topic']}\nExplanation: {item['explanation']}\nExample: {item['example']['code']}",
                metadata={"source": item.get("source", "")}
            )
            for item in metadata
        ]

        embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        index_to_docstore_id = {i: str(i) for i in range(len(documents))}
        docstore = InMemoryDocstore(dict(zip(index_to_docstore_id.values(), documents)))

        retriever = FAISS(
            embedding_function=embedding_function,
            index=faiss_index,
            docstore=docstore,
            index_to_docstore_id=index_to_docstore_id,
        )

        return retriever.as_retriever(search_type="similarity", search_kwargs={"k": 3}), documents, embedding_function, faiss_index, retriever

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize components: {str(e)}")

app = FastAPI()

retriever, document_list, embedding_function, faiss_index, vectorstore = initialize_components()
ollama_llm = Ollama(model="deepseek-r1:1.5b")

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        start_time = time.time()

        # Step 1: Retrieve local documents
        local_docs = retriever.get_relevant_documents(request.prompt)
        local_answer = "\n\n".join([doc.page_content for doc in local_docs]).strip()
        local_sources = [doc.metadata.get("source", "Unknown") for doc in local_docs]
        local_sources = [s for s in local_sources if s != "Unknown"]

        # Step 2: Get YouTube resources
        youtube_answer, youtube_sources = await search_youtube(request.prompt)
        youtube_answer = youtube_answer.strip()
        youtube_sources = youtube_sources or []

        # Step 3: If no useful local or YouTube data, fetch from Stack Overflow
        if not local_answer and not youtube_answer:
            print("🔁 Falling back to Stack Overflow...")
            stackoverflow_answer, stackoverflow_sources = await search_stackoverflow(request.prompt)
            final_answer = f"Stack Overflow Answer:\n{stackoverflow_answer}"
            final_sources = stackoverflow_sources
        else:
            # Combine what we have from local + YouTube
            combined_sections = []
            if local_answer:
                combined_sections.append(local_answer)
            if youtube_answer:
                combined_sections.append(f"YouTube Videos:\n{youtube_answer}")

            final_answer = "\n\n".join(combined_sections).strip()
            final_sources = list(set(local_sources + youtube_sources))

        return QueryResponse(
            answer=final_answer,
            sources=final_sources
        )

    except Exception as e:
        print("🔥 Error in /query:", str(e))
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
