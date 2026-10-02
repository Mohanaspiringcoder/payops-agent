import csv

from app.database.database import get_connection


CSV_PATH = "data/transactions.csv"


def load_transactions() -> None:
	connection = get_connection()

try:
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            timestamp TEXT,
            amount REAL,
            sender_bank TEXT,
            receiver_bank TEXT,
            merchant_category TEXT,
            payment_type TEXT,
            status TEXT,
            failure_reason TEXT,
            channel TEXT,
            response_time_ms INTEGER
        )
        """
    )

    with open(CSV_PATH, "r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            cursor.execute(
                """
                INSERT OR REPLACE INTO transactions (
                    transaction_id,
                    timestamp,
                    amount,
                    sender_bank,
                    receiver_bank,
                    merchant_category,
                    payment_type,
                    status,
                    failure_reason,
                    channel,
                    response_time_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["transaction_id"],
                    row["timestamp"],
                    float(row["amount"]),
                    row["sender_bank"],
                    row["receiver_bank"],
                    row["merchant_category"],
                    row["payment_type"],
                    row["status"],
                    row["failure_reason"],
                    row["channel"],
                    int(row["response_time_ms"]),
                ),
            )

    connection.commit()

finally:
    connection.close()


if __name__ == "__main__":
    load_transactions()
    print("Transactions loaded successfully.")
