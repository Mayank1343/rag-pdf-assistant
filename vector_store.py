import chromadb
from pathlib import Path

from pdf_processor import extract_pdf_text
from text_chunker import split_text
from embedding_generator import generate_embedding

# Connect to persistent ChromaDB
client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="company_policies",
    metadata={"hnsw:space": "cosine"}
)


def add_pdf_to_database(pdf_path):
    """Extract, chunk, embed and store one PDF."""

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        print("PDF file not found:", pdf_path)
        return

    if pdf_path.suffix.lower() != ".pdf":
        print("Only PDF files are supported.")
        return

    print("\nProcessing:", pdf_path.name)

    # Step 1: Extract text from the PDF
    pages = extract_pdf_text(pdf_path)

    if not pages:
        print("No extractable text found.")
        return

    # Step 2: Remove old records for this document
    # This prevents duplicates when the PDF is reprocessed.
    collection.delete(
        where={"source": pdf_path.name}
    )

    ids = []
    documents = []
    embeddings = []
    metadatas = []

    # Step 3: Process each page
    for page in pages:

        chunks = split_text(page["text"])

        for chunk_number, chunk in enumerate(chunks, start=1):

            chunk_id = (
                f"{pdf_path.name}_page{page['page']}"
                f"_chunk{chunk_number}"
            )

            # Generate an embedding using the document prefix
            embedding = generate_embedding(chunk)

            ids.append(chunk_id)
            documents.append(chunk)
            embeddings.append(embedding)

            metadatas.append({
                "source": pdf_path.name,
                "page": page["page"],
                "chunk": chunk_number
            })

    # Step 4: Save records to ChromaDB
    if ids:
        collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

    print("Successfully processed:", pdf_path.name)
    print("Chunks stored:", len(ids))
    print("Total database records:", collection.count())


if __name__ == "__main__":
    from pathlib import Path

    for pdf_path in Path("./data").glob("*.pdf"):
        add_pdf_to_database(pdf_path)