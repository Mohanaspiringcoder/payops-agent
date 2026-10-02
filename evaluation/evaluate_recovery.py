import json
from pathlib import Path

from app.graph.investigation_graph import route_after_validation


CASES_PATH = Path("evaluation/recovery_cases.json")


def load_cases() -> list[dict]:
    with CASES_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def evaluate_recovery() -> dict:
    cases = load_cases()

    correct = 0
    total = len(cases)

    print("\nTool Failure Recovery Evaluation")
    print("=" * 60)

    for case in cases:
        name = case["name"]
        retry_count = case["initial_retry_count"]
        expected_retry_count = case["expected_retry_count"]
        expected_route = case["expected_route"]

        state = {
            "question": "Investigate why payments are failing",
            "evidence": {},
            "operational_knowledge": {},
            "investigation": "Invalid investigation response",
            "validation": {
                "valid": False,
                "errors": ["Simulated validation failure"],
            },
            "retry_count": retry_count,
            "report": {},
            "approval_status": "REJECTED",
            "approval": {},
            "incident": {},
        }

        actual_route = route_after_validation(state)

        if actual_route == "retry":
            actual_retry_count = retry_count + 1
        else:
            actual_retry_count = retry_count

        is_correct = (
            actual_retry_count == expected_retry_count
            and actual_route == expected_route
        )

        if is_correct:
            correct += 1

        status = "PASS" if is_correct else "FAIL"

        print(f"\n[{status}]")
        print(f"Case          : {name}")
        print(f"Expected route: {expected_route}")
        print(f"Actual route  : {actual_route}")
        print(f"Expected retry: {expected_retry_count}")
        print(f"Actual retry  : {actual_retry_count}")

    accuracy = (correct / total) * 100 if total else 0

    print("\n" + "=" * 60)
    print(f"Correct : {correct}/{total}")
    print(f"Recovery Evaluation Accuracy: {accuracy:.2f}%")
    print("=" * 60)

    return {
        "correct": correct,
        "total": total,
        "accuracy": accuracy,
    }


if __name__ == "__main__":
    evaluate_recovery()
