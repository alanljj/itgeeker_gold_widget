"""
ITGeeker Gold Widget - 系统托盘模块
开发者: 技术奇客ITGeeker.net
版本: v1.3.5.0
"""

import os

from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor, QFont
from PySide6.QtCore import Qt, QRect
import webbrowser

from config import (
    APP_NAME,
    APP_VERSION,
    APP_EMOJI,
    APP_URL,
    APP_DEVELOPER,
    RUNTIME_APP_ICON,
    RUNTIME_APP_LOGO,
)


def make_emoji_icon(emoji: str = "🧈", size: int = 64) -> QIcon:
    """
    用 Emoji 字符生成 QIcon（仅作为 PNG/ICO 缺失时的兜底方案）
    """
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.TextAntialiasing)

    font = QFont()
    font.setPointSize(int(size * 0.55))
    painter.setFont(font)
    painter.setPen(Qt.black)
    painter.drawText(
        QRect(0, 0, size, size),
        Qt.AlignCenter | Qt.AlignVCenter,
        emoji
    )
    painter.end()

    return QIcon(pixmap)


def load_app_icon(preferred_size: int = 64) -> QIcon:
    """
    加载应用图标：优先使用 img/gold_widget.ico（多尺寸自适应），
    次选 img/gold_widget_310x310_Logo.png，最后回退到 Emoji 兜底。
    """
    # 1) ICO 优先 —— 包含 16/32/48/64/128/256 多分辨率，Windows 任务栏 / Alt-Tab 自动选最佳
    for path in (RUNTIME_APP_ICON, RUNTIME_APP_LOGO):
        if path and os.path.exists(path):
            icon = QIcon(path)
            if not icon.isNull():
                return icon

    # 2) 兜底：Emoji 渲染
    return make_emoji_icon(APP_EMOJI, preferred_size)


class GoldTrayIcon(QSystemTrayIcon):
    """系统托盘图标"""

    def __init__(self, widget, cfg: dict):
        super().__init__()
        self._widget = widget
        self._cfg = cfg

        # 使用真实 PNG/ICO 图标
        self.setIcon(load_app_icon(64))
        self.setToolTip(f"{APP_NAME}\n版本: {APP_VERSION}")

        self._build_menu()

        # 双击托盘图标 -> 显示/隐藏窗口
        self.activated.connect(self._on_activated)

    # ------------------------------------------------------------------
    def _build_menu(self):
        menu = QMenu()
        menu.setStyleSheet(self._menu_style())

        act_show = QAction(f"👁️ 显示/隐藏窗口", menu)
        act_show.triggered.connect(self._toggle_visibility)
        menu.addAction(act_show)

        act_refresh = QAction("🔄 立即刷新", menu)
        act_refresh.triggered.connect(self._do_refresh)
        menu.addAction(act_refresh)

        menu.addSeparator()

        act_top = QAction("📌 窗口置顶", menu)
        act_top.setCheckable(True)
        act_top.setChecked(self._cfg.get("always_on_top", False))
        act_top.triggered.connect(self._toggle_top)
        menu.addAction(act_top)
        self._act_top = act_top

        act_settings = QAction("⚙️ 设置", menu)
        act_settings.triggered.connect(self._open_settings)
        menu.addAction(act_settings)

        menu.addSeparator()

        act_url = QAction("🌐 访问官网", menu)
        act_url.triggered.connect(lambda: webbrowser.open(APP_URL))
        menu.addAction(act_url)

        act_about = QAction(f"ℹ️ 关于  {APP_VERSION}", menu)
        act_about.triggered.connect(self._show_about)
        menu.addAction(act_about)

        menu.addSeparator()

        act_quit = QAction("❌ 退出", menu)
        act_quit.triggered.connect(QApplication.quit)
        menu.addAction(act_quit)

        self.setContextMenu(menu)

    def _menu_style(self):
        bg = self._cfg.get("bg_color", "#1a1a2e")
        text = self._cfg.get("text_color", "#ffffff")
        return f"""
            QMenu {{
                background-color: {bg};
                color: {text};
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 8px;
                padding: 4px;
                font-size: 13px;
            }}
            QMenu::item {{
                padding: 6px 20px;
                border-radius: 5px;
            }}
            QMenu::item:selected {{
                background-color: rgba(255,255,255,0.12);
            }}
            QMenu::separator {{
                height: 1px;
                background: rgba(255,255,255,0.1);
                margin: 3px 8px;
            }}
        """

    # ------------------------------------------------------------------
    def _on_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.DoubleClick,
                      QSystemTrayIcon.ActivationReason.Trigger):
            self._toggle_visibility()

    def _toggle_visibility(self):
        if self._widget.isVisible():
            self._widget.hide()
        else:
            self._widget.show()
            self._widget.raise_()
            self._widget.activateWindow()

    def _do_refresh(self):
        self._widget._fetch_price()

    def _toggle_top(self, checked: bool):
        self._cfg["always_on_top"] = checked
        self._widget._toggle_always_on_top(checked)
        self._act_top.setChecked(checked)

    def _open_settings(self):
        self._widget._open_settings()

    def _show_about(self):
        self._widget._show_about()
