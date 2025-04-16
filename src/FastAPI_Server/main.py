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
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain.docstore.in_memory import InMemoryDocstore
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

        embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
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
ollama_llm = Ollama(model="llama3.2")

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        start_time = time.time()

        # Embed query and normalize
        query_vector = embedding_function.embed_query(request.prompt)
        query_vector_np = np.array(query_vector, dtype="float32").reshape(1, -1)
        query_vector_np = normalize(query_vector_np, axis=1)

        # Search in FAISS
        D, I = faiss_index.search(query_vector_np, k=3)
        max_score = 1 - float(D[0][0])  # cosine similarity
        print(f"[Similarity Score] {max_score:.4f}")
        CONFIDENCE_THRESHOLD = 0.5

        if max_score >= CONFIDENCE_THRESHOLD:
            local_docs = retriever.get_relevant_documents(request.prompt)
            local_answer = "\n\n".join([doc.page_content for doc in local_docs])
            local_sources = [doc.metadata.get("source", "Unknown") for doc in local_docs]
            local_sources = [s for s in local_sources if s != "Unknown"]

            youtube_answer, youtube_sources = await search_youtube(request.prompt)

            combined_answer = f"{local_answer}\n\nYouTube Videos:\n{youtube_answer}".strip()
            combined_sources = list(set(local_sources + youtube_sources))

            return QueryResponse(
                answer=combined_answer,
                sources=combined_sources
            )

        # Fallback to Stack Overflow
        print("Low confidence in local results. Using Stack Overflow...")
        stack_answer, stack_sources = await search_stackoverflow(request.prompt)
        print("\n[StackOverflow Original Answer]:\n", stack_answer)

        # Refine with Ollama
        refined_answer = ollama_llm.invoke(f"Improve this answer: {stack_answer}")
        print("\n[Refined Answer]:\n", refined_answer)

        # Add to vector DB and persist to disk
        refined_vector = np.array([embedding_function.embed_query(refined_answer)], dtype=np.float32)
        faiss_index.add(refined_vector)
        doc_id = str(len(vectorstore.docstore._dict))
        vectorstore.docstore._dict[doc_id] = Document(
            page_content=refined_answer,
            metadata={"source": "StackOverflow"}
        )
        vectorstore.index_to_docstore_id[len(vectorstore.index_to_docstore_id)] = doc_id
        faiss.write_index(faiss_index, "knowledge_base_python.index")

        # YouTube fallback too
        youtube_answer, youtube_sources = await search_youtube(request.prompt)

        combined_answer = (
            f"Local confidence too low.\n\n"
            f"Stack Overflow (original):\n{stack_answer}\n\n"
            f"Stack Overflow (refined):\n{refined_answer}\n\n"
            f"YouTube Videos:\n{youtube_answer}"
        )
        combined_sources = list(set(stack_sources + youtube_sources))

        return QueryResponse(answer=combined_answer, sources=combined_sources)

    except Exception as e:
        print("Error processing query:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
