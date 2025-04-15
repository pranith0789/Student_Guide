from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import json
import time
import numpy as np
import faiss
import aiohttp
import asyncio
from sentence_transformers import SentenceTransformer
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain_community.docstore.in_memory import InMemoryDocstore
from fastapi.middleware.cors import CORSMiddleware
from functools import lru_cache
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv("credententials.env")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
STACKOVERFLOW_KEY = os.getenv("STACKOVERFLOW_KEY")  # Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    prompt: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]

def initialize_components():
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

    vectorstore = FAISS(
        embedding_function=embedding_function,
        index=faiss_index,
        docstore=docstore,
        index_to_docstore_id=index_to_docstore_id,
    )

    # Return just the retriever without LLM refinement
    return vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})

retriever = initialize_components()

def store_documents(documents: List[Document]):
    """Store new documents in the FAISS index."""
    try:
        # Get existing index and metadata
        faiss_index = faiss.read_index("knowledge_base_python.index")
        with open("metadata.json", "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        # Create embeddings for new documents
        embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        embeddings = embedding_function.embed_documents([doc.page_content for doc in documents])
        
        # Add to FAISS index
        faiss_index.add(np.array(embeddings).astype('float32'))
        
        # Update metadata
        new_metadata = [
            {
                "topic": doc.page_content.split("\n")[0].replace("Topic: ", ""),
                "explanation": doc.page_content.split("\n")[1].replace("Explanation: ", ""),
                "example": {"code": doc.page_content.split("\n")[2].replace("Example: ", "")},
                "source": doc.metadata.get("source", "Stack Overflow")
            }
            for doc in documents
        ]
        metadata.extend(new_metadata)
        
        # Save updated index and metadata
        faiss.write_index(faiss_index, "knowledge_base_python.index")
        with open("metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
            
        # Reinitialize components with updated index
        global retriever
        retriever = initialize_components()
        
        return True
    except Exception as e:
        print(f"Error storing documents: {str(e)}")
        return False

@lru_cache(maxsize=100)
def search_stackoverflow_sync(query: str) -> tuple[str, List[str]]:
    """Synchronous wrapper for Stack Overflow search (for caching)."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(search_stackoverflow(query))

async def search_stackoverflow(query: str) -> tuple[str, List[str]]:
    """Search Stack Overflow for answers."""
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://api.stackexchange.com/2.3/search/advanced"
            params = {
                "q": query,
                "site": "stackoverflow",
                "sort": "relevance",
                "order": "desc",
                "filter": "withbody",
                "pagesize": 3,
            }
            if STACKOVERFLOW_KEY:
                params["key"] = STACKOVERFLOW_KEY
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()

                answers = []
                sources = []
                documents_to_store = []
                
                for item in data.get("items", []):
                    if item.get("is_answered") and item.get("accepted_answer_id"):
                        title = item.get("title", "")
                        body = item.get("body", "")
                        link = item.get("link", "")
                        
                        # Create document for storage
                        doc = Document(
                            page_content=f"Topic: {title}\nExplanation: {body}\nExample: No code example available",
                            metadata={"source": link}
                        )
                        documents_to_store.append(doc)
                        
                        answers.append(body)
                        sources.append(link)
                
                # Store new documents in the database
                if documents_to_store:
                    store_documents(documents_to_store)
                
                answer_text = "\n\n".join([f"Stack Overflow Result {i+1}:\n{ans}" for i, ans in enumerate(answers)])
                return answer_text or "No relevant Stack Overflow answers found.", sources
    except Exception as e:
        print(f"Stack Overflow API error: {str(e)}")
        return "Failed to fetch Stack Overflow answers.", []

@lru_cache(maxsize=100)
def search_youtube_sync(query: str) -> tuple[str, List[str]]:
    """Synchronous wrapper for YouTube search (for caching)."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(search_youtube(query))

async def search_youtube(query: str) -> tuple[str, List[str]]:
    """Search YouTube for videos."""
    if not YOUTUBE_API_KEY:
        print("YouTube API key missing")
        return "YouTube API key not provided.", []
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": 3,
                "key": YOUTUBE_API_KEY,
                "order": "relevance",
            }
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    print(f"YouTube API error: HTTP {response.status}")
                    return f"YouTube API error: HTTP {response.status}", []
                data = await response.json()
                if "error" in data:
                    print(f"YouTube API error: {data['error']['message']}")
                    return f"YouTube API error: {data['error']['message']}", []
                videos = []
                sources = []
                for item in data.get("items", []):
                    title = item["snippet"]["title"]
                    description = item["snippet"]["description"][:200] + ("..." if len(item["snippet"]["description"]) > 200 else "")
                    video_id = item["id"]["videoId"]
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    videos.append(f"Title: {title}\nDescription: {description}")
                    sources.append(video_url)
                video_text = "\n\n".join([f"YouTube Video {i+1}:\n{vid}" for i, vid in enumerate(videos)])
                return video_text or "No relevant YouTube videos found.", sources
    except Exception as e:
        print(f"YouTube API error: {str(e)}")
        return "Failed to fetch YouTube videos.", []

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    print("Received request:", request)
    print("Request prompt:", request.prompt)
    try:
        start_time = time.time()

        # Run local DB and YouTube searches in parallel
        local_task = asyncio.create_task(asyncio.to_thread(retriever.get_relevant_documents, request.prompt))
        youtube_task = asyncio.create_task(search_youtube(request.prompt))

        # Await results
        local_docs = await local_task
        youtube_answer, youtube_sources = await youtube_task

        # Format local results without LLM refinement
        local_answer = "\n\n".join([doc.page_content for doc in local_docs])
        local_sources = [doc.metadata.get("source", "Unknown") for doc in local_docs]
        local_sources = [s for s in local_sources if s != "Unknown"]

        # Check if local search is relevant
        if local_answer and local_answer.lower() not in ["", "i don't know", "no relevant information found"]:
            print(f"Local search took {(time.time() - start_time) * 1000:.2f} ms")
            combined_answer = f"{local_answer}\n\nYouTube Videos:\n{youtube_answer}".strip()
            combined_sources = list(set(local_sources + youtube_sources))
            print(f"Total query took {(time.time() - start_time) * 1000:.2f} ms")
            return QueryResponse(
                answer=combined_answer,
                sources=combined_sources
            )

        # Fallback to Stack Overflow + YouTube
        print("Local search failed, querying Stack Overflow...")
        stack_answer, stack_sources = await search_stackoverflow(request.prompt)
        combined_answer = f"Local search found no relevant results.\n\nStack Overflow:\n{stack_answer}\n\nYouTube Videos:\n{youtube_answer}".strip()
        combined_sources = list(set(stack_sources + youtube_sources))

        print(f"Total query took {(time.time() - start_time) * 1000:.2f} ms")
        return QueryResponse(
            answer=combined_answer,
            sources=combined_sources
        )
    except Exception as e:
        print("Error processing query:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)