from langgraph.types import Command

from app.graph.investigation_graph import graph


def build_state(thread_id: str) -> dict:
    return {
        "thread_id": thread_id,
        "question": "Investigate why payments are failing",
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


def build_config(thread_id: str) -> dict:
    return {
        "configurable": {
            "thread_id": thread_id,
        }
    }


def evaluate_hitl() -> dict:
    cases = [
        {
            "name": "approved_incident_creation",
            "decision": "APPROVED",
            "expected_created": True,
            "expected_status": "CREATED",
        },
        {
            "name": "rejected_incident_blocked",
            "decision": "REJECTED",
            "expected_created": False,
            "expected_status": "BLOCKED",
        },
    ]

    correct = 0
    total = len(cases)

    print("\nHITL Evaluation")
    print("=" * 60)

    for index, case in enumerate(cases, start=1):
        thread_id = f"hitl-evaluation-{index}"

        paused = graph.invoke(
            build_state(thread_id),
            config=build_config(thread_id),
        )

        pause_correct = (
            bool(paused.get("__interrupt__"))
            and paused["approval"] == {}
            and paused["incident"] == {}
        )

        result = graph.invoke(
            Command(
                resume={
                    "decision": case["decision"],
                }
            ),
            config=build_config(thread_id),
        )

        incident_correct = (
            result["incident"]["created"]
            == case["expected_created"]
            and result["incident"]["status"]
            == case["expected_status"]
        )

        is_correct = pause_correct and incident_correct

        if is_correct:
            correct += 1

        status = "PASS" if is_correct else "FAIL"

        print(f"\n[{status}]")
        print(f"Case          : {case['name']}")
        print(f"Decision      : {case['decision']}")
        print(f"Paused first  : {pause_correct}")
        print(f"Incident      : {result['incident']['status']}")

    accuracy = (correct / total) * 100 if total else 0

    print("\n" + "=" * 60)
    print(f"Correct : {correct}/{total}")
    print(f"HITL Evaluation Accuracy: {accuracy:.2f}%")
    print("=" * 60)

    return {
        "correct": correct,
        "total": total,
        "accuracy": accuracy,
    }


if __name__ == "__main__":
    evaluate_hitl()
