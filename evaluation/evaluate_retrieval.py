import json
from pathlib import Path

from app.rag.retriever import OperationalKnowledgeRetriever


CASES_PATH = Path("evaluation/retrieval_cases.json")


def load_cases() -> list[dict]:
    with CASES_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def result_contains_failure_code(result: dict, failure_code: str) -> bool:
    return result.get("failure_code", "").upper() == failure_code.upper()


def evaluate_retrieval(top_k: int = 2) -> dict:
    cases = load_cases()
    retriever = OperationalKnowledgeRetriever()

    hits = 0
    total = len(cases)

    print("\nRetrieval Recall@K Evaluation")
    print("=" * 60)
    print(f"K = {top_k}")

    for case in cases:
        question = case["question"]
        expected_failure_code = case["expected_failure_code"]

        results = retriever.retrieve(
            question=question,
            top_k=top_k,
        )

        found = any(
            result_contains_failure_code(result, expected_failure_code)
            for result in results
        )

        if found:
            hits += 1

        status = "PASS" if found else "FAIL"

        print(f"\n[{status}]")
        print(f"Question : {question}")
        print(f"Expected : {expected_failure_code}")
        print(f"Retrieved: {len(results)} result(s)")

        for index, result in enumerate(results, start=1):
            failure_code = result.get("failure_code", "UNKNOWN")
            distance = result.get("distance")

            if distance is not None:
                print(
                    f"  {index}. "
                    f"{failure_code} "
                    f"(distance={distance:.4f})"
                )
            else:
                print(
                    f"  {index}. "
                    f"{failure_code}"
                )

    recall = hits / total if total else 0

    print("\n" + "=" * 60)
    print(f"Hits    : {hits}/{total}")
    print(f"Recall@{top_k}: {recall:.2%}")
    print("=" * 60)

    return {
        "hits": hits,
        "total": total,
        "recall": recall * 100,
        "k": top_k,
    }


if __name__ == "__main__":
    evaluate_retrieval(top_k=2)
