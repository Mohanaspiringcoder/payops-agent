import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


OUTPUT_PATH = Path("data/transactions.csv")

random.seed(42)

BANKS = ["SBI", "HDFC", "ICICI", "AXIS", "KOTAK", "PNB"]

MERCHANT_CATEGORIES = [
    "GROCERY",
    "FOOD",
    "E_COMMERCE",
    "TRAVEL",
    "UTILITIES",
    "ENTERTAINMENT",
]

PAYMENT_TYPES = [
    "P2P",
    "P2M",
]

CHANNELS = [
    "MOBILE",
    "QR",
    "WEB",
]

FAILURE_REASONS = [
    "TIMEOUT",
    "BANK_ERROR",
    "INSUFFICIENT_FUNDS",
    "TECHNICAL_ERROR",
]


def generate_transactions(count: int = 100) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    start_time = datetime(2026, 9, 1, 9, 0, 0)

    fieldnames = [
        "transaction_id",
        "timestamp",
        "amount",
        "sender_bank",
        "receiver_bank",
        "merchant_category",
        "payment_type",
        "status",
        "failure_reason",
        "channel",
        "response_time_ms",
    ]

    with OUTPUT_PATH.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(1, count + 1):
            timestamp = start_time + timedelta(
                minutes=random.randint(0, 30 * 24 * 60)
            )

            status = random.choices(
                ["SUCCESS", "FAILED"],
                weights=[85, 15],
                k=1,
            )[0]

            failure_reason = ""

            if status == "FAILED":
                failure_reason = random.choices(
                    FAILURE_REASONS,
                    weights=[40, 30, 20, 10],
                    k=1,
                )[0]

            response_time_ms = random.randint(150, 1800)

            if failure_reason == "TIMEOUT":
                response_time_ms = random.randint(1200, 3000)

            writer.writerow(
                {
                    "transaction_id": f"TXN{i:06d}",
                    "timestamp": timestamp.isoformat(),
                    "amount": round(random.uniform(50, 25000), 2),
                    "sender_bank": random.choice(BANKS),
                    "receiver_bank": random.choice(BANKS),
                    "merchant_category": random.choice(MERCHANT_CATEGORIES),
                    "payment_type": random.choice(PAYMENT_TYPES),
                    "status": status,
                    "failure_reason": failure_reason,
                    "channel": random.choice(CHANNELS),
                    "response_time_ms": response_time_ms,
                }
            )


if __name__ == "__main__":
    transaction_count = 100
    generate_transactions(transaction_count)
    print(f"Generated {transaction_count} synthetic transactions.")
