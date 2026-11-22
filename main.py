from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional
from fastapi import UploadFile, File, HTTPException
from pathlib import Path
import shutil
import chromadb


from vector_store import add_pdf_to_database
from rag_pipeline import generate_answer


# Create FastAPI application
app = FastAPI(
    title="Local RAG Assistant API",
    description="Ask questions about your PDF documents using RAG.",
    version="1.0.0"
)


# Request model for conversational questions
class QuestionRequest(BaseModel):

    question: str = Field(
        min_length=3,
        max_length=1000,
        description="Question to ask the RAG assistant"
    )

    chat_history: list[dict] = Field(
        default_factory=list,
        description="Previous conversation messages"
    )


# Connect to the existing ChromaDB database
chroma_client = chromadb.PersistentClient(path="./chroma_db")

collection = chroma_client.get_collection(
    name="company_policies"
)

# Root endpoint
@app.get("/")
def home():
    return {
        "message": "Welcome to the Local RAG Assistant API",
        "status": "running"
    }


# Health-check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "RAG Assistant"
    }


# Conversational RAG endpoint
@app.post("/ask")
def ask_question(request: QuestionRequest):

    result = generate_answer(
        request.question,
        chat_history=request.chat_history
    )

    # Return answer and sources
    return {
        "question": request.question,
        "answer": result["answer"],
        "sources": result["sources"],
        "search_query": result.get("search_query")
    }


# Directory where uploaded PDFs will be stored
DATA_DIR = Path("./data")
DATA_DIR.mkdir(exist_ok=True)


@app.post("/documents/upload")
def upload_document(file: UploadFile = File(...)):

    # Accept PDF files only
    if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    # Save the uploaded PDF
    file_path = DATA_DIR / Path(file.filename).name

    try:
        with file.file as source:
            with open(file_path, "wb") as destination:
                shutil.copyfileobj(source, destination)

        # Process and store its chunks in ChromaDB
        add_pdf_to_database(file_path)

        return {
            "message": "Document uploaded and indexed successfully.",
            "filename": file_path.name
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(error)}"
        )

@app.get("/documents")
def list_documents():

    # Retrieve metadata from all indexed chunks
    results = collection.get(
        include=["metadatas"]
    )

    # Extract unique document names
    documents = {}

    for metadata in results["metadatas"]:
        filename = metadata["source"]

        if filename not in documents:
            documents[filename] = 0

        documents[filename] += 1

    return {
        "total_documents": len(documents),
        "documents": [
            {
                "filename": filename,
                "chunks": chunk_count
            }
            for filename, chunk_count in documents.items()
        ]
    }


@app.delete("/documents/{filename}")
def delete_document(filename: str):

    # Prevent directory traversal
    if Path(filename).name != filename or Path(filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF filename."
        )

    file_path = DATA_DIR / filename

    # Check whether the document is indexed
    existing = collection.get(
        where={"source": filename},
        include=["metadatas"]
    )

    if not existing["ids"]:
        raise HTTPException(
            status_code=404,
            detail="Document not found in the database."
        )

    # Delete indexed chunks
    collection.delete(
        where={"source": filename}
    )

    # Delete original PDF if it exists
    if file_path.exists():
        file_path.unlink()

    return {
        "message": "Document deleted successfully.",
        "filename": filename
    }

