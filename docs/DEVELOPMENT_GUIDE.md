# 开发指南

## 开发环境

建议使用 Python 3.10 或更高版本。

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Windows 用户也可以直接运行 `run.bat` 或 `run.ps1`。

## 代码分层

新增功能时优先放到已有模块中：

- 页面逻辑：`quantum_panorama/dashboards/`
- 采集逻辑：`quantum_panorama/collectors/`
- 数据库读写：`quantum_panorama/storage/database.py`
- AI 能力：`quantum_panorama/ai/`
- 通用工具：`quantum_panorama/utils/`
- 自动化脚本：`scripts/`

不要把所有逻辑写进 `app.py`。`app.py` 只负责页面路由、初始化和全局样式。

## 路径规范

新增路径请使用 `pathlib.Path`，不要写死 Windows 绝对路径。例如：

```python
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
```

## 网络请求规范

所有外部请求必须设置 `timeout`，并捕获异常：

```python
import requests

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except requests.RequestException as exc:
    # 页面层用 st.warning/st.error 展示，脚本层写日志或返回错误对象
    ...
```

不要绕过登录、验证码或付费墙，不做高频爬取。

## 数据库规范

新增表结构放在 `quantum_panorama/storage/database.py` 的初始化逻辑中。数据库文件默认位于：

```text
data/quantum_research.db
data/quantum_panorama.sqlite3
```

数据库文件是运行时产物，不提交到 GitHub。

## AI 功能规范

AI 研报和摘要必须只基于 `research_items` 中已有资料生成。资料不足时要明确写“现有资料不足，无法判断”。不要输出股票买卖建议。

`OPENAI_API_KEY` 读取优先级：

1. Streamlit secrets
2. 环境变量

未配置 Key 时，页面应提示但不能影响非 AI 功能。

## 提交前检查

每次提交前建议运行：

```powershell
python scripts/check_project_structure.py
python -m compileall .
git status --short
```

确认没有 `.env`、`.streamlit/secrets.toml`、数据库、日志、虚拟环境或缓存文件进入提交。
