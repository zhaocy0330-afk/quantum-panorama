from __future__ import annotations

import json

import pandas as pd

from .openai_client import chat_completion


REPORT_TEMPLATE = """# {title}

## 一、核心结论
用 3-5 条 bullet 总结。资料不足时必须写“现有资料不足，无法判断”。

## 二、本期重要事件
按重要性排序列出事件。

## 三、细分赛道动态
包括：量子计算、量子通信、量子传感、量子材料、政策监管、融资并购、公司动态、论文进展。

## 四、投资人视角分析
包括商业化进展、产业链影响、可关注方向、潜在标的类型、关键风险。不要输出股票买卖建议。

## 五、后续跟踪清单
生成 5-10 个后续应持续跟踪的问题。

## 六、资料来源
列出使用到的标题、来源和 URL。
"""


def dataframe_context(df: pd.DataFrame, max_items: int = 30) -> str:
    if df.empty:
        return "数据库中没有符合条件的已审核入库资料。"
    rows = []
    for _, row in df.head(max_items).iterrows():
        rows.append(
            {
                "title": row.get("title", ""),
                "url": row.get("url", ""),
                "source_name": row.get("source_name", ""),
                "published_at": row.get("published_at", ""),
                "category": row.get("category", ""),
                "importance": int(row.get("importance") or 1),
                "summary": row.get("summary", ""),
                "content_excerpt": row.get("content_excerpt", "")[:800],
            }
        )
    return json.dumps(rows, ensure_ascii=False, indent=2)


def build_report_prompt(report_type: str, title: str, df: pd.DataFrame, filters: str) -> str:
    return f"""
请基于下面数据库中已审核入库的资料，生成 Markdown 格式的“{report_type}”。

硬性要求：
1. 只基于资料 JSON，不允许编造事实。
2. 关键结论尽量引用来源 URL。
3. 资料不足时必须写“现有资料不足，无法判断”。
4. 不输出股票买卖建议。
5. 投资判断使用“可能、显示、值得跟踪、需要验证”等谨慎表述。
6. 面向投资经理、产业研究人员、量子科技项目尽调场景。
7. 保留资料来源列表。
8. 不要把未验证信息写成确定事实。

筛选条件：
{filters}

默认结构：
{REPORT_TEMPLATE.format(title=title)}

资料 JSON：
{dataframe_context(df)}
"""


def generate_report(report_type: str, title: str, df: pd.DataFrame, filters: str) -> tuple[str, str]:
    prompt = build_report_prompt(report_type, title, df, filters)
    return chat_completion(prompt)

