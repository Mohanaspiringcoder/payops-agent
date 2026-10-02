import statistics
import time

from app.graph.investigation_graph import graph as investigation_graph


QUESTION = "Investigate why payments are failing"
RUNS = 3


def run_investigation() -> float:
    start = time.perf_counter()

    investigation_graph.invoke(
        {
            "question": QUESTION,
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
    )

    end = time.perf_counter()

    return end - start


def evaluate_latency() -> dict:
    latencies = []

    print("\nEnd-to-End Latency Evaluation")
    print("=" * 60)
    print(f"Runs: {RUNS}")

    for run_number in range(1, RUNS + 1):
        latency = run_investigation()
        latencies.append(latency)

        print(f"Run {run_number}: {latency:.2f} seconds")

    average_latency = statistics.mean(latencies)
    minimum_latency = min(latencies)
    maximum_latency = max(latencies)

    print("\n" + "=" * 60)
    print(f"Average latency: {average_latency:.2f} seconds")
    print(f"Minimum latency: {minimum_latency:.2f} seconds")
    print(f"Maximum latency: {maximum_latency:.2f} seconds")
    print("=" * 60)

    return {
        "runs": RUNS,
        "average_seconds": round(average_latency, 2),
        "minimum_seconds": round(minimum_latency, 2),
        "maximum_seconds": round(maximum_latency, 2),
    }


if __name__ == "__main__":
    evaluate_latency()
