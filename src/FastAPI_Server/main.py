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

class QueryRequest(BaseModel):
    prompt:str

class QueryResponse(BaseModel):
    answer:str
    sources:List[str]

def intialize_components():
    try:
        faiss_index = faiss.read_index("knowledge_base_python.index")
        with open("metadata.json","r", encoding="utf-8") as f:
            metadata = json.load(f)


        documents = [Document(
            page_content = f"Topic:{item['topic']}\nExplanation:{item['explanation']}\nExample:{item['example']['code']}",
            metadata = {"source":item.get("source", "")}
            )
            for item in metadata
        ]


        embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        index_to_docstore_id = {i : str(i) for i in range(len(documents))}
        docstore = InMemoryDocstore(dict(zip(index_to_docstore_id.values(),documents)))

        retriever = FAISS(
            embedding_function=embedding_function,
            index=faiss_index,
            docstore=docstore,
            index_to_docstore_id=index_to_docstore_id,
        )

        return retriever.as_retriever(search_type='similarity',search_kwargs={"k":3}),documents,embedding_function,faiss_index,retriever

    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Failed to intialize components:{str(e)}")

retriever, document_list, embedding_function, faiss_index, vectorstore= intialize_components()
ollama_llm = Ollama(model='deepseek-r1:1.5b')

app=FastAPI()

@app.post("/query", response_model=QueryResponse)
async def process_query(request:QueryRequest):
    try:
        start_time= time.time()

        local_docs = retriever.get_relevant_documents(request.prompt)
        local_answer = "\n\n".join([doc.page_content for doc in local_docs]).strip()
        local_sources = [doc.metadata.get("source","Unknown") for doc in local_docs]
        local_sources = [s for s in local_sources if s != "Unknown"]

        prompt = f"use the following context to answer the following question:\n\n{local_answer}\n\nQuestion({request.prompt})"
        response=ollama_llm.invoke(prompt)

        return QueryResponse(
            answer=response,
            sources=local_sources
        )
    except Exception as e:
        print("🔥 error in /query:",str(e))
        raise HTTPException(status_code=500,detail=str(e))



