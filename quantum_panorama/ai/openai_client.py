from __future__ import annotations

import os


DEFAULT_MODEL = "gpt-4.1-mini"


def get_api_key() -> str:
    try:
        import streamlit as st

        value = st.secrets.get("OPENAI_API_KEY")
        if value:
            return str(value)
    except Exception:
        pass
    return os.getenv("OPENAI_API_KEY", "")


def has_api_key() -> bool:
    return bool(get_api_key())


def chat_completion(prompt: str, model: str = DEFAULT_MODEL, temperature: float = 0.2) -> tuple[str, str]:
    api_key = get_api_key()
    if not api_key:
        raise RuntimeError("未配置 AI Key，无法使用 AI研报生成。")
    from openai import OpenAI

    client = OpenAI(api_key=api_key, timeout=60)
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {
                "role": "system",
                "content": "你是谨慎的量子科技产业研究助手。只能基于用户提供的数据库资料分析，不得编造事实，不输出股票买卖建议。",
            },
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content or "", model

