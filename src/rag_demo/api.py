from fastapi import FastAPI, HTTPException, UploadFile
from pydantic import BaseModel
from dotenv import load_dotenv, find_dotenv

from langchain_openai import ChatOpenAI

from rag_demo.knowledge_base import KnowledgeBase
from rag_demo.pipeline import RAGPipeline

from pathlib import Path


app = FastAPI()

# Build kb / retriever / llm / rag_pipeline here, once, at import time
# (same steps main.py already does)

load_dotenv(find_dotenv(usecwd=True))

# Build a KnowledgeBase and build the index with the files in the "/data" directory
kb = KnowledgeBase()
kb.build_index("data")

# Get a retriever
retriever = kb.as_retriever(k=3)

# Configure an AI model
ai_model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Build a RAG pipeline 
rag_pipeline = RAGPipeline(
    retriever = retriever,
    llm = ai_model,
)

def rebuild_rag_pipeline() -> None:
    """Rebuild the index and replace the shared RAG pipeline"""
    global rag_pipeline

    # Rebuild kb's vector store
    kb.build_index("data")
    # Create a new retriever
    retriever = kb.as_retriever(k=3)
    # Assign a new RAGPipeline to the shared rag_pipeline variable
    rag_pipeline = RAGPipeline(
        retriever = retriever,
        llm = ai_model
    )

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str

@app.get("/health")
def health():
    """Confirm that the API process is running"""
    
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    """Answer one question using the RAG pipeline."""

    # Call rag_pipeline.ask() with request.question
    ai_response = rag_pipeline.ask(request.question)

    # Return a QueryResponse whose anwer contains the result
    return {"answer": ai_response}

# GET /documents, POST /docuemnts, DELETE /documents/{filename} below

@app.post("/documents")
async def upload_documents(file: UploadFile):
    """Save a text document into data/"""

    # Safely extract only the filename
    filename = Path(file.filename or "").name

    # Reject empty or suspicious file names
    if not filename or filename in (".", "..", "..."):
        raise HTTPException(status_code=400, detail="Invalid filename")

    # Check that it's suffix is ".txt"
    if not filename.lower().endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are allowed")

    # Read the uploaded bytes
    contents = await file.read()

    target = Path("data") / filename
    target.write_bytes(contents)

    rebuild_rag_pipeline()

    return {"filename": filename}


@app.get("/documents")
def retrieve_documents():
    """Return the filenames currently stored in data/"""

    # Create a Path representing "data"
    data_directory = Path("data")

    # Iterate through its contents
    filenames = sorted(
        this_file.name for this_file in data_directory.iterdir()
        if this_file.is_file()
    )

    # Return the filenames in the sorted order
    return filenames

@app.delete("/documents/{passed_in_filename}")
def delete_document(passed_in_filename: str):
    """Delete a document and rebuild the RAG pipeline"""
    
    # Extract the safe filename using Path(filename.name)
    # Reject it with HTTP 400 if it differs from the supplied filename
        
        # Safely extract only the filename
    filename = Path(passed_in_filename).name

    if filename != passed_in_filename:
        raise HTTPException(
            status_code=400, 
            detail=f"invalid filename '{passed_in_filename}'. Use a plain filename like 'example_file.txt'")

    # Reject empty or suspicious file names
    if not filename or filename in (".", "..", "..."):
        raise HTTPException(status_code=400, detail="Invalid filename")

    # Check that it's suffix is ".txt"
    if not filename.lower().endswith(".txt"):
        raise HTTPException(status_code=400, detail="You can only delete .txt files")

    # Build the target path inside /data
    target = Path("data") / filename
    # If target.is_file() is False, raise HTTP 404.
    if not target.is_file():
        raise HTTPException(status_code=404, detail=f"That file '{filename}' doesn't exist on the server")
    
    # Delete it using target.unlink
    target.unlink()

    # call rebuild_rag_pipeline()
    rebuild_rag_pipeline()

    # Return a confirmation dictionary
    return {"status": f"okay - file '{filename}' has been deleted"}

