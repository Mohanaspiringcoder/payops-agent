import sqlite3
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver


CHECKPOINT_DATABASE_PATH = Path(
    "data/generated/payops_checkpoints.db"
)

CHECKPOINT_DATABASE_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)

_connection = sqlite3.connect(
    CHECKPOINT_DATABASE_PATH,
    check_same_thread=False,
)

checkpointer = SqliteSaver(_connection)
checkpointer.setup()
