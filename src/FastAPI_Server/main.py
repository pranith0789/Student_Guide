from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langgraph.graph import StateGraph, END
import ollama
import os

app = FastAPI()

# Load FAISS index and embedding model
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db = FAISS.load_local("FAISS_DB/faiss_index", embedding_model, allow_dangerous_deserialization=True)

query_db_path = "FAISS_DB/query_index"

# Create an empty query_db if not exists
if os.path.exists(query_db_path):
    query_db = FAISS.load_local(query_db_path, embedding_model, allow_dangerous_deserialization=True)
else:
    # Create directory if it doesn't exist
    os.makedirs("FAISS_DB", exist_ok=True)
    
    # Create an empty FAISS index
    from langchain_core.documents import Document
    empty_doc = Document(page_content='init', metadata={'source': 'init'})
    query_db = FAISS.from_documents([empty_doc], embedding_model)
    
    # Save the initial database
    query_db.save_local(query_db_path)
    print("✅ created new empty query_db")

# Load the database (either existing or newly created)
query_db = FAISS.load_local(query_db_path, embedding_model, allow_dangerous_deserialization=True)

# FastAPI Request and Response Models
class QueryRequest(BaseModel):
    prompt:str

class QueryResponse(BaseModel):
    answer: str
    sources: list[str]

# LangGraph State
class SearchState(dict):
    def __init__(self, query=""):  # Allow initializing with query
        super().__init__()
        self.update({
            'query': query,  # Initialize query
            'retrieved_docs': [],  # List to hold docs
            'sources': [],  # List to hold sources
            'answer': ""  # Store the answer
        })

def retrieve_documents(state: dict) -> dict:
    print(f"Initial state in retrieve_documents: {state}")
    if isinstance(state, SearchState):
        state = dict(state)

    query = state.get('query', '')
    if not query:
        raise ValueError("Empty query received")
    
    # Search documents
    docs = db.similarity_search(query, k=5)
    
    # 🔥 Search similar queries too
    similar_queries_docs = query_db.similarity_search(query, k=5)
    similar_queries = [doc.page_content for doc in similar_queries_docs]
    
    return {
        'query': query,
        'retrieved_docs': docs,
        'similar_queries': similar_queries,  # 🆕 Store similar queries
        'sources': list({doc.metadata.get('source') for doc in docs if doc.metadata.get('source')}),
        'answer': state.get('answer', '')
    }

def refine_answer(state: dict) -> dict:
    print(f"State in refine_answer: {state}")
    if isinstance(state, SearchState):
        state = dict(state)

    query = state.get('query', '')
    if not query:
        raise ValueError("Empty query in refine_answer")

    # Prepare contexts
    doc_context = "\n\n".join([doc.page_content for doc in state.get('retrieved_docs', [])])
    queries_context = "\n\n".join(state.get('similar_queries', []))

    # Combine everything into a prompt
    full_context = f"""
Relevant Previous Queries:
{queries_context}

Knowledge Base Documents:
{doc_context}

Question:
{query}
"""

    # Generate response using full context
    response = ollama.chat(
        model="deepseek-r1:1.5b",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Answer based on the provided previous queries and documents."},
            {"role": "user", "content": full_context}
        ]
    )
    refined_answer = response['message']['content']
    
    return {
        'query': query,
        'retrieved_docs': state.get('retrieved_docs', []),
        'similar_queries': state.get('similar_queries', []),
        'sources': state.get('sources', []),
        'answer': refined_answer.strip()
    }

# Build the graph
graph = StateGraph(dict)  # Use dict instead of SearchState
graph.add_node("retrieve_documents", retrieve_documents)
graph.add_node("refine_answer", refine_answer)

graph.set_entry_point("retrieve_documents")
graph.add_edge("retrieve_documents", "refine_answer")
graph.add_edge("refine_answer", END)

app_graph = graph.compile()

# FastAPI Endpoint
@app.post("/query", response_model=QueryResponse)
async def query_handler(request: QueryRequest):
    try:
        print(f"Received query: {request.prompt}")

        # Run the graph
        initial_state = {
            'query': request.prompt,
            'retrieved_docs': [],
            'sources': [],
            'answer': ''
        }
        print(f"Initial state: {initial_state}")
        
        # Ensure the graph execution completes
        final_state = app_graph.invoke(initial_state)
        if final_state is None:
            raise ValueError("Graph execution returned None")
            
        print(f"Final state: {final_state}")
        
        # Extract the answer and sources from the final state
        answer = final_state.get('answer', '')
        sources = final_state.get('sources', [])
        
        if not answer:
            raise ValueError("No answer generated")
            
        # Store the query in query_db
        new_doc = Document(
            page_content=request.prompt,
            metadata={'source': 'user_query'}
        )
        query_db.add_documents([new_doc])
        query_db.save_local(query_db_path)
        print("✅ Saved new query to query_db")

        # Return the response
        response = QueryResponse(
            answer=answer,
            sources=sources
        )
        print(f"Returning response: {response}")
        return response

    except Exception as e:
        print(f"Error in query handler: {str(e)}")
        error_response = QueryResponse(
            answer=f"Error processing query: {str(e)}",
            sources=[]
        )
        print(f"Returning error response: {error_response}")
        return error_response


