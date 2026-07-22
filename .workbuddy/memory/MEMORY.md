# ITGeeker Gold Widget - 工作记忆

## 项目信息
- **项目名**: ITGeeker Gold Widget
- **版本**: v1.3.3.0
- **路径**: `D:\git_geeker\itgeeker_gold_widget`
- **开发者**: 技术奇客ITGeeker.net | https://www.itgeeker.net
- **Emoji图标**: 🧈

## 技术栈
- Python 3.14 + PySide6 6.11.1 + requests 2.34.2
- 无边框透明圆角窗口（WA_TranslucentBackground）
- 系统托盘 QSystemTrayIcon
- 包管理：**uv**（PEP 621 风格 `pyproject.toml` + `uv.lock`）
- 打包：PyInstaller 6.21.0（dev 依赖）

## 环境与工具链约定（2026-07-22 起生效）
- **包管理**：统一用 `uv`，**禁止** `pip` / `pip3` / `python -m pip`
  - 装包：`uv add <pkg>`
  - 卸包：`uv remove <pkg>`
  - 同步环境：`uv sync`
  - 临时工具：`uvx <tool>`
- **运行脚本**：优先 `uv run <script>.py`（自动激活 venv）
  - 也可手动：`.\.venv\Scripts\activate` → `python <script>.py`
- **虚拟环境**：`.venv/` 在项目根目录内（uv 自动管理，**不要**手工改）
- **Python 版本**：3.14（由 `.python-version` 锁定，pyproject 也写 `requires-python = ">=3.14"`）
- **代码兼容性**：所有新代码须兼容 Python 3.14 新特性/语法

## 依赖现状（⚠️ 待补）
- `pyproject.toml` 当前 `dependencies = []`（空）
- `.venv` 已建好但**未装** PySide6 / requests —— 旧 `requirements.txt` 里的依赖需要迁移到 pyproject
- 下次装包前应先：`uv add PySide6 requests`（用 uv 把现有 requirements 转成正式依赖）

## 项目结构
```
main.py              # 主入口（应用初始化、图标、托盘绑定）
main_window.py       # 主窗口 GoldWidget（无边框、拖拽、右键菜单、实时刷新）
settings_dialog.py   # 设置对话框（颜色/透明度/字体/刷新间隔/货币）
tray.py              # 系统托盘 GoldTrayIcon + load_app_icon() + make_emoji_icon() 兜底
gold_api.py          # 价格数据（3个数据源故障转移）
config.py            # JSON配置管理 + resource_path()，保存至 ~/.itgeeker_widget_config/config_gold.json
pyproject.toml       # uv 项目元数据（PEP 621）
uv.lock              # uv 锁定文件
.python-version      # 3.14
itgeeker_gold_widget.spec  # PyInstaller 打包配置
version_info.py      # Windows 版本信息（VSVersionInfo）
test_api.py          # 数据源测试脚本（可删除）
img/
  gold_widget.ico              # ⭐ EXE + 运行时窗口/托盘图标（多尺寸）
  gold_widget_310x310_Logo.png # 大尺寸 Logo 备选
README.md
```

## 数据源（故障转移顺序）
1. 新浪财经 Au9999（CNY/克）
2. GoldPrice.org JSON（CNY 或 USD）
3. Yahoo Finance GC=F（USD/oz）→ 自动汇率转换为 CNY/克

**已验证**: Yahoo Finance GC=F 在当前网络环境下可用（2026-04-04 测试成功）
- 价格示例: 4702.7 $/oz → ¥1040.51 元/克（+0.491%）

## 主要功能
- 无边框透明窗口，圆角玻璃质感，鼠标拖拽移动，右下角拖拽调整大小
- 显示当日价格、涨跌额、涨跌幅（红/绿色区分涨跌）
- 右键菜单 = 托盘菜单（刷新/设置/置顶/关于/退出）
- 设置对话框：背景色、透明度、文字色、字体大小、刷新间隔、货币单位
- 自动保存窗口位置/大小，下次启动恢复
- 系统托盘：使用 `img/gold_widget.ico`，双击显示/隐藏

## 运行（uv 风格）
```bash
# 首次/重装依赖
uv sync

# 启动主程序
uv run python main.py

# 测试数据源
uv run python test_api.py
```

## 打包（按用户习惯：先测后打，不自动打包）
```bash
uv add --dev pyinstaller
uv run pyinstaller --clean itgeeker_gold_widget.spec
```
