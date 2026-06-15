from __future__ import annotations

import streamlit as st

from quantum_panorama.database import read_table
from quantum_panorama.dashboards.common import crud_panel, download_buttons, filter_by_sidebar, import_panel
from quantum_panorama.utils.llm_client import summarize_interview


def render() -> None:
    st.title("访谈纪要库")
    df = read_table("interviews")
    tabs = st.tabs(["访谈清单", "访谈摘要卡片", "AI提取入口", "新增/编辑/删除", "导入导出"])
    with tabs[0]:
        filtered = filter_by_sidebar(df, ["market_segment", "tech_routes", "interviewee_type", "credibility", "verification_status"])
        st.dataframe(filtered, use_container_width=True, hide_index=True)
    with tabs[1]:
        selected = st.selectbox("选择访谈", df["title"].tolist())
        row = df[df["title"].eq(selected)].iloc[0]
        st.markdown(f"### {row['title']}")
        cols = st.columns(4)
        cols[0].metric("对象", row["interviewee"])
        cols[1].metric("类型", row["interviewee_type"])
        cols[2].metric("可信度", row["credibility"])
        cols[3].metric("验证状态", row["verification_status"])
        st.info(f"核心观点：{row['key_points']}")
        st.write(f"**可验证信息**：{row['verifiable_facts']}")
        st.write(f"**主观判断**：{row['subjective_judgments']}")
        st.warning(f"风险提示：{row['risks']}")
        st.success(f"后续动作：{row['follow_up_actions']}")
    with tabs[2]:
        raw = st.text_area("粘贴访谈纪要", height=220)
        if st.button("AI提取访谈摘要（占位）"):
            result = summarize_interview(raw)
            st.json(result)
            st.caption("后续接入 LLM 后，将自动建议更新企业库、专家库和产业链网络。")
    with tabs[3]:
        crud_panel("interviews", "访谈")
    with tabs[4]:
        import_panel("interviews")
        download_buttons(df, "interviews")

