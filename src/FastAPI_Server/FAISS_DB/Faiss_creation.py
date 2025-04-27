import json
from langgraph.graph import StateGraph, END
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings

# Load data
with open("src\\FastAPI_Server\\FAISS_DB\\knowledge_base_python.json", 'r', encoding='utf-8') as f:
    data = json.load(f)

# Embedding model
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Functions
def create_documents(state):
    documents = []
    for item in data:
        text_parts = []
        text_parts.append(f"Topic:{item['topic']}")
        text_parts.append(f"Explanation:{item['explanation']}")
        if item.get("example") and item["example"].get("code"):
            text_parts.append(f"Example:{item['example']['code']}")
        
        full_text = "\n".join(text_parts)

        doc = Document(
            page_content=full_text,
            metadata={
                "topic": item["topic"],
                "level": item.get("level", "unknown"),
                "source": item.get("source", "unknown")
            }
        )
        documents.append(doc)
    return {"documents": documents}

def store_in_faiss(state):
    documents = state["documents"]
    db = FAISS.from_documents(documents, embedding_model)
    db.save_local("faiss_index")
    print("✅ FAISS DB saved successfully!")
    return {}

# Graph
graph = StateGraph(dict)
graph.add_node("create_documents", create_documents)
graph.add_node("store_in_faiss", store_in_faiss)
graph.set_entry_point("create_documents")
graph.add_edge("create_documents", "store_in_faiss")
graph.add_edge("store_in_faiss", END)

# Compile and run
app = graph.compile()

initial_state = {"documents": []}
app.invoke(initial_state)
