from __future__ import annotations

import re


def normalize_text(text: str | None) -> str:
    if not text:
        return ""
    text = re.sub(r"\s+", " ", str(text)).strip()
    return text


def split_tags(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in re.split(r"[;；,，/]", str(value)) if item.strip()]

