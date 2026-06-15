from __future__ import annotations

import streamlit as st

from quantum_panorama.collectors.source_registry import DEFAULT_RESEARCH_SOURCES
from quantum_panorama.storage import database as db


def render() -> None:
    st.title("数据源管理")
    st.caption("配置低频、合规的数据源。支持 RSS、网页列表页和单 URL，不绕过登录、验证码或付费墙。")
    db.init_db()

    with st.expander("新增数据源", expanded=True):
        with st.form("add_data_source_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("名称")
            source_type = c2.selectbox("类型", ["rss", "web_list", "single_url"])
            url = st.text_input("URL")
            keywords = st.text_input("关键词", placeholder="quantum, qubit, 融资, 政策")
            category_hint = st.selectbox(
                "类别提示",
                ["", "量子计算", "量子通信", "量子传感", "量子材料", "政策监管", "融资并购", "公司动态", "论文进展", "产业链", "风险事件", "未分类"],
            )
            c3, c4 = st.columns(2)
            enabled = c3.checkbox("启用", value=True)
            interval = c4.number_input("采集间隔小时", min_value=1, max_value=720, value=24)
            submitted = st.form_submit_button("添加数据源", type="primary")
        if submitted:
            if not name.strip() or not url.strip():
                st.warning("名称和 URL 必填。")
            else:
                try:
                    db.add_data_source(name, source_type, url, keywords, category_hint, int(enabled), int(interval))
                    st.success("已添加数据源。")
                    st.rerun()
                except Exception as exc:
                    st.error(f"添加失败：{exc}")

    c1, c2 = st.columns(2)
    if c1.button("一键添加默认数据源", use_container_width=True):
        try:
            added = db.add_default_sources(DEFAULT_RESEARCH_SOURCES)
            st.success(f"已添加 {added} 个默认数据源，已存在的不会重复添加。")
            st.rerun()
        except Exception as exc:
            st.error(f"添加默认数据源失败：{exc}")

    sources = db.get_data_sources()
    if sources.empty:
        st.info("暂无数据源。可以先点击“一键添加默认数据源”。")
        return

    st.subheader("当前数据源")
    st.dataframe(sources, use_container_width=True, hide_index=True)

    with st.expander("启用 / 停用 / 删除"):
        selected = st.selectbox("选择数据源", sources["id"].astype(str) + " | " + sources["name"].astype(str))
        source_id = int(selected.split(" | ")[0])
        col_a, col_b, col_c = st.columns(3)
        if col_a.button("启用", use_container_width=True):
            db.set_data_source_enabled(source_id, 1)
            st.success("已启用。")
            st.rerun()
        if col_b.button("停用", use_container_width=True):
            db.set_data_source_enabled(source_id, 0)
            st.info("已停用。")
            st.rerun()
        if col_c.button("删除", use_container_width=True):
            db.delete_data_source(source_id)
            st.warning("已删除。")
            st.rerun()

