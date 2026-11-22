import pymupdf
from pathlib import Path

# Locate the data folder relative to this Python file
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"


def extract_pdf_text(pdf_path):

    # Open the PDF document
    document = pymupdf.open(pdf_path)

    extracted_pages = []

    # Extract text page by page
    for page_number, page in enumerate(document, start=1):

        text = page.get_text("text")

        # Store text along with its original page number
        if text.strip():
            extracted_pages.append({
                "text": text,
                "page": page_number,
                "source": pdf_path.name
            })

    document.close()

    return extracted_pages


def process_all_pdfs():

    # Find every PDF inside the data folder
    pdf_files = list(DATA_DIR.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found in the data folder.")
        return

    print(f"Found {len(pdf_files)} PDF files.")

    all_pages = []

    for pdf_file in pdf_files:

        print(f"\nProcessing: {pdf_file.name}")

        pages = extract_pdf_text(pdf_file)

        print(f"Extracted {len(pages)} pages.")

        all_pages.extend(pages)

    print("\nTotal extracted pages:", len(all_pages))

    # Display a small preview of extracted content
    if all_pages:
        print("\nFirst page preview:")
        print(all_pages[0]["text"][:1000])

        print("\nSource:", all_pages[0]["source"])
        print("Page:", all_pages[0]["page"])

    return all_pages


if __name__ == "__main__":
    process_all_pdfs()
