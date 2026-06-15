from __future__ import annotations

import streamlit as st

from quantum_panorama.database import read_table
from quantum_panorama.utils.llm_client import generate_research_report


REPORT_TYPES = [
    "市场全景报告",
    "技术路线分析报告",
    "企业画像报告",
    "专家访谈总结报告",
    "产业链分析报告",
    "投资机会与风险报告",
    "本团队产业化建议报告",
]


def contains_route(df, route: str):
    if not route or route == "全部" or df.empty or "tech_routes" not in df.columns:
        return df
    return df[df["tech_routes"].fillna("").str.contains(route, regex=False)]


def render() -> None:
    st.title("AI行研报告")
    orgs = read_table("organizations")
    experts = read_table("experts")
    interviews = read_table("interviews")
    routes = sorted(set(";".join(orgs["tech_routes"].fillna("")).split(";")) - {""})

    c1, c2, c3 = st.columns(3)
    market = c1.selectbox("市场方向", ["全部"] + sorted(orgs["market_segment"].dropna().unique().tolist()))
    route = c2.selectbox("技术路线", ["全部"] + routes)
    report_type = c3.selectbox("报告类型", REPORT_TYPES)
    info_types = st.multiselect("信息类型", ["论文", "专利", "融资", "政策", "企业", "专家", "访谈", "产业链"], default=["企业", "专家", "访谈"])
    date_range = st.text_input("时间范围", value="近三年")

    filtered_orgs = orgs if market == "全部" else orgs[orgs["market_segment"].isin([market, "综合"])]
    filtered_experts = experts if market == "全部" else experts[experts["market_segment"].isin([market, "综合"])]
    filtered_interviews = interviews if market == "全部" else interviews[interviews["market_segment"].isin([market, "综合"])]
    filtered_orgs = contains_route(filtered_orgs, route)
    filtered_experts = contains_route(filtered_experts, route)
    filtered_interviews = contains_route(filtered_interviews, route)

    st.caption(f"已选择：{market} / {route} / {', '.join(info_types)} / {date_range}")
    if st.button("生成报告（MVP占位）", type="primary"):
        report = generate_research_report(market, route, report_type, filtered_orgs, filtered_experts, filtered_interviews)
        st.session_state["generated_report"] = report

    report = st.session_state.get("generated_report", "")
    if report:
        st.markdown(report)
        st.download_button("导出 Markdown", report.encode("utf-8"), f"{report_type}.md", "text/markdown")
    else:
        st.info("第一版暂不调用真实大模型，已预留 llm_client.py。点击生成后会基于结构化数据产出 Markdown 报告框架。")
