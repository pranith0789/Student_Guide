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
import requests
import wikipedia
import httpx

# Constants
USER_MEMORY_INDEX = "Query_DB/user_memory.index"
USER_METADATA_FILE = "Query_DB/user_metadata.json"

Response_Memory_index = "Query_Response_DB/Response_memory.index"
Response_Metadata_file = "Query_Response_DB/Response_metadata.json"

class QueryRequest(BaseModel):
    prompt: str
    user_id: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]

# Initialize components
def intialize_components():
    try:
        faiss_index = faiss.read_index("FAISS_DB/knowledge_base_python.index")
        with open("FAISS_DB/metadata.json", "r", encoding="utf-8") as f:
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
small_llm = Ollama(model='gemma3:1b')
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

response_memory_index = faiss.IndexFlatL2(384)
query_response_metadata = []

#Stores query with response for future use.
def store_query_response(query:str,Response:str):
    try:
        vector = embedding_function.embed_query(query)
        response_vector = embedding_function.embed_query(Response)
        response_memory_index.add(np.array([vector], dtype=np.float32))
        query_response_metadata.append({
            "query":vector.tolist(),
            "Response":response_vector.tolist(),
            "timestamp":datetime.datetime.utcnow().isoformat()
        })
        faiss.write_index(response_memory_index,Response_Memory_index)
        with open(Response_Metadata_file, "w", encoding="Utf-8") as f:
            json.dump(query_response_metadata,f,indent=2)
        
    except Exception as e:
        print(f"Error stroing query Response:{e}")


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

#Get past responses if same query is asked twicel
def get_stored_response(prompt: str):
    try:
        if response_memory_index.ntotal==0:
            return[]
        vector = embedding_function.embed_query(prompt)
        distances, indices = response_memory_index.search(np.array([vector], dtype=np.float32), k=1)
        results=[]
        for i in indices[0]:
            if i < len(query_response_metadata):
                results.append(query_response_metadata[i])
        return results
    except Exception as e:
        print(f"Error while retrieving response : {e}")
        return[]

def classify_sources(query:str,classifier_llm) -> dict:
    prompt = f"""
        you are a source classifier for an AI tutor.
        Available sources:
        - FAISS_DB: Contains structured tutorials and examples from curated content.
        - StackOverflow: Useful for debugging or coding help.
        - Wikipedia: Good for definitions and theory.
        - YouTube: Great for visual explanations or walkthroughs.

        classify the best source for this query. Return a list with sources.
        Query:"{query}"
    """

    try:
        response = classifier_llm.invoke(prompt)
        return response
    except Exception as e:
        print(f"source classification error: {e}")
        return {"Sources":["FaissDB"]}

async def StackOverFlow_response(prompt: str, api_key: str):
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
            return f"**Top StackOverflow Result:**\n{top_question['title']}\n{top_question['link']}"
        return "No relevant results found on Stack Overflow."
    except Exception as e:
        return f"Error fetching info from StackOverflow: {e}"


def Wikipedia_Response(prompt:str) -> str:
    try:
        summary = wikipedia.summary(prompt, sentences=3)
        page = wikipedia.page(prompt)
        return f"**Wikipedia Summary:**\n{summary}\n\n[Read More]({page.url})"
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Your query matched multiple topics: {', '.join(e.options[:5])}"
    except wikipedia.exceptions.PageError:
        return "Wikipedia page not found."
    except Exception as e:
        return f"Error fetching from Wikipedia: {str(e)}"

async def YouTube_Response(prompt: str, api_key: str):
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
            return f"**Top YouTube Result:**\n{video['snippet']['title']}\n{video_url}"
        return "No relevant videos found on YouTube."
    except Exception as e:
        return f"Error fetching from YouTube: {e}"

# FastAPI app
app = FastAPI()

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        existing_response = get_stored_response(request.prompt)
        if existing_response:
            return QueryResponse(answer=str(existing_response[0]['Response']), sources=[])

        sources = classify_sources(request.prompt, classifier_llm=ollama_llm)

        final_response = ""
        used_sources = []
        local_sources = []

        if "StackOverFlow" in sources and "StackOverFlow" not in used_sources:
            stack_response = await StackOverFlow_response(request.prompt, api_key="your_api_key")
            refined_response = small_llm.invoke(f"Improve and explain the following:\n{stack_response}")
            final_response += f"\n\n{stack_response}"
            used_sources.append("StackOverFlow")

        if "Wikipedia" in sources and "Wikipedia" not in used_sources:
            wikipedia_response = Wikipedia_Response(request.prompt)
            refined_response = small_llm.invoke(f"Improve and explain the following:\n{wikipedia_response}")
            final_response += f"\n\n{wikipedia_response}"
            used_sources.append("Wikipedia")

        if "FAISS_DB" in sources and "FAISS_DB" not in used_sources:
            local_docs = retriever.get_relevant_documents(request.prompt)
            local_answer = "\n\n".join([doc.page_content for doc in local_docs]).strip()
            refined_response = small_llm.invoke(f"Improve and explain the following:\n{local_answer}")
            final_response += f"\n\n{local_answer}"
            local_sources = [doc.metadata.get("source", "Unknown") for doc in local_docs if doc.metadata.get("source", "Unknown") != "Unknown"]
            used_sources.append("FAISS_DB")

        if "YouTube" in sources and "YouTube" not in used_sources:
            youtube_response = await YouTube_Response(request.prompt, api_key="your_api_key")
            final_response += f"\n\n{youtube_response}"
            used_sources.append("YouTube")

        similar_queries = get_similar_user_queries(request.prompt, k=3)
        context = f"use the following context to answer the question:\n\n{final_response}\n\nPast similar queries:\n"
        context += "\n".join(similar_queries) if similar_queries else "No past queries found."

        prompt = f"{context}\n\nQuestion: {request.prompt}"
        final_answer = ollama_llm.invoke(prompt)

        store_user_query(request.prompt, request.user_id)
        store_query_response(request.prompt, final_answer)

        return QueryResponse(answer=final_answer, sources=used_sources + local_sources)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))






#==================================================================Langgraph code=======================================================================
# from fastapi import FastAPI, Request
# from pydantic import BaseModel
# from fastapi.middleware.cors import CORSMiddleware
# from langgraph.graph import StateGraph, END
# from langgraph.prebuilt import ToolNode
# from langchain_core.runnables import Runnable
# from typing import TypedDict, Literal
# import faiss
# import numpy as np
# import httpx
# import os
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_community.vectorstores import FAISS
# from langchain_community.llms import Ollama
# from langchain_core.documents import Document
# from langchain_community.tools import WikipediaQueryRun
# from langchain_community.utilities import WikipediaAPIWrapper
# from duckduckgo_search import DDGS

# app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # adjust for production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class QueryModel(BaseModel):
#     query:str
#     user_id: str

# #LLM_models
# embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
# ollama_llm = Ollama(model='deepseek-r1:1.5b')
# small_llm = Ollama(model='gemma3:1b')

# BASE_DIR = os.path.dirname(__file__)
# FAISS_DB_PATH = os.path.join(BASE_DIR, "FAISS_DB")
# QUERY_DB_PATH = os.path.join(BASE_DIR, "Query_DB")
# QUERY_RESPONSE_DB_PATH = os.path.join(BASE_DIR, "Query_Response_DB")

# # Helper function to load or create FAISS index
# def load_or_create_faiss(path: str, model):
#     index_path = os.path.join(path, "index.faiss")
#     if os.path.exists(index_path):
#         return FAISS.load_local(path, model, allow_dangerous_deserialization=True)
#     else:
#         print(f"[Warning] {path} index not found. Creating new FAISS index...")
#         index = FAISS.from_documents([], model)
#         index.save_local(path)
#         return index

# # Load or create each index
# faiss_index = load_or_create_faiss(FAISS_DB_PATH, embedding_model)
# faiss_index_query = load_or_create_faiss(QUERY_DB_PATH, embedding_model)
# faiss_index_query_response = load_or_create_faiss(QUERY_RESPONSE_DB_PATH, embedding_model)

# #Credentials
# STACK_API_KEY = "rl_hzCWsuykMD5YuX4wfbw5YagZ5"
# YOUTUBE_API_KEY = "AIzaSyA8DC-VlDt0BTfC9jEonSStDg3yVNEokaU"

# def get_faiss_relevant_answer(prompt:str) -> dict:
#     docs = faiss_index_docs.similarity_search(prompt, k=3)
#     combined = " ".join(doc.page_content for doc in docs)
#     return {"faiss":combined}

# async def search_stackoverflow(input: dict) -> dict:
#     prompt = input["input"]
#     url = "https://api.stackexchange.com/2.3/search/advanced"
#     params = {
#         "order": "desc",
#         "sort": "relevance",
#         "q": prompt,
#         "site": "stackoverflow",
#         "key": STACK_API_KEY,
#     }

#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.get(url, params=params)
#             response.raise_for_status()
#             data = response.json()

#         if data["items"]:
#             top = data["items"][0]
#             content = f"{top['title']}\n{top['link']}"
#             return {"stack": content}
#         return {"stack": "No relevant StackOverflow result found."}
#     except Exception as e:
#         return {"stack": f"Error fetching StackOverflow result: {e}"}


# async def search_youtube(input: dict) -> dict:
#     prompt = input["input"]
#     url = "https://www.googleapis.com/youtube/v3/search"
#     params = {
#         "part": "snippet",
#         "q": prompt,
#         "type": "video",
#         "maxResults": 1,
#         "key": YOUTUBE_API_KEY,
#     }

#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.get(url, params=params)
#             response.raise_for_status()
#             data = response.json()

#         if data["items"]:
#             video = data["items"][0]
#             title = video["snippet"]["title"]
#             link = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
#             return {"yt": f"{title}\n{link}"}
#         return {"yt": "No relevant YouTube video found."}
#     except Exception as e:
#         return {"yt": f"Error fetching YouTube result: {e}"}



# def search_wikipedia(query: str) -> dict:
#     tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
#     result = tool.invoke(query)
#     return {"wiki": result}

# def check_query_in_faiss_DB(query: str, user_id: str) -> str | None:
#     matches = faiss_index_query.similarity_search(query, k=5)
#     for match in matches:
#         if match.metadata.get("text") == query and match.metadata.get("user_id") == user_id:
#             result = faiss_index_answer.similarity_search(query, k=5)
#             for res in result:
#                 if res.metadata.get("user_id") == user_id:
#                     return res.page_content
#     return None


# def store_query_to_FAISS(query: str, user_id: str):
#     doc = Document(
#         page_content=query,
#         metadata={
#             "text": query,
#             "user_id": user_id
#         }
#     )
#     faiss_index_query.add_documents([doc])
#     faiss_index_query.save_local("QUERY_DB")

# def store_answer_to_FAISS(query: str, answer: str, user_id: str):
#     doc = Document(
#         page_content=answer,
#         metadata={
#             "text": query,
#             "user_id": user_id
#         }
#     )
#     faiss_index_answer.add_documents([doc])
#     faiss_index_answer.save_local("Query_Response_DB")

# def combine_answers(query: str, faiss=None, wiki=None, stack=None, youtube=None) -> str:
#     parts = [("FAISS", faiss), ("Wikipedia", wiki), ("StackOverflow", stack), ("YouTube", youtube)]
#     context = "\n".join([f"{name}:\n{val}" for name, val in parts if val])
#     prompt = f"""You are a helpful AI tutor.

#     Query: {query}

#     Based on the following sources, generate a helpful, concise answer:

#     {context}

#     Final Answer:"""
#     return ollama_llm.invoke(prompt)

# class GraphState(TypedDict):
#     input: str
#     user_id: str
#     faiss: str
#     stack: str
#     yt: str
#     wiki: str
#     final_answer: str
#     source: Literal["faiss", "stackoverflow", "youtube", "wikipedia", "all"]
#     found_from_db: bool

# def check_memory(state: GraphState) -> dict:
#     query = state["input"]
#     user_id = state.get("user_id")  # Make sure it's passed in
#     answer = check_query_in_faiss_DB(query, user_id)
#     if answer:
#         return {
#             "input": query,
#             "final_answer": answer,
#             "found_from_db": True,
#             "user_id": user_id
#         }
#     return {"input": query, "found_from_db": False, "user_id": user_id}


# def classify_query(state: GraphState) -> dict:
#     query = state["input"]
#     prompt = f"""
#         you are a source classifier for an AI tutor.
#         Available sources:
#         - FAISS_DB: Contains structured tutorials and examples from curated content.
#         - StackOverflow: Useful for debugging or coding help.
#         - Wikipedia: Good for definitions and theory.
#         - YouTube: Great for visual explanations or walkthroughs.

#         classify the best source for this query. Return a list with sources.
#         Query:"{query}"
   

#         Respond with one of the above (lowercase only).
#     """
#     source = ollama_llm.invoke(prompt).strip().lower()
#     return {"input": query, "source": source}

# def answer(state: GraphState) -> dict:
#     return {
#         "final_answer": combine_answers(
#             query=state["input"],
#             faiss=state.get("faiss"),
#             wiki=state.get("wiki"),
#             stack=state.get("stack"),
#             youtube=state.get("yt")
#         )
#     }

# def store_result(state: GraphState) -> dict:
#     query = state["input"]
#     answer = state["final_answer"]
#     user_id = state["user_id"]
#     store_query_to_FAISS(query, user_id)
#     store_answer_to_FAISS(query, answer, user_id)
#     return state




# graph = StateGraph(GraphState)

# graph.add_node("check_memory", check_memory)
# graph.add_node("classify", classify_query)
# graph.add_node("faiss", ToolNode(get_faiss_relevant_answer))
# graph.add_node("wiki", ToolNode(search_wikipedia))
# graph.add_node("stack", ToolNode(search_stackoverflow))
# graph.add_node("yt", ToolNode(search_youtube))
# graph.add_node("answer", answer)
# graph.add_node("store", store_result)

# graph.set_entry_point("check_memory")


# def memory_found_router(state: GraphState) -> str:
#     return "end" if state.get("found_from_db") else "classify"

# def route_source(state: GraphState) -> str:
#     return {
#         "faiss": "faiss",
#         "wikipedia": "wiki",
#         "stackoverflow": "stack",
#         "youtube": "yt",
#         "all": "faiss"
#     }.get(state["source"], "faiss")

# graph.add_conditional_edges("check_memory", memory_found_router, {
#     "end": END,
#     "classify": "classify"
# })

# graph.add_conditional_edges("classify", route_source)
# graph.add_edge("faiss", "wiki")
# graph.add_edge("wiki", "stack")
# graph.add_edge("stack", "yt")
# graph.add_edge("yt", "answer")

# graph.add_edge("faiss", "answer")
# graph.add_edge("wiki", "answer")
# graph.add_edge("stack", "answer")
# graph.add_edge("yt", "answer")

# graph.add_edge("answer", "store")
# graph.set_finish_point("store")

# graph_app = graph.compile()

# # =================== FASTAPI ENDPOINT =====================

# @app.post("/query")
# async def handle_query(query: QueryModel):
#     result = graph_app.invoke({"input": query.query,"user_id":query.user_id})
#     return {"answer": result["final_answer"]}