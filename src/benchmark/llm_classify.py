import os
import time
import json
import re
import hashlib
from pathlib import Path
from google import genai
from google.genai import types
from groq import Groq

from src.utils.config import LABEL_COLUMNS, DOCS_DIR
from src.utils.logger import get_logger

logger = get_logger(__name__)

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# gemini-3.6-flash ka free tier quota sirf 20/day hai — gemini-2.0-flash ka
# quota kaafi zyada hai (250+/day range), isliye default yahi rakha hai.
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.6-27b")

CACHE_DIR = Path(DOCS_DIR) / "llm_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

PROMPT_TEMPLATE = """Classify the following comment for each category below. Respond with ONLY a JSON object mapping each category to 0 or 1.

Categories: {labels}

Comment: "{text}"

JSON:"""


def text_hash(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def load_cache(name):
    path = CACHE_DIR / f"{name}_cache.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def save_cache(name, cache):
    path = CACHE_DIR / f"{name}_cache.json"
    with open(path, "w") as f:
        json.dump(cache, f)


def _parse_response(raw_text):
    if not raw_text:
        return [0] * len(LABEL_COLUMNS)
    try:
        cleaned = re.sub(
            r"^```(?:json)?\s*|\s*```$", "", raw_text.strip(), flags=re.MULTILINE
        )
        match = re.search(r"\{[^{}]*\}", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(0)
        parsed = json.loads(cleaned)
        return [int(parsed.get(label, 0)) for label in LABEL_COLUMNS]
    except Exception as e:
        logger.warning(
            f"Failed to parse LLM response: {raw_text[:100] if raw_text else 'EMPTY'} | {e}"
        )
        return [0] * len(LABEL_COLUMNS)


def classify_gemini(text):
    prompt = PROMPT_TEMPLATE.format(labels=", ".join(LABEL_COLUMNS), text=text)
    start = time.time()

    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    latency = time.time() - start
    raw_text = response.text if hasattr(response, "text") and response.text else ""
    return _parse_response(raw_text), latency, 0.0


def classify_groq(text):
    groq_prompt = f"""Classify this comment into categories (1 for Yes, 0 for No).

Categories: {", ".join(LABEL_COLUMNS)}
Comment: "{text}"

Respond with ONLY the JSON object below, filled in, and nothing else:
{{"toxic":0,"severe_toxic":0,"obscene":0,"threat":0,"insult":0,"identity_hate":0}}"""

    start = time.time()

    kwargs = dict(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You output only a single JSON object matching the exact schema given. No explanation, no markdown, no extra text.",
            },
            {"role": "user", "content": groq_prompt},
        ],
        max_tokens=500,
        temperature=0.0,
    )

    if "gpt-oss" in GROQ_MODEL:
        kwargs["reasoning_effort"] = "low"

    response = groq_client.chat.completions.create(**kwargs)
    latency = time.time() - start
    raw_text = response.choices[0].message.content if response.choices else ""
    return _parse_response(raw_text), latency, 0.0
