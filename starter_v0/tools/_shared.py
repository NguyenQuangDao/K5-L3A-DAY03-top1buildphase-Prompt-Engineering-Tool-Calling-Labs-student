from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
TIMEOUT = 30
USER_AGENT = "AI20k-Day03-Research-Agent/1.0 (educational lab)"


def err(tool: str, exc: Exception) -> dict[str, Any]:
    return {"tool": tool, "error": type(exc).__name__, "message": str(exc)}


def clamp_int(value: Any, default: int, low: int, high: int) -> int:
    """Coerce a model-supplied number (5, "5", None, "abc", -1) into [low, high]."""
    if isinstance(value, bool):
        return default
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return max(low, min(high, number))


def pick_enum(value: Any, allowed: list[str], default: str) -> str:
    """Case-insensitive enum match; anything outside the enum falls back to `default`."""
    if isinstance(value, str):
        folded = value.strip().lower()
        for option in allowed:
            if option.lower() == folded:
                return option
    return default


def domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""


def fold_text(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.lower())
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


def terms(text: str) -> set[str]:
    stopwords = {
        "a", "an", "and", "are", "as", "at", "by", "for", "from", "in", "is", "of", "on", "or", "the", "to",
        "ban", "bao", "can", "cho", "co", "cua", "duoc", "gi", "giup", "la", "lam", "minh", "mot", "nay",
        "nen", "the", "thi", "trong", "va", "ve", "voi",
    }
    folded = fold_text(text)
    return {term for term in re.findall(r"[a-z0-9]+", folded) if len(term) > 1 and term not in stopwords}

