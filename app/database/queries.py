from app.database.database import get_connection


def get_transaction_count() -> int:
    connection = get_connection()

    try:
        result = connection.execute(
            "SELECT COUNT(*) AS count FROM transactions"
        ).fetchone()

        return result["count"]
    finally:
        connection.close()


def get_success_rate() -> dict:
    connection = get_connection()

    try:
        result = connection.execute(
            """
            SELECT
                COUNT(*) AS total_transactions,
                SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END)
                    AS successful_transactions
            FROM transactions
            """
        ).fetchone()

        total = result["total_transactions"]
        successful = result["successful_transactions"] or 0

        success_rate = (
            (successful / total) * 100
            if total > 0
            else 0.0
        )

        return {
            "total_transactions": total,
            "successful_transactions": successful,
            "success_rate": round(success_rate, 2),
        }
    finally:
        connection.close()


def get_failure_summary() -> dict:
    connection = get_connection()

    try:
        total_failed = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM transactions
            WHERE status = 'FAILED'
            """
        ).fetchone()["count"]

        rows = connection.execute(
            """
            SELECT failure_reason, COUNT(*) AS count
            FROM transactions
            WHERE status = 'FAILED'
            GROUP BY failure_reason
            ORDER BY count DESC
            """
        ).fetchall()

        failure_reasons = {
            row["failure_reason"]: row["count"]
            for row in rows
        }

        return {
            "total_failed": total_failed,
            "failure_reasons": failure_reasons,
        }
    finally:
        connection.close()


def get_bank_failure_summary() -> dict:
    connection = get_connection()

    try:
        sender_rows = connection.execute(
            """
            SELECT sender_bank, COUNT(*) AS count
            FROM transactions
            WHERE status = 'FAILED'
            GROUP BY sender_bank
            ORDER BY count DESC
            """
        ).fetchall()

        receiver_rows = connection.execute(
            """
            SELECT receiver_bank, COUNT(*) AS count
            FROM transactions
            WHERE status = 'FAILED'
            GROUP BY receiver_bank
            ORDER BY count DESC
            """
        ).fetchall()

        return {
            "failed_by_sender_bank": {
                row["sender_bank"]: row["count"]
                for row in sender_rows
            },
            "failed_by_receiver_bank": {
                row["receiver_bank"]: row["count"]
                for row in receiver_rows
            },
        }
    finally:
        connection.close()
