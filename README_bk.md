# 🧈 ITGeeker Gold Widget

**版本**: v1.3.3.0  
**开发者**: 技术奇客ITGeeker.net  
**网址**: https://www.itgeeker.net

---

## 功能特性

- 📊 实时显示黄金当日价格、涨跌额、涨跌幅
- 💰 支持 **人民币/克 (Au9999)** 和 **美元/盎司** 双模式
- 🪟 无边框透明窗口，圆角玻璃质感
- 📌 右键菜单支持窗口置顶
- 🎨 可自定义背景颜色、透明度、字体大小、文字颜色
- ⏱️ 可设置数据刷新间隔（最短10秒）
- 💾 自动记住窗口位置和大小，下次启动自动恢复
- 🖱️ 支持鼠标拖拽移动窗口，右下角拖拽调整大小
- 🖥️ 系统托盘图标，双击显示/隐藏窗口
- 🔄 右键菜单和托盘菜单功能完全一致

## 数据来源

| 货币 | 来源 | 品种 |
|------|------|------|
| CNY  | 新浪财经（主） | Au9999 沪金 |
| CNY  | GoldPrice.org（备用） | XAU/CNY |
| USD  | GoldPrice.org | XAU/USD |

## 安装运行

### 环境要求
- Python 3.10+
- Windows 10/11

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行

```bash
python main.py
```

### 打包为 Windows EXE

```bash
# 打包（输出到项目根目录）
pip install pyinstaller
python -m PyInstaller itgeeker_gold_widget.spec --clean --noconfirm
```

> 📦 打包后 `ITGeekerGoldWidget.exe` 及所有依赖文件位于 `dist/` 目录。

## 快捷操作

| 操作 | 功能 |
|------|------|
| 鼠标左键拖拽 | 移动窗口 |
| 右下角拖拽 | 调整窗口大小 |
| 右键菜单 | 刷新/设置/置顶/退出 |
| 托盘双击 | 显示/隐藏窗口 |
| 托盘右键 | 完整菜单 |

## 配置文件位置

配置自动保存至用户目录：

```
%USERPROFILE%\itgeeker_widget_config\config_gold.json
```

## 项目结构

```
itgeeker_gold_widget/
├── main.py              # 主入口
├── main_window.py       # 主窗口 Widget
├── settings_dialog.py   # 设置对话框
├── tray.py              # 系统托盘
├── gold_api.py          # 价格数据获取
├── config.py            # 配置管理
├── requirements.txt     # 依赖
└── README.md
```

## 开源协议

MIT License - 自由使用，欢迎贡献

---

> 💡 **提示**: 如遇价格获取失败，请检查网络连接或稍后重试。数据仅供参考，不构成投资建议。
