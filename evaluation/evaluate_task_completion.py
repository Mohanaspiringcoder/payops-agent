import json
from pathlib import Path

from app.graph.investigation_graph import graph as investigation_graph


CASES_PATH = Path("evaluation/task_completion_cases.json")


def load_cases() -> list[dict]:
    with CASES_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def evaluate_task_completion() -> dict:
    cases = load_cases()

    correct = 0
    total = len(cases)

    print("\nTask Completion Evaluation")
    print("=" * 60)

    for case in cases:
        name = case["name"]
        question = case["question"]
        approval_status = case["approval_status"]
        expected_incident_status = case["expected_incident_status"]

        result = investigation_graph.invoke(
            {
                "question": question,
                "evidence": {},
                "operational_knowledge": {},
                "investigation": "",
                "validation": {},
                "retry_count": 0,
                "report": {},
                "approval_status": approval_status,
                "approval": {},
                "incident": {},
            }
        )

        incident = result.get("incident", {})

        actual_incident_status = incident.get(
            "status",
            "INCOMPLETE",
        )

        is_correct = (
            actual_incident_status == expected_incident_status
        )

        if is_correct:
            correct += 1

        status = "PASS" if is_correct else "FAIL"

        print(f"\n[{status}]")
        print(f"Case     : {name}")
        print(f"Approval : {approval_status}")
        print(f"Expected : {expected_incident_status}")
        print(f"Actual   : {actual_incident_status}")

        if actual_incident_status == "INCOMPLETE":
            print(
                "Reason   : Investigation workflow did not reach "
                "the incident decision stage."
            )

    completion_rate = (
        (correct / total) * 100
        if total
        else 0
    )

    print("\n" + "=" * 60)
    print(f"Completed correctly: {correct}/{total}")
    print(f"Task Completion Rate: {completion_rate:.2f}%")
    print("=" * 60)

    return {
        "correct": correct,
        "total": total,
        "completion_rate": completion_rate,
    }


if __name__ == "__main__":
    evaluate_task_completion()
