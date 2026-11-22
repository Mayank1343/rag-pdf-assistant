import chromadb
import ollama

# Connect to our existing persistent database
client = chromadb.PersistentClient(path="./chroma_db")

# Access the collection we created earlier
collection = client.get_collection(
    name="company_policies"
)

EMBEDDING_MODEL = "nomic-embed-text"


def retrieve_documents(question, top_k=3):
    """Find the most relevant document chunks for a question."""

    # Generate an embedding specifically for a search query
    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=f"search_query: {question}"
    )

    query_embedding = response["embeddings"][0]

    # Search ChromaDB using the query vector
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    retrieved_documents = []

    # Extract the matching documents and their metadata
    for index, document in enumerate(results["documents"][0]):

        retrieved_documents.append({
            "text": document,
            "source": results["metadatas"][0][index]["source"],
            "page": results["metadatas"][0][index]["page"],
            "distance": results["distances"][0][index]
        })

    return retrieved_documents


if __name__ == "__main__":

    question = "How many annual leave days do employees receive?"

    documents = retrieve_documents(question)

    print("\nUser question:", question)

    print("\nRetrieved documents:")

    for index, document in enumerate(documents, start=1):
        print(f"\n--- Result {index} ---")
        print("Source:", document["source"])
        print("Page:", document["page"])
        print("Distance:", round(document["distance"], 4))
        print("Text:", document["text"])