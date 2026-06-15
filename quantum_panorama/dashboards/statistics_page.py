from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from quantum_panorama.analyzers.tech_route_analyzer import route_heat
from quantum_panorama.database import read_table


def dated_counts(df: pd.DataFrame, date_col: str, label: str) -> pd.DataFrame:
    if df.empty or date_col not in df.columns:
        return pd.DataFrame({"year": [], label: []})
    return df.assign(year=df[date_col].fillna("").str[:4]).groupby("year").size().reset_index(name=label)


def render() -> None:
    st.title("统计看板")
    orgs = read_table("organizations")
    experts = read_table("experts")
    interviews = read_table("interviews")
    papers = read_table("papers")
    patents = read_table("patents")
    financing = read_table("financing_events")
    policies = read_table("policies")

    st.subheader("行业基础指标")
    cols = st.columns(5)
    for col, (label, value) in zip(cols, [("论文数量", len(papers)), ("专利数量", len(patents)), ("融资案例数", len(financing)), ("政策数量", len(policies)), ("访谈数量", len(interviews))]):
        col.metric(label, value)

    st.subheader("趋势图")
    c1, c2, c3, c4 = st.columns(4)
    c1.plotly_chart(px.line(dated_counts(papers, "publish_date", "论文数"), x="year", y="论文数", markers=True), use_container_width=True)
    c2.plotly_chart(px.line(dated_counts(patents, "application_date", "专利数"), x="year", y="专利数", markers=True), use_container_width=True)
    c3.plotly_chart(px.line(dated_counts(financing, "financing_date", "融资案例数"), x="year", y="融资案例数", markers=True), use_container_width=True)
    c4.plotly_chart(px.line(dated_counts(policies, "publish_date", "政策数"), x="year", y="政策数", markers=True), use_container_width=True)

    st.subheader("企业、专家、访谈覆盖")
    a, b, c = st.columns(3)
    a.plotly_chart(px.pie(orgs, names="organization_type", title="企业/主体类型分布"), use_container_width=True)
    b.plotly_chart(px.pie(experts, names="market_segment", title="专家市场方向分布"), use_container_width=True)
    c.plotly_chart(px.pie(interviews, names="verification_status", title="访谈验证状态"), use_container_width=True)

    st.subheader("产业链和技术路线")
    d, e = st.columns(2)
    d.plotly_chart(px.bar(orgs["industry_chain_role"].value_counts().reset_index(), x="industry_chain_role", y="count", color="industry_chain_role", title="上游/中游/下游主体数量"), use_container_width=True)
    heat = route_heat(orgs).reset_index()
    heat.columns = ["技术路线", "热度"]
    e.plotly_chart(px.bar(heat, x="技术路线", y="热度", color="技术路线", title="技术路线热度排名"), use_container_width=True)

    st.subheader("市场成熟度评分模型（MVP预留）")
    score = pd.DataFrame(
        [
            {"维度": "技术成熟度", "分数": 65},
            {"维度": "工程化难度", "分数": 45},
            {"维度": "商业化确定性", "分数": 55},
            {"维度": "论文活跃度", "分数": 70},
            {"维度": "专利活跃度", "分数": 58},
            {"维度": "融资热度", "分数": 62},
            {"维度": "政策支持", "分数": 75},
            {"维度": "产业链完整度", "分数": 52},
            {"维度": "下游需求强度", "分数": 50},
            {"维度": "与本团队相关性", "分数": 68},
        ]
    )
    st.plotly_chart(px.line_polar(score, r="分数", theta="维度", line_close=True), use_container_width=True)

