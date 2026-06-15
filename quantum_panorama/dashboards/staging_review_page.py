from __future__ import annotations

import pandas as pd
import streamlit as st

from quantum_panorama.storage import database as db


def selected_ids_from_editor(df: pd.DataFrame, key: str) -> list[int]:
    if df.empty:
        return []
    editable = df.copy()
    editable.insert(0, "选择", False)
    shown_cols = ["选择", "id", "title", "source_name", "category", "importance", "url", "fetched_at", "status", "matched_keywords"]
    edited = st.data_editor(
        editable[[col for col in shown_cols if col in editable.columns]],
        key=key,
        hide_index=True,
        use_container_width=True,
        disabled=[col for col in shown_cols if col != "选择"],
    )
    return edited.loc[edited["选择"], "id"].astype(int).tolist()


def render() -> None:
    st.title("采集结果审核池")
    st.caption("所有采集结果先进入 staging；批准后才写入正式投研数据库 research_items。")
    db.init_db()

    c1, c2, c3 = st.columns(3)
    status = c1.selectbox("状态", ["pending", "approved", "rejected", "全部"])
    staging = db.get_staging(status)
    category_options = ["全部"] + sorted(staging["category"].dropna().unique().tolist()) if not staging.empty else ["全部"]
    source_options = ["全部"] + sorted(staging["source_name"].dropna().unique().tolist()) if not staging.empty else ["全部"]
    category = c2.selectbox("分类", category_options)
    source = c3.selectbox("来源", source_options)
    keyword = st.text_input("关键词筛选")

    filtered = staging.copy()
    if category != "全部" and not filtered.empty:
        filtered = filtered[filtered["category"].eq(category)]
    if source != "全部" and not filtered.empty:
        filtered = filtered[filtered["source_name"].eq(source)]
    if keyword and not filtered.empty:
        mask = filtered.apply(lambda row: keyword.lower() in " ".join(map(str, row.values)).lower(), axis=1)
        filtered = filtered[mask]

    if filtered.empty:
        st.info("当前筛选条件下暂无 staging 记录。")
    else:
        selected_ids = selected_ids_from_editor(filtered, "staging_review_editor")
        a, b, c = st.columns(3)
        if a.button("批准入正式库", type="primary", use_container_width=True):
            try:
                result = db.approve_staging_records(selected_ids)
                st.success(f"已批准 {result['approved']} 条，跳过 {result['skipped']} 条。")
                st.rerun()
            except Exception as exc:
                st.error(f"批准失败：{exc}")
        if b.button("拒绝", use_container_width=True):
            count = db.reject_staging_records(selected_ids)
            st.warning(f"已拒绝 {count} 条。")
            st.rerun()
        if c.button("清空已拒绝", use_container_width=True):
            count = db.clear_rejected_staging()
            st.info(f"已清空 {count} 条已拒绝记录。")
            st.rerun()
        st.download_button(
            "导出 staging CSV",
            filtered.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
            "crawl_results_staging.csv",
            "text/csv",
        )

