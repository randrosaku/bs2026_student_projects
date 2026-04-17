from models import ObligationList
from huggingface_hub import InferenceClient
import json

import logging

logger = logging.getLogger(__name__)
client = InferenceClient()


def get_default_prompt() -> str:
    return """Extract all obligations from the following text. For each obligation return a JSON array with objects containing:
    - "actor": who is obligated
    - "action": what they must do  
    - "modality": the modal verb (must, shall, must not...)
    - "condition": any triggering or temporal condition (or empty string)
    - "span": the verbatim sentence from the text that contains the obligation
    - "rationale": a brief explanation of why this text is an obligation (or empty string if not clear)

    Return only the JSON array, no additional text.

    Text: {chunk}"""


def extract_obligations(chunk: str) -> list[dict]:
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": get_default_prompt(),
            },
            {
                "role": "user",
                "content": (
                    f"Extract all obligations from this text:\n\n{chunk}\n\n"
                    "Return ONLY valid JSON with key 'obligations'."
                ),
            },
        ],
    )

    text = completion.choices[0].message.content.strip()

    if text.startswith("```"):
        text = text.split("```")[1]
        text = text.replace("json", "", 1).strip()

    data = json.loads(text)
    result = ObligationList(**data)
    return [o.model_dump() for o in result.obligations]
