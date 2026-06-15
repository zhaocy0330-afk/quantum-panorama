from __future__ import annotations

from io import BytesIO
from typing import Any

import pandas as pd
import streamlit as st

from quantum_panorama.config import (
    CHAIN_ROLES,
    CREDIBILITY_LEVELS,
    INFO_TYPES,
    MARKET_SEGMENTS,
    ORGANIZATION_TYPES,
    PRIORITIES,
    TRACKING_STATUS,
    VERIFICATION_STATUS,
)
from quantum_panorama.database import append_dataframe, delete_row, insert_row, update_row
from quantum_panorama.models import CRUD_FIELDS
from quantum_panorama.utils.importer import read_uploaded_table


SELECT_OPTIONS = {
    "organization_type": ORGANIZATION_TYPES,
    "industry_chain_role": CHAIN_ROLES,
    "market_segment": MARKET_SEGMENTS,
    "credibility": CREDIBILITY_LEVELS,
    "verification_status": VERIFICATION_STATUS,
    "information_type": INFO_TYPES,
    "investment_priority": PRIORITIES,
    "cooperation_priority": PRIORITIES,
    "tracking_status": TRACKING_STATUS,
    "interview_value": ["高", "中", "低"],
    "relevance_to_our_team": ["高", "中", "低"],
    "sensitivity": ["公开", "内部", "保密"],
    "interviewee_type": ["专家", "企业", "客户", "供应商", "投资机构", "政府部门", "科研院所"],
    "relationship_type": ["供应关系", "客户关系", "合作关系", "竞品关系", "投资关系", "孵化关系", "技术授权关系", "联合实验室关系", "示范项目关系", "顾问关系"],
    "status": ["未开始", "进行中", "已完成", "延期", "放弃"],
}


def filter_by_sidebar(df: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    filtered = df.copy()
    for key in keys:
        if key in filtered.columns and filtered[key].notna().any():
            values = sorted([str(v) for v in filtered[key].dropna().unique() if str(v)])
            selected = st.multiselect(key, values, key=f"filter_{key}_{hash(tuple(values))}")
            if selected:
                filtered = filtered[filtered[key].astype(str).isin(selected)]
    return filtered


def download_buttons(df: pd.DataFrame, name: str) -> None:
    csv = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=name[:31])
    col1, col2 = st.columns(2)
    col1.download_button("导出 CSV", csv, f"{name}.csv", "text/csv", use_container_width=True)
    col2.download_button(
        "导出 Excel",
        excel_buffer.getvalue(),
        f"{name}.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )


def import_panel(table_name: str) -> None:
    uploaded = st.file_uploader("导入 CSV/Excel", type=["csv", "xlsx"], key=f"upload_{table_name}")
    if uploaded is not None:
        df = read_uploaded_table(uploaded)
        st.dataframe(df, use_container_width=True)
        if st.button("确认导入", key=f"confirm_import_{table_name}"):
            count = append_dataframe(table_name, df)
            st.success(f"已导入 {count} 条记录")
            st.rerun()


def value_from_row(row: pd.Series | None, field: str) -> str:
    if row is None or field not in row:
        return ""
    value = row.get(field, "")
    return "" if pd.isna(value) else str(value)


def field_input(field: str, current: str = "") -> Any:
    if field in SELECT_OPTIONS:
        options = SELECT_OPTIONS[field]
        index = options.index(current) if current in options else 0
        return st.selectbox(field, options, index=index)
    if field.endswith("_date") or field in {"due_date", "latest_financing_date", "founded_year"}:
        return st.text_input(field, value=current, placeholder="YYYY-MM-DD 或年份")
    if field in {
        "notes",
        "raw_notes",
        "key_points",
        "verifiable_facts",
        "subjective_judgments",
        "important_conclusions",
        "risks",
        "follow_up_actions",
        "advantages",
        "risk_notes",
        "key_views",
        "products_services",
        "question_to_verify",
        "description",
    }:
        return st.text_area(field, value=current, height=100)
    return st.text_input(field, value=current)


def crud_panel(table_name: str, title: str) -> None:
    fields = CRUD_FIELDS[table_name]
    st.subheader(f"{title}维护")
    mode = st.radio("操作", ["新增", "编辑", "删除"], horizontal=True, key=f"mode_{table_name}")

    from quantum_panorama.database import read_table

    df = read_table(table_name)
    selected_row = None
    selected_id = None
    if mode in {"编辑", "删除"}:
        if df.empty:
            st.warning("暂无可操作记录")
            return
        labels = [f"{int(row.id)} | {row.get('name', row.get('title', row.get('task_title', '记录')))}" for _, row in df.iterrows()]
        selected = st.selectbox("选择记录", labels, key=f"select_{table_name}")
        selected_id = int(selected.split(" | ")[0])
        selected_row = df[df["id"] == selected_id].iloc[0]

    if mode == "删除":
        st.warning("删除后不可恢复，请确认这是测试或确定要移除的数据。")
        if st.button("确认删除", type="primary", key=f"delete_{table_name}"):
            delete_row(table_name, selected_id)
            st.success("已删除")
            st.rerun()
        return

    with st.form(f"form_{table_name}_{mode}"):
        payload = {}
        for idx in range(0, len(fields), 2):
            cols = st.columns(2)
            for col, field in zip(cols, fields[idx : idx + 2]):
                with col:
                    payload[field] = field_input(field, value_from_row(selected_row, field))
        submitted = st.form_submit_button("保存", type="primary")
    if submitted:
        if mode == "新增":
            insert_row(table_name, payload)
            st.success("已新增")
        else:
            update_row(table_name, selected_id, payload)
            st.success("已更新")
        st.rerun()


def card(title: str, body: str, tags: list[str] | None = None) -> None:
    tag_html = "".join(f"<span class='qp-tag'>{tag}</span>" for tag in tags or [] if tag)
    st.markdown(
        f"""
        <div class="qp-card">
            <h4>{title}</h4>
            <div class="qp-muted">{body}</div>
            <div style="margin-top:10px;">{tag_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

