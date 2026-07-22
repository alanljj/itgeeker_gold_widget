"""
ITGeeker Gold Widget - 主入口
软件名称: ITGeeker Gold Widget
版本: v1.3.3.0
开发者: 技术奇客ITGeeker.net
网址: https://www.itgeeker.net
Emoji图标: 🧈
"""

import sys
import os

# 确保当前目录在 path 中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from config import load_config, save_config, APP_NAME, APP_VERSION
from main_window import GoldWidget
from tray import GoldTrayIcon, load_app_icon


def main():
    # 高 DPI 支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION.replace("v", ""))
    app.setOrganizationName("ITGeeker.net")

    # 设置应用图标（任务栏 & 窗口标题栏共用 img/ 下的真实图标）
    app_icon = load_app_icon(128)
    app.setWindowIcon(app_icon)

    # 设置全局字体（支持中文 + Emoji）
    font = QFont()
    font.setFamily("Microsoft YaHei UI")
    font.setPixelSize(13)
    app.setFont(font)

    # 不因最后一个窗口关闭而退出（托盘模式）
    app.setQuitOnLastWindowClosed(False)

    # 加载配置
    cfg = load_config()

    # 创建主窗口（先不传 tray，后面再绑定）
    widget = GoldWidget(cfg)
    widget.setWindowIcon(app_icon)

    # 创建系统托盘
    tray = GoldTrayIcon(widget, cfg)
    tray.show()

    # 把 tray 绑回 widget
    widget.tray = tray

    # 显示主窗口
    widget.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
