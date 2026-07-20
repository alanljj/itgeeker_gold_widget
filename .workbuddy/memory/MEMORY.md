# ITGeeker Gold Widget - 工作记忆

## 项目信息
- **项目名**: ITGeeker Gold Widget
- **版本**: v1.3.0.0
- **路径**: d:\git_geeker\geeker_dev\python_dev\py_fin\widget_gold_price\
- **开发者**: 技术奇客ITGeeker.net | https://www.itgeeker.net
- **Emoji图标**: 🧈

## 技术栈
- Python 3.14 + PySide6 6.11.0 + requests
- 无边框透明圆角窗口（WA_TranslucentBackground）
- 系统托盘 QSystemTrayIcon

## 项目结构
```
main.py              # 主入口（应用初始化、图标、托盘绑定）
main_window.py       # 主窗口 GoldWidget（无边框、拖拽、右键菜单、实时刷新）
settings_dialog.py   # 设置对话框（颜色/透明度/字体/刷新间隔/货币）
tray.py              # 系统托盘 GoldTrayIcon + make_emoji_icon()
gold_api.py          # 价格数据（3个数据源故障转移）
config.py            # JSON配置管理，保存至 ~/.itgeeker_widget_config/config_gold.json
requirements.txt     # PySide6>=6.6.0, requests>=2.31.0
itgeeker_gold_widget.spec  # PyInstaller 打包配置
version_info.py      # 版本信息（VSVersionInfo）
test_api.py          # 数据源测试脚本（可删除）
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
- 系统托盘：Emoji图标生成，双击显示/隐藏

## 运行
```bash
pip install PySide6 requests
python main.py
```
