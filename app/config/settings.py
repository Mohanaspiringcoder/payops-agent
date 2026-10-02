import os

from dotenv import load_dotenv


load_dotenv()


LLM_MODEL = os.getenv(
    "PAYOPS_LLM_MODEL",
    "qwen2.5:1.5b",
)

LLM_TEMPERATURE = float(
    os.getenv(
        "PAYOPS_LLM_TEMPERATURE",
        "0",
    )
)
