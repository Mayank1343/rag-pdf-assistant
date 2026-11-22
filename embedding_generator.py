import ollama

from text_chunker import split_text
from pdf_processor import process_all_pdfs

# Local embedding model
EMBEDDING_MODEL = "nomic-embed-text"


def generate_embedding(text, task="search_document"):
    """Convert text into a task-specific embedding vector."""

    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=f"{task}: {text}"
    )

    return response["embeddings"][0]


def generate_all_embeddings():
    """Extract PDFs, chunk their text, and embed every chunk."""

    # Step 1: Extract text from all PDFs
    pages = process_all_pdfs()

    all_chunks = []

    # Step 2: Split each page into smaller chunks
    for page in pages:
        chunks = split_text(page["text"])

        for chunk_number, chunk in enumerate(chunks, start=1):
            all_chunks.append({
                "text": chunk,
                "source": page["source"],
                "page": page["page"],
                "chunk": chunk_number
            })

    print("\nTotal chunks:", len(all_chunks))

    # Step 3: Generate an embedding for every chunk
    for index, item in enumerate(all_chunks, start=1):
        item["embedding"] = generate_embedding(item["text"])

        print(
            f"Generated embedding {index}/{len(all_chunks)}"
        )

    return all_chunks


if __name__ == "__main__":

    chunks = generate_all_embeddings()

    print("\nEmbedding generation completed!")

    if chunks:
        print("Total embeddings:", len(chunks))
        print("Dimensions:", len(chunks[0]["embedding"]))
        print("First chunk source:", chunks[0]["source"])
        print("First chunk page:", chunks[0]["page"])