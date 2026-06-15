# GitHub 完整上传指南

本项目包含 `.gitignore`、`.streamlit/`、`.github/`、`.env.example` 等点号开头的文件或目录。它们对运行、部署和协作很重要，不能漏传。

## 不建议网页拖拽上传

不建议用 GitHub 网页拖拽、Windows 文件管理器复制或压缩包手工上传整个项目，原因是：

- Windows 文件管理器可能默认隐藏点号文件和目录。
- 手工上传容易漏掉 `.streamlit/config.toml`、`.github/workflows/`、`.gitignore`、`.env.example`。
- 漏传后 Streamlit Cloud、GitHub Actions 或本地启动脚本可能无法正常工作。

## 推荐用 Git 命令行上传

请在项目根目录执行。项目根目录应能看到 `app.py`、`README.md`、`requirements.txt`。

```bash
git init
git add .
git status --short
git commit -m "Initial commit: quantum research app"
git branch -M main
git remote add origin <你的GitHub仓库地址>
git push -u origin main
```

如果仓库已经初始化过，只需要：

```bash
git add .
git status --short
git commit -m "Prepare project for GitHub upload"
git push
```

## GitHub 支持点号文件

GitHub 本身支持以下文件和目录：

- `.gitignore`
- `.env.example`
- `.streamlit/config.toml`
- `.github/workflows/auto_collect.yml`

只要使用 Git 命令行，它们会被正常追踪和上传。

## 上传前检查

运行：

```bash
python scripts/check_project_structure.py
git status --short
```

请重点确认这些文件存在并会被提交：

- `README.md`
- `requirements.txt`
- `run.bat`
- `.gitignore`
- `.env.example`
- `app.py`
- `.streamlit/config.toml`
- `.github/workflows/auto_collect.yml`
- `docs/`
- `config/`
- `quantum_panorama/`
- `scripts/`

## 不应该上传的文件

这些文件不能上传：

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

## 如果点号文件看不见怎么办

Windows 文件管理器里可以开启“查看 -> 显示 -> 隐藏的项目”。不过更推荐用命令确认：

```powershell
Get-ChildItem -Force
git status --short
```

`Get-ChildItem -Force` 会显示 `.streamlit`、`.github`、`.gitignore` 等隐藏文件。

## Streamlit Cloud 部署提醒

上传到 GitHub 后，在 Streamlit Community Cloud 中选择该仓库，入口文件填：

```text
app.py
```

如果需要 AI 功能，在 Streamlit Cloud 的 Secrets 中配置：

```toml
OPENAI_API_KEY = "your_api_key_here"
```

不要把真实 Key 写进代码或提交到 GitHub。
