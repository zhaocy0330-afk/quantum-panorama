from __future__ import annotations

from datetime import datetime


DEFAULT_DATA_SOURCES = [
    {
        "source_name": "arXiv",
        "source_type": "论文",
        "enabled": True,
        "requires_api_key": False,
        "base_url": "https://export.arxiv.org/api/query",
        "description": "用于量子计算、量子通信、量子精密测量前沿论文检索。",
        "last_run_at": "",
    },
    {
        "source_name": "OpenAlex",
        "source_type": "论文/作者/机构",
        "enabled": True,
        "requires_api_key": False,
        "base_url": "https://api.openalex.org/works",
        "description": "用于论文、作者、机构和主题检索。",
        "last_run_at": "",
    },
    {
        "source_name": "USPTO",
        "source_type": "专利",
        "enabled": True,
        "requires_api_key": True,
        "base_url": "https://developer.uspto.gov/api-catalog",
        "description": "预留美国专利检索接口，MVP 使用 mock 数据。",
        "last_run_at": "",
    },
    {
        "source_name": "RSS/新闻源",
        "source_type": "新闻/政策/融资",
        "enabled": True,
        "requires_api_key": False,
        "base_url": "https://quantumcomputingreport.com/feed/",
        "description": "用于企业新闻、融资新闻、政策动态和产品动态检索。",
        "last_run_at": "",
    },
    {
        "source_name": "手动导入",
        "source_type": "CSV/Excel",
        "enabled": True,
        "requires_api_key": False,
        "base_url": "",
        "description": "用于人工整理的 Excel/CSV 数据导入。",
        "last_run_at": "",
    },
]

DEFAULT_RESEARCH_SOURCES = [
    {
        "name": "arXiv Quantum Physics RSS",
        "source_type": "rss",
        "url": "https://export.arxiv.org/rss/quant-ph",
        "keywords": "quantum,qubit,ion trap,superconducting,QKD,quantum sensing",
        "category_hint": "论文进展",
        "enabled": 1,
        "crawl_interval_hours": 24,
    },
    {
        "name": "Nature Quantum Information",
        "source_type": "web_list",
        "url": "https://www.nature.com/npjqi/",
        "keywords": "quantum,qubit,QKD,sensing,materials",
        "category_hint": "论文进展",
        "enabled": 1,
        "crawl_interval_hours": 48,
    },
    {
        "name": "IBM Quantum Blog",
        "source_type": "web_list",
        "url": "https://www.ibm.com/quantum/blog",
        "keywords": "quantum computing,qubit,roadmap,error correction",
        "category_hint": "公司动态",
        "enabled": 1,
        "crawl_interval_hours": 24,
    },
    {
        "name": "IonQ News",
        "source_type": "web_list",
        "url": "https://ionq.com/news",
        "keywords": "IonQ,quantum computing,trapped ion,partnership,customer",
        "category_hint": "公司动态",
        "enabled": 1,
        "crawl_interval_hours": 24,
    },
    {
        "name": "Quantinuum News",
        "source_type": "web_list",
        "url": "https://www.quantinuum.com/news",
        "keywords": "Quantinuum,quantum computing,quantum cybersecurity,trapped ion",
        "category_hint": "公司动态",
        "enabled": 1,
        "crawl_interval_hours": 24,
    },
    {
        "name": "中国工信部新闻",
        "source_type": "web_list",
        "url": "https://www.miit.gov.cn/xwdt/",
        "keywords": "量子,科技,政策,产业,创新",
        "category_hint": "政策监管",
        "enabled": 1,
        "crawl_interval_hours": 24,
    },
    {
        "name": "科技部新闻",
        "source_type": "web_list",
        "url": "https://www.most.gov.cn/kjbgz/",
        "keywords": "量子,科技,政策,基础研究,产业",
        "category_hint": "政策监管",
        "enabled": 1,
        "crawl_interval_hours": 24,
    },
]


def registry_as_rows() -> list[dict]:
    rows = []
    now = datetime.now().isoformat(timespec="seconds")
    for item in DEFAULT_DATA_SOURCES:
        row = item.copy()
        row["last_run_at"] = row.get("last_run_at") or now
        rows.append(row)
    return rows
