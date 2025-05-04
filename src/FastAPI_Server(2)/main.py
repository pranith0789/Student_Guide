from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import faiss
from pydantic import BaseModel
from typing import List
import numpy as np
import datetime
import httpx
import wikipedia
import re
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.llms import Ollama

# Constants
USER_MEMORY_INDEX = "Query_DB/user_memory.index"
USER_METADATA_FILE = "Query_DB/user_metadata.json"
RESPONSE_MEMORY_INDEX = "Query_Response_DB/Response_memory.index"
RESPONSE_METADATA_FILE = "Query_Response_DB/Response_metadata.json"
SIMILARITY_THRESHOLD = 0.05  # Stricter threshold for exact matches

class QueryRequest(BaseModel):
    prompt: str
    # user_id: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]

# Initialize components
def initialize_components():
    try:
        faiss_index = faiss.read_index("FAISS_DB/knowledge_base_python.index")
        with open("FAISS_DB/metadata.json", "r", encoding="utf-8") as f:
            metadata = json.load(f)

        documents = [
            Document(
                page_content=f"Topic:{item['topic']}\nExplanation:{item['explanation']}\nExample:{item['example']['code']}",
                metadata={"source": item.get("source", "")}
            ) for item in metadata
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

        return retriever.as_retriever(search_type='similarity', search_kwargs={"k": 3}), documents, embedding_function, faiss_index, retriever

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize components: {str(e)}")

retriever, document_list, embedding_function, faiss_index, vectorstore = initialize_components()
ollama_llm = Ollama(model='llama3.2')
small_llm = Ollama(model='gemma3:1b')

# Initialize user memory index
user_memory_index = faiss.IndexFlatL2(384)
user_query_metadata = []

# Store user query
def store_user_query(query: str):
    try:
        vector = embedding_function.embed_query(query)
        user_memory_index.add(np.array([vector], dtype=np.float32))
        user_query_metadata.append({
            # "user_id": user_id,
            "query": query,
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
        faiss.write_index(user_memory_index, USER_MEMORY_INDEX)
        with open(USER_METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(user_query_metadata, f, indent=2)
    except Exception as e:
        print(f"Error storing user query: {e}")

response_memory_index = faiss.IndexFlatL2(384)
query_response_metadata = []

# Store query with response
def store_query_response(query: str, response: str):
    try:
        vector = embedding_function.embed_query(query)
        response_memory_index.add(np.array([vector], dtype=np.float32))
        query_response_metadata.append({
            "query": query,
            "response": response,
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
        faiss.write_index(response_memory_index, RESPONSE_MEMORY_INDEX)
        with open(RESPONSE_METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(query_response_metadata, f, indent=2)
    except Exception as e:
        print(f"Error storing query response: {e}")

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

# Get past responses with stricter matching
def get_stored_response(prompt: str):
    try:
        if response_memory_index.ntotal == 0:
            return None
        vector = embedding_function.embed_query(prompt)
        distances, indices = response_memory_index.search(np.array([vector], dtype=np.float32), k=1)
        if distances[0][0] > SIMILARITY_THRESHOLD:
            print(f"No close match for prompt: '{prompt}', distance: {distances[0][0]}")
            return None
        for i in indices[0]:
            if i < len(query_response_metadata):
                stored_query = query_response_metadata[i]["query"]
                # Exact text match for added precision
                if stored_query.strip().lower() == prompt.strip().lower():
                    print(f"Found exact cached response for prompt: '{prompt}', distance: {distances[0][0]}")
                    return query_response_metadata[i]["response"]
                print(f"Close but not exact match for prompt: '{prompt}', stored: '{stored_query}', distance: {distances[0][0]}")
                return None
        return None
    except Exception as e:
        print(f"Error retrieving response: {e}")
        return None

# Classify sources
def classify_sources(query: str, classifier_llm) -> List[str]:
    prompt = f"""
        You are a source classifier. For the query:"{query}", return only a comma-seperated list of relevant sources from these options:
        - FAISS DB - Contains basic definations and code exampled
        - Wikipedia - Contains detailed explanation about the topic
        - StackOverFlow - Used for debugging and trouble shotting the problems
        - YouTube - Used for video explanation
        
        Return format example: Wikipedida , YouTube
        Do not include any explanations or additional text. Return as list type seperated by commas.
    """
    try:
        response = classifier_llm.invoke(prompt)
        sources_list = [source.strip() for source in response.split(',')]
        return sources_list
    except Exception as e:
        print(f"Source classification error: {e}")
        return ["FAISS_DB"]

# StackOverflow response
async def stackoverflow_response(prompt: str, api_key: str):
    url = "https://api.stackexchange.com/2.3/search/advanced"
    params = {
        "order": "desc",
        "sort": "relevance",
        "q": prompt,
        "site": "stackoverflow",
        "key": api_key
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        if data["items"]:
            top_question = data["items"][0]
            return f"StackOverflow: {top_question['title']} ({top_question['link']})"
        return "No relevant results found on StackOverflow."
    except Exception as e:
        return f"Error fetching from StackOverflow: {e}"

# Wikipedia response
def wikipedia_response(prompt: str) -> str:
    try:
        summary = wikipedia.summary(prompt, sentences=3)
        page = wikipedia.page(prompt)
        return f"Wikipedia: {summary} (Read more: {page.url})"
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Wikipedia: Multiple topics found: {', '.join(e.options[:5])}"
    except wikipedia.exceptions.PageError:
        return "Wikipedia: Page not found."
    except Exception as e:
        return f"Error fetching from Wikipedia: {str(e)}"

# YouTube response
async def youtube_response(prompt: str, api_key: str):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": prompt,
        "type": "video",
        "maxResults": 1,
        "key": api_key
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        if "items" in data and data["items"]:
            video = data["items"][0]
            video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
            return f"YouTube: {video['snippet']['title']} ({video_url})"
        return "No relevant videos found on YouTube."
    except Exception as e:
        return f"Error fetching from YouTube: {e}"

# Clean response
def clean_response(text: str) -> str:
    return re.sub(r'<think>.*?</think>\n*', '', text, flags=re.DOTALL)

# FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        # Check for stored response
        # existing_response = get_stored_response(request.prompt)
        # if existing_response:
        #     return QueryResponse(answer=clean_response(existing_response), sources=["StoredResponse"])

        # Classify sources
        sources = classify_sources(request.prompt, classifier_llm=ollama_llm)
        print(f"Classified sources for prompt '{request.prompt}': {sources}")

        final_response = ""
        used_sources = []
        local_sources = []
        youtube_videos = []
        online_resources = []
        
        if "StackOverFlow" in sources and "StackOverFlow" not in used_sources:
            stack_response = await stackoverflow_response(request.prompt, api_key="rl_hzCWsuykMD5YuX4wfbw5YagZ5")
            refined_response = small_llm.invoke(f"Summarize and explain in plain text:\n{stack_response}")
            final_response += f"\n{refined_response}"
            used_sources.append("StackOverflow")

        if "Wikipedia" in sources and "Wikipedia" not in used_sources:
            wiki_response = wikipedia_response(request.prompt)
            refined_response = small_llm.invoke(f"Summarize and explain in plain text:\n{wiki_response}")
            final_response += f"\n{refined_response}"
            used_sources.append("Wikipedia")

        if "FAISS DB" in sources and "FAISS DB" not in used_sources:
            local_docs = retriever.get_relevant_documents(request.prompt)
            local_answer = "\n".join([doc.page_content for doc in local_docs]).strip()
            refined_response = small_llm.invoke(f"Summarize and explain in plain text:\n{local_answer}")
            final_response += f"\n{refined_response}"
            local_sources = [doc.metadata.get("source", "Unknown") for doc in local_docs if doc.metadata.get("source", "Unknown") != "Unknown"]
            used_sources.append("FAISS_DB")

        # Uncomment to enable YouTube
        if "YouTube" in sources and "YouTube" not in used_sources:
            youtuberesponse = await youtube_response(request.prompt, api_key="AIzaSyA8DC-VlDt0BTfC9jEonSStDg3yVNEokaU")
            refined_response = small_llm.invoke(f"Remove the text and give me only youtube video link{youtuberesponse}")
            youtube_videos.append(refined_response)
            used_sources.append("YouTube")

        # Get similar queries
        similar_queries = get_similar_user_queries(request.prompt, k=3)
        context = f"Combine responses into a single paragraph and answer the question:\n{final_response}\nPast similar queries:\n"
        context += "\n".join(similar_queries) if similar_queries else "No past queries found."

        prompt = f"{context}\nQuestion: {request.prompt}"
        final_answer = ollama_llm.invoke(prompt)

        # Clean the final answer
        cleaned_answer = clean_response(final_answer)
        
        suggestion_prompt = f"""
        You are an advanced AI_Tutor that helps user for future by recommending next steps through current user_query and previous_Query
        current_query:{request.prompt}
        previous_query:{similar_queries}
        return the list of suggested topics seperated by comma.
        """
        
        Topics = ollama_llm.invoke(suggestion_prompt)
        print(Topics)

        # Store query and response
        store_user_query(request.prompt)
        store_query_response(request.prompt, cleaned_answer)

        if not local_sources:
            online_resources = used_sources + youtube_videos
        else:
            online_resources = used_sources + local_sources +  youtube_videos
            
        return QueryResponse(answer=cleaned_answer, sources = online_resources)

    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))
