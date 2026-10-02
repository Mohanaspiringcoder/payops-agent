import re


def chunk_operational_document(document: str) -> list[dict[str, str]]:
    """Split the operational document into failure-code sections."""

    sections = re.split(r"\n(?=## )", document.strip())

    chunks = []

    for section in sections:
        section = section.strip()

        if not section or section.startswith("# UPI Payment Failure Code Reference"):
            continue

        heading = section.splitlines()[0].strip()

        if not heading.startswith("## "):
            continue

        failure_code = heading.replace("## ", "", 1).strip()

        chunks.append(
            {
                "failure_code": failure_code,
                "content": section,
            }
        )

    return chunks
