import json
from pathlib import Path

from app.analytics.evidence import build_failure_evidence
from app.analytics.guardrails import validate_investigation_response


CASES_PATH = Path("evaluation/groundedness_cases.json")


def load_cases() -> list[dict]:
    with CASES_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_test_evidence() -> dict:
    return build_failure_evidence(
        {
            "total_failed": 8,
            "failure_reasons": {
                "TIMEOUT": 3,
                "INSUFFICIENT_FUNDS": 2,
                "BANK_ERROR": 2,
                "TECHNICAL_ERROR": 1,
            },
        }
    )


def evaluate_groundedness() -> dict:
    cases = load_cases()
    evidence = get_test_evidence()

    correct = 0
    total = len(cases)

    print("\nGroundedness Evaluation")
    print("=" * 60)

    for case in cases:
        name = case["name"]
        response = case["response"]
        expected_valid = case["expected_valid"]

        validation = validate_investigation_response(
            response=response,
            evidence=evidence,
        )

        actual_valid = validation["valid"]
        is_correct = actual_valid == expected_valid

        if is_correct:
            correct += 1

        status = "PASS" if is_correct else "FAIL"

        print(f"\n[{status}]")
        print(f"Case     : {name}")
        print(f"Expected : {expected_valid}")
        print(f"Actual   : {actual_valid}")

        if validation["errors"]:
            print("Errors:")
            for error in validation["errors"]:
                print(f"  - {error}")

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
    evaluate_groundedness()
