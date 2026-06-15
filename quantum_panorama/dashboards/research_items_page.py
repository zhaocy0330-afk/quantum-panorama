from __future__ import annotations

import streamlit as st

from quantum_panorama.storage import database as db


def render() -> None:
    st.title("投研数据库")
    st.caption("展示已审核入库的 research_items，可导出 CSV / Excel / Markdown。")
    db.init_db()

    items = db.get_research_items()
    if items.empty:
        st.info("暂无已审核入库资料。请先在采集结果审核池批准记录。")
        return

    c1, c2, c3 = st.columns(3)
    category = c1.selectbox("分类", ["全部"] + sorted(items["category"].dropna().unique().tolist()))
    source = c2.selectbox("来源", ["全部"] + sorted(items["source_name"].dropna().unique().tolist()))
    min_importance = c3.slider("最低重要性", 1, 5, 1)
    keyword = st.text_input("关键词")

    filtered = db.get_research_items(category, source, keyword, min_importance)
    st.dataframe(filtered, use_container_width=True, hide_index=True)

    c4, c5, c6 = st.columns(3)
    c4.download_button("导出 CSV", filtered.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"), "research_items.csv", "text/csv", use_container_width=True)
    c5.download_button("导出 Excel", db.dataframe_to_excel_bytes(filtered), "research_items.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    c6.download_button("导出 Markdown", db.research_items_to_markdown(filtered).encode("utf-8"), "research_items.md", "text/markdown", use_container_width=True)

