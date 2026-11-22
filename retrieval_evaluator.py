from retriever import retrieve_documents
from evaluation_dataset import evaluation_dataset


def evaluate_retrieval():

    total_tests = len(evaluation_dataset)

    source_hits = 0
    evidence_hits = 0

    print("\n===== RAG RETRIEVAL EVALUATION =====")

    for index, test in enumerate(evaluation_dataset, start=1):

        question = test["question"]
        expected_source = test["expected_source"]
        expected_terms = test["expected_terms"]

        # Retrieve the top 3 document chunks
        results = retrieve_documents(question, top_k=3)

        # Check whether the expected PDF was retrieved
        retrieved_sources = [
            item["source"] for item in results
        ]

        source_found = expected_source in retrieved_sources

        if source_found:
            source_hits += 1

        # Combine retrieved text for evidence checking
        retrieved_text = " ".join(
            item["text"] for item in results
        ).lower()

        # Check whether all expected terms appear
        evidence_found = all(
            term.lower() in retrieved_text
            for term in expected_terms
        )

        if evidence_found:
            evidence_hits += 1

        # Display individual test results
        print(f"\nTest {index}: {question}")

        print("Expected PDF:", expected_source)
        print("Retrieved PDFs:", retrieved_sources)

        print(
            "Source match:",
            "PASS" if source_found else "FAIL"
        )

        print(
            "Evidence match:",
            "PASS" if evidence_found else "FAIL"
        )

    # Calculate evaluation metrics
    source_accuracy = (source_hits / total_tests) * 100
    evidence_accuracy = (evidence_hits / total_tests) * 100

    print("\n===== EVALUATION SUMMARY =====")

    print(f"Total tests: {total_tests}")
    print(f"Source matches: {source_hits}/{total_tests}")
    print(f"Evidence matches: {evidence_hits}/{total_tests}")

    print(f"Source hit rate: {source_accuracy:.2f}%")
    print(f"Evidence hit rate: {evidence_accuracy:.2f}%")


if __name__ == "__main__":
    evaluate_retrieval()