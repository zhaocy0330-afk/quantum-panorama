# 项目结构说明

本项目当前名称为 `quantum-panorama`。为了不破坏现有页面和导入路径，核心业务代码继续放在 `quantum_panorama/` 包中；`src/` 目录仅作为后续扩展占位。

## 顶层文件

- `app.py`：Streamlit 主入口，负责初始化数据库、加载页面和侧边栏导航。
- `requirements.txt`：运行依赖。
- `run.bat`：Windows 双击启动脚本。
- `run.ps1`：PowerShell 启动脚本。
- `desktop_launcher.py`：桌面封装预留入口。
- `.gitignore`：忽略虚拟环境、数据库、日志、缓存和 secrets。
- `.env.example`：环境变量模板，不包含真实密钥。

## 配置目录

- `.streamlit/config.toml`：可提交的 Streamlit 展示配置。
- `.streamlit/secrets.toml.example`：Streamlit secrets 示例。
- `config/app_config.yaml`：应用、数据库、研报和模型配置示例。
- `config/sources.yaml`：默认数据源示例。
- `config/keywords.yaml`：分类关键词和重要性关键词示例。

## 业务代码目录

- `quantum_panorama/dashboards/`：Streamlit 页面。
- `quantum_panorama/collectors/`：RSS、网页、手动 URL、自动采集管线。
- `quantum_panorama/storage/`：新投研数据库读写层。
- `quantum_panorama/database.py`：原 MVP 数据库初始化和示例数据。
- `quantum_panorama/ai/`：OpenAI 客户端、单条摘要和研报生成。
- `quantum_panorama/utils/`：分类、去重、导入导出等工具。
- `quantum_panorama/analyzers/`：市场、技术路线、企业、专家、投融资等分析模块。

## 数据目录

- `data/*.csv`：示例种子数据，可以提交。
- `data/*.db`、`data/*.sqlite3`：运行时数据库，不提交。
- `database/.gitkeep`：预留数据库目录占位。

## 脚本和文档

- `scripts/check_project_structure.py`：上传 GitHub 前检查关键文件和敏感文件。
- `scripts/run_auto_collect.py`：GitHub Actions 或命令行采集预留脚本。
- `docs/GITHUB_UPLOAD_GUIDE.md`：GitHub 上传指南。
- `docs/DEVELOPMENT_GUIDE.md`：后续开发指南。
