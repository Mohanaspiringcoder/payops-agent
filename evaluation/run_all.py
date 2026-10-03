import json
from pathlib import Path

from evaluation.evaluate_groundedness import evaluate_groundedness
from evaluation.evaluate_intent import evaluate_intent_selection
from evaluation.evaluate_recovery import evaluate_recovery
from evaluation.evaluate_retrieval import evaluate_retrieval
from evaluation.evaluate_task_completion import evaluate_task_completion
from evaluation.evaluate_hitl import evaluate_hitl

RESULTS_PATH = Path("evaluation/results/latest_results.json")


def run_all_evaluations() -> dict:
    print("\n" + "=" * 70)
    print("PAYOPS AGENT - FUNCTIONAL EVALUATION SUITE")
    print("=" * 70)

    intent_result = evaluate_intent_selection()
    retrieval_result = evaluate_retrieval(top_k=2)
    groundedness_result = evaluate_groundedness()
    task_completion_result = evaluate_task_completion()
    recovery_result = evaluate_recovery()
    hitl_result = evaluate_hitl()

    results = {
        "functional": {
            "intent_selection": intent_result,
            "retrieval_recall_at_2": retrieval_result,
            "groundedness": groundedness_result,
            "task_completion": task_completion_result,
            "failure_recovery": recovery_result,
            "hitl": hitl_result,
        },
        "performance": {
            "latency": {
                "note": (
                    "Run independently with "
                    "python -m evaluation.evaluate_latency"
                )
            }
        },
    }

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with RESULTS_PATH.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)

    print("\n" + "=" * 70)
    print("FUNCTIONAL EVALUATION SUMMARY")
    print("=" * 70)

    print(
        f"Intent Selection Accuracy : "
        f"{intent_result['accuracy']:.2f}%"
    )

    print(
        f"Retrieval Recall@2       : "
        f"{retrieval_result['recall']:.2f}%"
    )

    print(
        f"Groundedness Accuracy    : "
        f"{groundedness_result['accuracy']:.2f}%"
    )

    print(
        f"Task Completion Rate     : "
        f"{task_completion_result['completion_rate']:.2f}%"
    )

    print(
        f"Failure Recovery Accuracy: "
        f"{recovery_result['accuracy']:.2f}%"
    )
    print(
            f"HITL Evaluation Accuracy  : "
            f"{hitl_result['accuracy']:.2f}%"
    )

    print("=" * 70)
    print(f"\nResults saved to: {RESULTS_PATH}")
    print(
        "\nLatency is benchmarked separately with:"
        "\npython -m evaluation.evaluate_latency"
    )

    return results


if __name__ == "__main__":
    run_all_evaluations()
