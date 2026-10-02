import json
from pathlib import Path

from app.agents.planner import plan_request


CASES_PATH = Path("evaluation/intent_cases.json")


def load_cases() -> list[dict]:
    with CASES_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def evaluate_intent_selection() -> dict:
    cases = load_cases()

    correct = 0
    total = len(cases)

    print("\nIntent Selection Evaluation")
    print("=" * 60)

    for case in cases:
        question = case["question"]
        expected_intent = case["expected_intent"]

        result = plan_request(question)
        predicted_intent = result

        is_correct = predicted_intent == expected_intent

        if is_correct:
            correct += 1

        status = "PASS" if is_correct else "FAIL"

        print(f"\n[{status}]")
        print(f"Question : {question}")
        print(f"Expected : {expected_intent}")
        print(f"Predicted: {predicted_intent}")

    accuracy = (correct / total) * 100 if total else 0

    print("\n" + "=" * 60)
    print(f"Correct : {correct}/{total}")
    print(f"Accuracy: {accuracy:.2f}%")
    print("=" * 60)

    return {
        "correct": correct,
        "total": total,
        "accuracy": accuracy,
    }


if __name__ == "__main__":
    evaluate_intent_selection()
