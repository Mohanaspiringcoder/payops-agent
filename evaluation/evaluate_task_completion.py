import json
from pathlib import Path

from langgraph.types import Command

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

    for index, case in enumerate(cases, start=1):
        name = case["name"]
        question = case["question"]
        approval_status = case["approval_status"]
        expected_incident_status = case["expected_incident_status"]

        thread_id = f"task-completion-{index}"
        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

        initial_state = {
            "thread_id": thread_id,
            "question": question,
            "evidence": {},
            "operational_knowledge": {},
            "investigation": "",
            "validation": {},
            "retry_count": 0,
            "report": {},
            "approval_status": "REJECTED",
            "approval": {},
            "incident": {},
        }

        paused = investigation_graph.invoke(
            initial_state,
            config=config,
        )

        paused_for_approval = bool(
            paused.get("__interrupt__")
        )

        if paused_for_approval:
            result = investigation_graph.invoke(
                Command(
                    resume={
                        "decision": approval_status,
                    }
                ),
                config=config,
            )
        else:
            result = paused

        incident = result.get("incident", {})

        actual_incident_status = incident.get(
            "status",
            "INCOMPLETE",
        )

        is_correct = (
            paused_for_approval
            and actual_incident_status == expected_incident_status
        )

        if is_correct:
            correct += 1

        status = "PASS" if is_correct else "FAIL"

        print(f"\n[{status}]")
        print(f"Case     : {name}")
        print(f"Approval : {approval_status}")
        print(f"Paused   : {paused_for_approval}")
        print(f"Expected : {expected_incident_status}")
        print(f"Actual   : {actual_incident_status}")

        if not paused_for_approval:
            print(
                "Reason   : Investigation workflow did not pause "
                "for human approval."
            )
        elif actual_incident_status == "INCOMPLETE":
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
