from pathlib import Path

from vector_store import add_pdf_to_database, collection

DATA_DIR = Path("./data")
DATA_DIR.mkdir(exist_ok=True)


def add_document():
    filename = input("Enter PDF filename: ").strip()

    pdf_path = DATA_DIR / filename

    if not pdf_path.exists():
        print("File not found. Copy the PDF into the data folder first.")
        return

    add_pdf_to_database(pdf_path)


def list_documents():
    # Retrieve metadata from all stored chunks
    records = collection.get(
        include=["metadatas"]
    )

    # Use a set to avoid listing the same PDF multiple times
    filenames = {
        item["source"]
        for item in records["metadatas"]
    }

    print("\nDocuments in knowledge base:")

    if not filenames:
        print("No documents found.")
        return

    for filename in sorted(filenames):
        print("-", filename)


def delete_document():
    filename = input("Enter PDF filename to delete: ").strip()

    # Check whether this document exists in ChromaDB
    existing = collection.get(
        where={"source": filename},
        include=["metadatas"]
    )

    if not existing["ids"]:
        print("Document not found in the database.")
        return

    # Delete all chunks belonging to this PDF
    collection.delete(
        where={"source": filename}
    )

    print("Document removed from ChromaDB:", filename)


def main():

    while True:

        print("\n===== RAG DOCUMENT MANAGER =====")
        print("1. Add PDF")
        print("2. List documents")
        print("3. Delete PDF")
        print("4. Exit")

        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            add_document()

        elif choice == "2":
            list_documents()

        elif choice == "3":
            delete_document()

        elif choice == "4":
            print("Exiting document manager.")
            break

        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()