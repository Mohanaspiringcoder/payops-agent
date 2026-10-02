from pathlib import Path


DOCUMENT_PATH = Path("data/documents/failure_code_reference.md")


def load_operational_document() -> str:
    """Load the operational knowledge document as text."""
    if not DOCUMENT_PATH.exists():
        raise FileNotFoundError(
            f"Operational document not found: {DOCUMENT_PATH}"
        )

    return DOCUMENT_PATH.read_text(encoding="utf-8")
