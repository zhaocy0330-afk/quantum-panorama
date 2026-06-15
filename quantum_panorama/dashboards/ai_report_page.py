from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import streamlit as st

from quantum_panorama.ai.item_summarizer import summarize_item
from quantum_panorama.ai.openai_client import DEFAULT_MODEL, has_api_key
from quantum_panorama.ai.report_generator import generate_report
from quantum_panorama.storage import database as db


REPORT_TYPES = ["量子行业日报", "量子行业周报", "量子行业月报", "赛道专题报告", "公司跟踪报告", "投资机会简报", "风险事件报告"]


def date_defaults(report_type: str) -> tuple[date, date]:
    today = date.today()
    if "日报" in report_type:
        return today - timedelta(days=1), today
    if "周报" in report_type:
        return today - timedelta(days=7), today
    if "月报" in report_type:
        return today - timedelta(days=30), today
    return today - timedelta(days=90), today


def render_report_tab() -> None:
    items_all = db.get_research_items()
    if items_all.empty:
        st.info("暂无已审核入库资料，无法生成研报。")
        return
    if not has_api_key():
        st.warning("未配置 AI Key，无法使用 AI研报生成。其他非 AI 功能照常可用。")

    report_type = st.selectbox("研报类型", REPORT_TYPES)
    start_default, end_default = date_defaults(report_type)
    c1, c2, c3 = st.columns(3)
    start = c1.date_input("开始日期", value=start_default)
    end = c2.date_input("结束日期", value=end_default)
    min_importance = c3.slider("最低重要性评分", 1, 5, 1)
    category = st.selectbox("分类", ["全部"] + sorted(items_all["category"].dropna().unique().tolist()))
    source = st.selectbox("来源", ["全部"] + sorted(items_all["source_name"].dropna().unique().tolist()))
    keyword = st.text_input("关键词")
    title = st.text_input("研报标题", value=f"{report_type} - {end.isoformat()}")

    data = db.get_research_items(category, source, keyword, min_importance, start.isoformat(), end.isoformat())
    st.caption(f"将使用 {len(data)} 条已审核入库资料。AI 只基于这些资料生成。")
    st.dataframe(data[["title", "category", "importance", "source_name", "url"]], use_container_width=True, hide_index=True)

    if st.button("生成 AI 研报", type="primary", disabled=not has_api_key(), use_container_width=True):
        if data.empty:
            st.warning("现有资料不足，无法判断。请扩大筛选范围或先入库资料。")
            return
        filters = f"category={category}; source={source}; keyword={keyword}; importance>={min_importance}; range={start}~{end}"
        with st.spinner("正在生成研报..."):
            try:
                content, model = generate_report(report_type, title, data, filters)
                report_id = db.save_ai_report(report_type, title, f"{start}~{end}", filters, content, model)
                st.success(f"研报已生成并保存，ID={report_id}。")
                st.markdown(content)
                st.download_button("下载 Markdown", content.encode("utf-8"), f"{title}.md", "text/markdown")
            except Exception as exc:
                st.error(f"AI 研报生成失败：{exc}")


def render_item_summary_tab() -> None:
    items = db.get_research_items()
    if items.empty:
        st.info("暂无已审核入库资料。")
        return
    if not has_api_key():
        st.warning("未配置 AI Key，无法生成单条 AI 摘要。")
    labels = items["id"].astype(str) + " | " + items["title"].astype(str).str.slice(0, 80)
    selected = st.multiselect("选择需要摘要的数据", labels.tolist())
    ids = [int(label.split(" | ")[0]) for label in selected]
    if st.button("批量生成摘要", type="primary", disabled=not has_api_key() or not ids):
        done = 0
        for item_id in ids:
            item_df = db.get_research_item(item_id)
            if item_df.empty:
                continue
            try:
                summary, _ = summarize_item(item_df.iloc[0])
                db.save_item_summary(item_id, summary)
                done += 1
            except Exception as exc:
                st.error(f"数据 {item_id} 摘要失败：{exc}")
        st.success(f"已生成 {done} 条摘要。")
    summaries = db.get_item_summaries()
    if summaries.empty:
        st.info("暂无 AI 摘要。")
    else:
        st.dataframe(summaries, use_container_width=True, hide_index=True)


def render_history_tab() -> None:
    reports = db.list_ai_reports()
    if reports.empty:
        st.info("暂无历史研报。")
        return
    st.dataframe(reports[["id", "report_type", "title", "time_range", "model_name", "created_at"]], use_container_width=True, hide_index=True)
    selected = st.selectbox("查看研报", reports["id"].astype(str) + " | " + reports["title"].astype(str))
    report_id = int(selected.split(" | ")[0])
    row = reports[reports["id"].eq(report_id)].iloc[0]
    st.markdown(row["content_markdown"])
    st.download_button("下载 Markdown", str(row["content_markdown"]).encode("utf-8"), f"{row['title']}.md", "text/markdown")


def render() -> None:
    st.title("AI研报生成中心")
    st.caption(f"当前默认模型：{DEFAULT_MODEL}。AI 只基于 research_items 中已审核入库资料生成，不输出股票买卖建议。")
    db.init_db()
    tabs = st.tabs(["生成研报", "单条数据 AI 摘要", "历史研报"])
    with tabs[0]:
        render_report_tab()
    with tabs[1]:
        render_item_summary_tab()
    with tabs[2]:
        render_history_tab()

