from __future__ import annotations

import json

import pandas as pd

from .openai_client import chat_completion


def build_summary_prompt(item: pd.Series) -> str:
    data = {
        "title": item.get("title", ""),
        "url": item.get("url", ""),
        "source_name": item.get("source_name", ""),
        "category": item.get("category", ""),
        "summary": item.get("summary", ""),
        "content_excerpt": item.get("content_excerpt", "")[:1200],
    }
    return f"""
请只基于以下单条数据库资料，生成结构化 JSON。不得补充资料之外的事实。

字段：
- one_sentence_summary
- key_entities
- industry_segment
- impact_analysis
- risk_flags
- confidence_level

若资料不足，请在相应字段写“现有资料不足，无法判断”。

资料：
{json.dumps(data, ensure_ascii=False, indent=2)}
"""


def summarize_item(item: pd.Series) -> tuple[dict, str]:
    content, model = chat_completion(build_summary_prompt(item), temperature=0.1)
    try:
        parsed = json.loads(content)
    except Exception:
        parsed = {
            "one_sentence_summary": content.strip(),
            "key_entities": "现有资料不足，无法判断",
            "industry_segment": item.get("category", ""),
            "impact_analysis": "现有资料不足，无法判断",
            "risk_flags": "现有资料不足，无法判断",
            "confidence_level": "低",
        }
    return parsed, model

