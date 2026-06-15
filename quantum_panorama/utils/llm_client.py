from __future__ import annotations

import pandas as pd


def summarize_interview(raw_notes: str) -> dict[str, str]:
    """Placeholder for future LLM extraction."""
    if not raw_notes:
        return {"summary": "", "facts": "", "judgments": "", "actions": ""}
    head = raw_notes[:180]
    return {
        "summary": f"自动摘要占位：{head}",
        "facts": "待接入 LLM 后抽取可验证事实。",
        "judgments": "待接入 LLM 后区分判断、推测和观点。",
        "actions": "建议人工确认后同步企业库、专家库和产业链关系。",
    }


def generate_research_report(
    market_segment: str,
    tech_route: str,
    report_type: str,
    organizations: pd.DataFrame,
    experts: pd.DataFrame,
    interviews: pd.DataFrame,
) -> str:
    """Deterministic MVP report generator; replace internals with model calls later."""
    org_count = len(organizations)
    expert_count = len(experts)
    interview_count = len(interviews)
    key_orgs = "、".join(organizations["name"].head(5).astype(str).tolist()) if not organizations.empty else "暂无"
    key_experts = "、".join(experts["name"].head(5).astype(str).tolist()) if not experts.empty else "暂无"
    key_points = "\n".join(f"- {v}" for v in interviews.get("key_points", pd.Series(dtype=str)).dropna().head(5))
    key_points = key_points or "- 暂无访谈观点"
    return f"""# {report_type}

## 一、市场概述
选择范围：{market_segment or "全部市场"} / {tech_route or "全部技术路线"}。当前样本包含 {org_count} 个主体、{expert_count} 位专家、{interview_count} 条访谈。

## 二、技术路线分析
该部分已预留 LLM 分析入口。MVP 根据结构化字段展示技术原理、核心部件、工程化难点和商业化路径。

## 三、前沿研究进展
后续可接入 arXiv、OpenAlex 与论文打标管线，形成论文趋势、热点关键词和机构活跃度。

## 四、专利与知识产权
后续可接入专利 API，分析申请人排名、授权率、技术路线专利壁垒。

## 五、融资与竞争格局
重点主体：{key_orgs}。

## 六、政策与区域机会
政策数据表已预留区域、发布机构、支持方向和与本团队相关性字段。

## 七、上游核心零部件分析
重点看国产替代成熟度、卡脖子程度、供应能力和交付周期。

## 八、整机/整体解决方案企业分析
重点看核心自研环节、外采核心部件、交付案例、订单和收入质量。

## 九、下游客户与应用场景分析
重点验证真实需求强度、付费意愿、采购周期和示范项目效果。

## 十、产业链网络与关键卡点
产业链网络模块已支持供应、客户、合作、竞品、投资、示范项目等关系。

## 十一、专家观点与访谈摘要
核心专家：{key_experts}。

{key_points}

## 十二、商业化路径判断
建议区分科研仪器、政府示范、运营商、电力能源、工业检测、导航定位等路径分别评估。

## 十三、投资机会与风险
优先关注上游共性卡点、已有客户验证的整机企业，以及真实预算明确的下游场景。

## 十四、对本团队的建议
围绕本团队相关性字段，优先推进高相关企业、专家和客户访谈。

## 十五、后续调研任务清单
请在调研任务管理页补充责任人、截止时间和验证问题。
"""

