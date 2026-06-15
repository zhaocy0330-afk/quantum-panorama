from __future__ import annotations

import plotly.express as px
import streamlit as st

from quantum_panorama.analyzers.tech_route_analyzer import route_heat
from quantum_panorama.database import read_table
from quantum_panorama.dashboards.common import card


def render() -> None:
    st.title("量子行业总览")
    st.caption("围绕市场方向、技术路线、上中下游主体、专家访谈和产业链关系沉淀行业认知。")

    orgs = read_table("organizations")
    experts = read_table("experts")
    interviews = read_table("interviews")
    papers = read_table("papers")
    patents = read_table("patents")
    financing = read_table("financing_events")
    policies = read_table("policies")

    cols = st.columns(6)
    metrics = [
        ("企业/主体", len(orgs)),
        ("专家", len(experts)),
        ("访谈", len(interviews)),
        ("论文", len(papers)),
        ("专利", len(patents)),
        ("融资事件", len(financing)),
    ]
    for col, (label, value) in zip(cols, metrics):
        col.metric(label, value)

    st.subheader("三大市场对比")
    market_counts = orgs["market_segment"].replace("综合", "量子市场总体").value_counts().reset_index()
    market_counts.columns = ["市场方向", "主体数量"]
    fig = px.bar(market_counts, x="市场方向", y="主体数量", color="市场方向", text="主体数量")
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.subheader("技术路线热度")
        heat = route_heat(orgs).reset_index()
        heat.columns = ["技术路线", "主体覆盖数"]
        st.plotly_chart(px.bar(heat, x="技术路线", y="主体覆盖数", color="技术路线"), use_container_width=True)
    with col2:
        st.subheader("产业链分层概览")
        for role in ["上游", "中游", "下游", "支撑机构"]:
            names = orgs.loc[orgs["industry_chain_role"].eq(role), "short_name"].fillna("").tolist()
            st.markdown(f"<div class='qp-stage'><b>{role}</b><br>{' / '.join(names) or '暂无'}</div>", unsafe_allow_html=True)

    st.subheader("最新沉淀")
    a, b, c, d = st.columns(4)
    with a:
        card("近期论文", papers.sort_values("publish_date", ascending=False).iloc[0]["title"], ["论文", papers.iloc[0]["tech_routes"]])
    with b:
        card("近期专利", patents.sort_values("application_date", ascending=False).iloc[0]["title"], ["专利", patents.iloc[0]["tech_routes"]])
    with c:
        card("近期融资", financing.sort_values("financing_date", ascending=False).iloc[0]["round"], ["融资", financing.iloc[0]["amount"]])
    with d:
        card("近期访谈", interviews.sort_values("interview_date", ascending=False).iloc[0]["title"], ["访谈", interviews.iloc[0]["verification_status"]])

    st.subheader("AI摘要")
    st.info(
        "MVP 摘要：当前样本显示，上游激光、真空、低温、测控电子学是多路线共性卡点；"
        "量子通信更接近项目制商业化，精密测量需要客户场景 ROI 验证，量子计算仍以科研客户和云平台为主。"
    )
    with st.expander("政策样本"):
        st.dataframe(policies, use_container_width=True)

