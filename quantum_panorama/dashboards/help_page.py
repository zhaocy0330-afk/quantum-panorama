from __future__ import annotations

import streamlit as st


def render() -> None:
    st.title("使用说明")
    st.caption("量子行业研究工作台升级为 AI 投研系统 MVP：手动采集、半自动采集、审核入库、AI分析和研报生成。")

    st.header("系统定位")
    st.write(
        "本系统面向投资经理、产业研究人员和量子科技项目尽调场景，用于沉淀量子行业资料、"
        "跟踪数据源、审核采集结果、形成投研数据库，并基于已入库资料生成 AI 摘要和 Markdown 研报。"
    )

    st.header("推荐使用流程")
    steps = [
        "进入数据源管理，添加 RSS、网页列表页或单 URL 数据源。",
        "使用手动采集中心录入临时发现的网页 URL。",
        "使用自动检索中心对已启用数据源运行一次低频采集。",
        "进入采集结果审核池，筛选 pending 记录，批准入正式库或拒绝。",
        "进入投研数据库查看已审核资料，并导出 CSV、Excel 或 Markdown。",
        "进入 AI研报生成中心，对单条资料生成结构化摘要，或生成日报、周报、专题和风险报告。",
        "继续使用原有市场分析、技术路线、企业库、专家库、访谈库和产业链网络页面做结构化研究。",
    ]
    for idx, step in enumerate(steps, start=1):
        st.markdown(f"**第 {idx} 步：** {step}")

    st.header("数据源管理")
    st.write(
        "数据源支持 `rss`、`web_list`、`single_url`。可配置名称、URL、关键词、类别提示、启用状态和采集间隔小时。"
        "默认数据源按钮会添加 arXiv、Nature、IBM Quantum、IonQ、Quantinuum、工信部、科技部等示例源，已存在的 URL 不会重复添加。"
    )

    st.header("手动采集")
    st.write(
        "单 URL 或批量 URL 均可采集。系统会抓取网页标题、meta description 和正文前 1000 字。"
        "任何单个 URL 失败都不会导致页面崩溃，失败原因会在页面显示。"
    )

    st.header("自动检索")
    st.write(
        "当前 MVP 的自动检索是页面触发：选择数据源后点击“运行一次自动采集”。"
        "Streamlit Cloud 不适合长期后台常驻任务，因此已预留 GitHub Actions 手动 workflow，后续确认后再打开 schedule。"
    )

    st.header("审核入库")
    st.write(
        "采集结果先进入 `crawl_results_staging`，状态为 pending。批准后写入 `research_items`，拒绝后可清空。"
        "系统按标准化 URL hash、标题 hash 和标题相似度做去重，避免重复入库。"
    )

    st.header("AI 分析与研报")
    st.write(
        "AI 只读取 `research_items` 中已审核入库资料，不允许编造事实。资料不足时必须说明“现有资料不足，无法判断”。"
        "未配置 `OPENAI_API_KEY` 时，AI 功能不可用，但采集、审核、数据库和原有页面照常使用。"
    )

    st.header("导入导出")
    st.write("staging 支持 CSV 导出；投研数据库支持 CSV、Excel、Markdown；AI 研报支持 Markdown 下载。Word/PDF 为后续预留。")

    st.header("部署与桌面应用")
    st.write(
        "Streamlit Cloud 部署时推送代码到 GitHub，入口为 `app.py`，依赖来自 `requirements.txt`，API Key 放入 Secrets。"
        "桌面场景可使用 `desktop_launcher.py` 启动本地 Streamlit，后续可用 PyInstaller/Electron/Tauri 封装。"
    )

    st.header("常见问题")
    faq = {
        "数据没有更新怎么办？": "检查数据源是否启用、采集日志是否有错误、关键词是否过窄，以及结果是否仍在审核池 pending。",
        "自动检索结果不准确怎么办？": "调整数据源关键词和类别提示；MVP 使用规则分类和低频采集，复杂语义判断交给审核与 AI 摘要。",
        "如何避免重复数据？": "系统自动使用 URL hash、title hash 和标题相似度去重；正式库和审核池都会参与检查。",
        "如何备份数据库？": "备份 `data/quantum_research.db` 和旧版 `data/quantum_panorama.sqlite3`。生产建议迁移到托管数据库。",
        "如何配置 API Key？": "在 Streamlit Secrets 或环境变量中配置 `OPENAI_API_KEY`，不要写入代码或提交 secrets.toml。",
        "如何本地运行？": "`pip install -r requirements.txt` 后执行 `streamlit run app.py`。",
        "如何部署到网页？": "推送到 GitHub，在 Streamlit Community Cloud 选择 `app.py` 作为入口重新部署。",
    }
    for question, answer in faq.items():
        with st.expander(question):
            st.write(answer)

