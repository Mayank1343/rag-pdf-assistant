from rag_pipeline import generate_answer
from answer_evaluation_dataset import answer_evaluation_dataset


def evaluate_answers():

    total_tests = len(answer_evaluation_dataset)

    correct_answers = 0
    correct_refusals = 0

    print("\n===== RAG ANSWER EVALUATION =====")

    for index, test in enumerate(answer_evaluation_dataset, start=1):

        question = test["question"]
        expected_terms = test["expected_terms"]
        should_refuse = test["should_refuse"]

        # Generate an answer using the existing RAG pipeline
        result = generate_answer(question)

        # Support either dictionary or tuple return formats
        if isinstance(result, dict):
            answer = result["answer"]
        else:
            answer = result[0]

        answer_lower = answer.lower()

        # Check whether expected information appears in the answer
        if should_refuse:
            refusal_found = (
                "couldn't find this information" in answer_lower
                or "not found" in answer_lower
                or "don't have enough information" in answer_lower
            )

            passed = refusal_found

            if passed:
                correct_refusals += 1

        else:
            passed = all(
                term.lower() in answer_lower
                for term in expected_terms
            )

            if passed:
                correct_answers += 1

        print(f"\nTest {index}: {question}")
        print("Generated answer:", answer)
        print("Expected terms:", expected_terms)
        print("Result:", "PASS" if passed else "FAIL")

    passed_tests = correct_answers + correct_refusals

    print("\n===== EVALUATION SUMMARY =====")
    print(f"Total tests: {total_tests}")
    print(f"Correct factual answers: {correct_answers}/4")
    print(f"Correct refusals: {correct_refusals}/1")
    print(f"Total passed: {passed_tests}/{total_tests}")
    print(f"Pass rate: {(passed_tests / total_tests) * 100:.2f}%")


if __name__ == "__main__":
    evaluate_answers()