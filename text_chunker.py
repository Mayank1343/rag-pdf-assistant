import re


def split_text(text, chunk_size=800, chunk_overlap=150):
    """
    Split text into chunks using sentence boundaries.

    Args:
        text: Input text extracted from a PDF.
        chunk_size: Maximum approximate characters per chunk.
        chunk_overlap: Approximate overlap between consecutive chunks.

    Returns:
        A list of text chunks.
    """

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return []

    # Split text into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current_chunk = []

    for sentence in sentences:

        # Calculate the size if we add this sentence
        candidate = " ".join(current_chunk + [sentence])

        if len(candidate) <= chunk_size:
            current_chunk.append(sentence)

        else:
            # Save the existing chunk
            if current_chunk:
                chunk_text = " ".join(current_chunk)
                chunks.append(chunk_text)

            # Preserve overlap from the previous chunk
            overlap_text = ""
            if current_chunk and chunk_overlap > 0:
                previous_text = " ".join(current_chunk)

                if len(previous_text) > chunk_overlap:
                    # Extract overlap while preserving complete words
                    overlap_words = previous_text.split()
                    overlap_text = ""

                    for word in reversed(overlap_words):
                        candidate = word + " " + overlap_text if overlap_text else word

                        if len(candidate) > chunk_overlap:
                            break

                        overlap_text = candidate
                else:
                    overlap_text = previous_text

            # Start the next chunk with overlap
            current_chunk = [overlap_text, sentence] if overlap_text else [sentence]

    # Save the final chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks