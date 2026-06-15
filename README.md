# Quantum Panorama 量子行业自动行研系统

这是一个基于 **Streamlit + SQLite + pandas + OpenAI API 预留接口** 的量子行业自动行研 / 自动情报 / 投资辅助分析工具。系统面向量子科技产业研究、企业跟踪、专家访谈、产业链梳理、自动采集、审核入库和 AI 研报生成场景。

当前版本保留原有量子产业研究工作台 MVP 页面，并新增数据源管理、手动采集、半自动采集、采集结果审核池、投研数据库和 AI 研报生成中心。

## 核心功能

- 量子行业新闻、企业动态、政策、融资和产品信息采集。
- 论文、专利、政策、融资、企业、专家、访谈和产业链关系整理。
- 量子计算、量子通信、量子精密测量/量子传感等分类标签。
- URL、标题和相似标题去重。
- staging 审核池：所有采集结果先审核，批准后进入正式投研数据库。
- 投研数据库 `research_items` 导出 CSV / Excel / Markdown。
- AI 单条摘要和日报、周报、月报、专题报告生成入口。
- 本地 Streamlit 可视化界面，兼容 Streamlit Community Cloud 部署。

## 项目结构

```text
quantum-panorama/
├─ app.py                         # Streamlit 主入口
├─ README.md                      # 项目说明
├─ requirements.txt               # Python 依赖
├─ run.bat                        # Windows 双击启动脚本
├─ run.ps1                        # PowerShell 启动脚本
├─ desktop_launcher.py            # 桌面封装预留入口
├─ .gitignore                     # Git 忽略规则
├─ .env.example                   # 环境变量示例，不含真实密钥
├─ .streamlit/
│  ├─ config.toml                 # 可提交的 Streamlit 配置
│  └─ secrets.toml.example        # Streamlit secrets 示例，不含真实密钥
├─ .github/
│  └─ workflows/
│     └─ auto_collect.yml         # 手动触发的 GitHub Actions 采集预留
├─ config/
│  ├─ app_config.yaml             # 应用配置示例
│  ├─ sources.yaml                # 数据源配置示例
│  └─ keywords.yaml               # 分类关键词示例
├─ data/
│  ├─ .gitkeep                    # 保留目录
│  └─ *.csv                       # 示例种子数据，可提交
├─ database/
│  └─ .gitkeep                    # 数据库目录占位，真实 db 不提交
├─ docs/
│  ├─ PROJECT_STRUCTURE.md
│  ├─ DEVELOPMENT_GUIDE.md
│  └─ GITHUB_UPLOAD_GUIDE.md
├─ quantum_panorama/              # 当前实际业务代码包
│  ├─ ai/
│  ├─ analyzers/
│  ├─ collectors/
│  ├─ dashboards/
│  ├─ services/
│  ├─ storage/
│  └─ utils/
├─ scripts/
│  ├─ check_project_structure.py  # 上传前结构检查
│  └─ run_auto_collect.py         # 自动采集脚本预留
├─ src/
│  └─ __init__.py                 # 兼容占位；当前业务包仍是 quantum_panorama
└─ tests/
   └─ .gitkeep
```

## 本地运行

### Windows 一键启动

双击项目根目录下的：

```text
run.bat
```

脚本会自动检查 Python、创建 `.venv`、安装依赖并启动 Streamlit。

### PowerShell 启动

```powershell
cd quantum-panorama
.\run.ps1
```

如果 PowerShell 执行策略阻止脚本，可临时使用：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\run.ps1
```

### 命令行手动启动

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

如果 Windows 上 `python` 命令无响应或指向 Microsoft Store 占位启动器，可把上面的 `python` 替换为 `py`，例如：

```bash
py -m venv .venv
```

浏览器打开：

```text
http://localhost:8501
```

## 环境变量

复制 `.env.example` 为 `.env` 后填写本地私有配置。不要提交 `.env`。

常用变量：

```env
OPENAI_API_KEY=your_api_key_here
QUANTUM_PANORAMA_DB_PATH=data/quantum_panorama.sqlite3
QUANTUM_RESEARCH_DB_PATH=data/quantum_research.db
REPORT_OUTPUT_DIR=reports/output
APP_ENV=development
```

Streamlit Cloud 使用 `.streamlit/secrets.toml` 或 Cloud 控制台 Secrets。仓库中只提交 `.streamlit/secrets.toml.example`。

## 数据库说明

系统会自动创建本地 SQLite 数据库：

```text
data/quantum_panorama.sqlite3
data/quantum_research.db
```

数据库文件属于运行时生成物，默认不提交到 GitHub。示例 CSV 数据保留在 `data/` 下，可用于初始化展示。

## 上传前检查

在项目根目录运行：

```bash
python scripts/check_project_structure.py
python -m compileall .
```

检查脚本会提示关键文件是否存在、是否发现不应上传的敏感文件，并给出是否适合上传 GitHub 的结论。

## GitHub 上传方法

请从项目根目录执行 Git 命令，不要只上传某个子文件夹。

```bash
git init
git add .
git status --short
git commit -m "Initial commit: quantum research app"
git branch -M main
git remote add origin <你的GitHub仓库地址>
git push -u origin main
```

重要提醒：

- 不建议用网页拖拽上传整个项目。
- GitHub 支持 `.gitignore`、`.streamlit`、`.github`、`.env.example` 等点号文件。
- Windows 文件管理器可能默认隐藏点号文件，但 Git 可以正常追踪。
- 上传前一定运行 `git status --short`，确认 `.streamlit/config.toml`、`.github/workflows/`、`.gitignore`、`.env.example` 没有遗漏。

## Streamlit Community Cloud 部署

1. 将完整项目 push 到 GitHub。
2. 在 Streamlit Community Cloud 中选择该仓库。
3. Main file path 填写：

```text
app.py
```

4. 在 Secrets 中按需配置：

```toml
OPENAI_API_KEY = "your_api_key_here"
QUANTUM_PANORAMA_DB_PATH = "data/quantum_panorama.sqlite3"
QUANTUM_RESEARCH_DB_PATH = "data/quantum_research.db"
```

未配置 `OPENAI_API_KEY` 时，AI 研报功能不可用，但采集、审核、数据库和看板功能仍可使用。

## 不应该上传的文件

- `.env`
- `.env.local`
- `.streamlit/secrets.toml`
- `.venv/`
- `venv/`
- `__pycache__/`
- `*.pyc`
- `*.log`
- `*.db`
- `*.sqlite`
- `*.sqlite3`
- `reports/output/`
- `outputs/`
- `temp/`
- `tmp/`

## 当前 MVP 状态

已完成：

- Streamlit 页面框架和原 MVP 页面保留。
- 数据源管理、手动采集、自动检索中心、staging 审核池。
- 投研数据库和导出功能。
- AI 摘要 / AI 研报生成入口。
- 本地 SQLite 初始化。
- GitHub Actions 手动触发采集预留。
- GitHub-ready 文档、启动脚本、上传前结构检查脚本。

后续建议：

- 增加单元测试和采集器 mock 测试。
- 将配置文件 `config/*.yaml` 与页面默认配置打通。
- 增加更细粒度的权限、审计日志和数据备份。
- 接入真实专利、论文和政策 API。
- 增加 Word / PDF / PPT 导出。
