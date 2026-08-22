"""
ITGeeker Gold Widget - 主窗口 Widget
开发者: 技术奇客ITGeeker.net
网址: https://www.itgeeker.net
版本: v1.3.5.0
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSizeGrip, QApplication, QMenu
)
from PySide6.QtCore import (
    Qt, QTimer, QThread, Signal, QPoint, QSize
)
from PySide6.QtGui import (
    QPainter, QColor, QFont, QCursor, QAction,
    QPainterPath, QLinearGradient
)

from config import APP_NAME, APP_VERSION, APP_EMOJI, APP_URL, APP_DEVELOPER, save_config, set_auto_start
from gold_api import fetch_gold_price, GoldPriceData
import webbrowser


# ---------------------------------------------------------------------------
# 后台数据拉取线程
# ---------------------------------------------------------------------------
class FetchThread(QThread):
    data_ready = Signal(object)  # GoldPriceData

    def __init__(self, currency: str = "CNY"):
        super().__init__()
        self.currency = currency

    def run(self):
        data = fetch_gold_price(self.currency)
        self.data_ready.emit(data)


# ---------------------------------------------------------------------------
# 主 Widget 窗口
# ---------------------------------------------------------------------------
class GoldWidget(QWidget):

    def __init__(self, cfg: dict, tray=None):
        super().__init__()
        self.cfg = cfg
        self.tray = tray
        self._drag_pos = None
        self._gold_data: GoldPriceData | None = None
        self._fetch_thread: FetchThread | None = None

        self._setup_window()
        self._setup_ui()
        self._setup_timer()
        self._fetch_price()   # 启动时立即拉取一次

    # ------------------------------------------------------------------
    # 窗口基础设置
    # ------------------------------------------------------------------
    def _setup_window(self):
        self.setWindowTitle(APP_NAME)
        # 无边框 + 工具窗口（不出现在任务栏alt-tab中，但配合main.py的setWindowIcon已足够）
        flags = Qt.FramelessWindowHint
        if self.cfg.get("always_on_top"):
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # 恢复上次窗口位置和大小
        x = self.cfg.get("window_x", 100)
        y = self.cfg.get("window_y", 100)
        w = self.cfg.get("window_width", 220)
        h = self.cfg.get("window_height", 175)
        self.setGeometry(x, y, w, h)
        self.setMinimumSize(210, 135)

    # ------------------------------------------------------------------
    # UI 布局
    # ------------------------------------------------------------------
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 8)
        layout.setSpacing(2)

        # --- 标题行：Emoji + 软件名（左）+ 版本号小字（右）---
        title_row = QHBoxLayout()
        self.lbl_icon = QLabel(APP_EMOJI)
        self.lbl_icon.setStyleSheet("font-size: 18px; background: transparent;")
        self.lbl_title = QLabel(APP_NAME)
        self._apply_label_style(self.lbl_title, size=11, bold=True, alpha=180)

        # 右侧：版本号（小字，半透明）
        self.lbl_version = QLabel(APP_VERSION)
        self._apply_label_style(self.lbl_version, size=8, alpha=90)
        self.lbl_version.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        title_row.addWidget(self.lbl_icon)
        title_row.addWidget(self.lbl_title)
        title_row.addStretch()
        title_row.addWidget(self.lbl_version)
        layout.addLayout(title_row)

        # --- 价格行 ---
        self.lbl_price = QLabel("-- --")
        font_size = self.cfg.get("font_size", 14)
        self._apply_label_style(self.lbl_price, size=font_size + 10, bold=True)
        self.lbl_price.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.lbl_price)

        # --- 涨跌行 + 货币切换按钮 ---
        change_row = QHBoxLayout()
        change_row.setSpacing(4)
        self.lbl_change = QLabel("--")
        self._apply_label_style(self.lbl_change, size=font_size + 2, bold=True)
        self.lbl_change_pct = QLabel("(--%)")
        self._apply_label_style(self.lbl_change_pct, size=font_size + 2)

        # 货币切换按钮（右侧，小胶囊样式）
        from PySide6.QtWidgets import QPushButton
        self.btn_currency = QPushButton()
        self._update_currency_btn_text()
        self.btn_currency.setFixedSize(54, 22)
        self.btn_currency.setCursor(Qt.PointingHandCursor)
        self.btn_currency.clicked.connect(self._toggle_currency)
        self._apply_currency_btn_style()

        change_row.addWidget(self.lbl_change)
        change_row.addWidget(self.lbl_change_pct)
        change_row.addStretch()
        change_row.addWidget(self.btn_currency)
        layout.addLayout(change_row)

        # --- 详细行（开/高/低）---
        detail_row = QHBoxLayout()
        detail_row.setSpacing(8)
        self.lbl_open = QLabel("开: --")
        self.lbl_high = QLabel("高: --")
        self.lbl_low = QLabel("低: --")
        for lbl in (self.lbl_open, self.lbl_high, self.lbl_low):
            self._apply_label_style(lbl, size=font_size - 1, alpha=160)
            detail_row.addWidget(lbl)
        detail_row.addStretch()
        layout.addLayout(detail_row)

        # --- 底部行（时间 左 | 数据来源 右 | SizeGrip）---
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(4)
        bottom_row.setContentsMargins(0, 0, 0, 0)

        # 左：更新时间
        self.lbl_time = QLabel("")
        self._apply_label_style(self.lbl_time, size=9, alpha=110)
        bottom_row.addWidget(self.lbl_time)

        bottom_row.addStretch()

        # 右：数据来源（10px，半透明）
        self.lbl_source = QLabel("")
        self._apply_label_style(self.lbl_source, size=10, alpha=100)
        self.lbl_source.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        bottom_row.addWidget(self.lbl_source)

        # 右下角 SizeGrip
        size_grip = QSizeGrip(self)
        size_grip.setStyleSheet("background: transparent;")
        bottom_row.addWidget(size_grip, 0, Qt.AlignBottom | Qt.AlignRight)
        layout.addLayout(bottom_row)

    def _update_currency_btn_text(self):
        cur = self.cfg.get("currency", "CNY")
        # 显示"切换到另一个"的提示：当前CNY就显示 $ USD，当前USD就显示 ¥ CNY
        if cur == "CNY":
            self.btn_currency.setText("$ USD")
        else:
            self.btn_currency.setText("¥ CNY")

    def _apply_currency_btn_style(self):
        cur = self.cfg.get("currency", "CNY")
        accent = "#f5a623" if cur == "CNY" else "#52c8ff"
        self.btn_currency.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255,255,255,0.10);
                color: {accent};
                border: 1px solid {accent};
                border-radius: 11px;
                font-size: 10px;
                font-weight: bold;
                padding: 0 6px;
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.20);
            }}
            QPushButton:pressed {{
                background: rgba(255,255,255,0.08);
            }}
        """)

    def _toggle_currency(self):
        cur = self.cfg.get("currency", "CNY")
        self.cfg["currency"] = "USD" if cur == "CNY" else "CNY"
        save_config(self.cfg)
        self._update_currency_btn_text()
        self._apply_currency_btn_style()
        # 立即刷新数据
        self._fetch_price()

    def _apply_label_style(self, lbl: QLabel, size=12, bold=False, alpha=255):
        color = self.cfg.get("text_color", "#ffffff")
        weight = "bold" if bold else "normal"
        lbl.setStyleSheet(
            f"color: {color}; font-size: {size}px; font-weight: {weight}; "
            f"background: transparent; opacity: {alpha/255:.2f};"
        )
        lbl.setAttribute(Qt.WA_TranslucentBackground, True)

    # ------------------------------------------------------------------
    # 定时器
    # ------------------------------------------------------------------
    def _setup_timer(self):
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._fetch_price)
        interval_sec = self.cfg.get("refresh_interval", 60)
        self._timer.start(interval_sec * 1000)

    def _restart_timer(self):
        self._timer.stop()
        interval_sec = self.cfg.get("refresh_interval", 60)
        self._timer.start(interval_sec * 1000)

    # ------------------------------------------------------------------
    # 数据拉取
    # ------------------------------------------------------------------
    def _fetch_price(self):
        if self._fetch_thread and self._fetch_thread.isRunning():
            return
        self.lbl_source.setText("刷新中…")
        currency = self.cfg.get("currency", "CNY")
        self._fetch_thread = FetchThread(currency)
        self._fetch_thread.data_ready.connect(self._on_data_ready)
        self._fetch_thread.start()

    def _on_data_ready(self, data: GoldPriceData):
        self._gold_data = data
        self._update_ui(data)

    # ------------------------------------------------------------------
    # 更新 UI 显示
    # ------------------------------------------------------------------
    def _update_ui(self, data: GoldPriceData):
        if data.error:
            self.lbl_price.setText("获取失败")
            self.lbl_change.setText(data.error)
            self.lbl_source.setText("--")
            return

        # 价格
        if data.currency == "CNY":
            price_str = f"¥ {data.price:.2f}"
            unit_str = data.unit
        else:
            price_str = f"$ {data.price:.2f}"
            unit_str = data.unit

        self.lbl_price.setText(f"{price_str}  {unit_str}")

        # 涨跌颜色
        up = data.is_up
        change_color = "#ff4d4f" if up else "#52c41a"
        arrow = "▲" if up else "▼"
        sign = "+" if up else ""

        change_val = f"{arrow} {sign}{data.change:.3f}" if data.currency == "CNY" else f"{arrow} {sign}{data.change:.2f}"
        pct_val = f"({sign}{data.change_pct:.2f}%)"

        self.lbl_change.setText(change_val)
        self.lbl_change.setStyleSheet(
            f"color: {change_color}; font-size: {self.cfg.get('font_size',14)+2}px; "
            f"font-weight: bold; background: transparent;"
        )
        self.lbl_change_pct.setText(pct_val)
        self.lbl_change_pct.setStyleSheet(
            f"color: {change_color}; font-size: {self.cfg.get('font_size',14)+2}px; "
            f"background: transparent;"
        )

        # 开高低
        if data.open_price:
            self.lbl_open.setText(f"开: {data.open_price:.2f}")
        if data.high:
            self.lbl_high.setText(f"高: {data.high:.2f}")
        if data.low:
            self.lbl_low.setText(f"低: {data.low:.2f}")

        # 时间和来源
        self.lbl_time.setText(data.timestamp.strftime("%H:%M:%S"))
        self.lbl_source.setText(data.source)

        # 更新系统托盘提示
        if self.tray:
            self.tray.setToolTip(
                f"{APP_EMOJI} {APP_NAME}\n"
                f"版本: {APP_VERSION}\n"
                f"黄金: {price_str} {unit_str}\n"
                f"涨跌: {change_val} {pct_val}\n"
                f"更新: {data.timestamp.strftime('%H:%M:%S')}"
            )

    # ------------------------------------------------------------------
    # 绘制背景
    # ------------------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        bg_color = QColor(self.cfg.get("bg_color", "#1a1a2e"))
        bg_color.setAlpha(self.cfg.get("bg_opacity", 160))

        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 14, 14)

        painter.fillPath(path, bg_color)

        # 微妙的顶部高光渐变
        grad = QLinearGradient(0, 0, 0, 40)
        grad.setColorAt(0, QColor(255, 255, 255, 18))
        grad.setColorAt(1, QColor(255, 255, 255, 0))
        painter.fillPath(path, grad)

        # 边框
        border_color = QColor(255, 255, 255, 30)
        painter.setPen(border_color)
        painter.drawPath(path)

    # ------------------------------------------------------------------
    # 鼠标拖拽移动窗口
    # ------------------------------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        self._save_geometry()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._save_geometry()

    def moveEvent(self, event):
        super().moveEvent(event)
        self._save_geometry()

    def _save_geometry(self):
        self.cfg["window_x"] = self.x()
        self.cfg["window_y"] = self.y()
        self.cfg["window_width"] = self.width()
        self.cfg["window_height"] = self.height()
        save_config(self.cfg)

    # ------------------------------------------------------------------
    # 右键菜单
    # ------------------------------------------------------------------
    def contextMenuEvent(self, event):
        self._show_context_menu(event.globalPos())

    def _show_context_menu(self, pos: QPoint):
        menu = QMenu(self)
        menu.setStyleSheet(self._menu_style())

        act_refresh = QAction("🔄 立即刷新", self)
        act_refresh.triggered.connect(self._fetch_price)
        menu.addAction(act_refresh)

        menu.addSeparator()

        # 置顶菜单：文本随状态动态变化
        is_on_top = self.cfg.get("always_on_top", False)
        act_top = QAction("🔓 取消置顶" if is_on_top else "📌 窗口置顶", self)
        act_top.setCheckable(True)
        act_top.setChecked(is_on_top)
        act_top.triggered.connect(self._toggle_always_on_top)
        menu.addAction(act_top)

        act_settings = QAction("⚙️ 设置", self)
        act_settings.triggered.connect(self._open_settings)
        menu.addAction(act_settings)

        menu.addSeparator()

        act_url = QAction("🌐 访问官网", self)
        act_url.triggered.connect(lambda: webbrowser.open(APP_URL))
        menu.addAction(act_url)

        act_about = QAction(f"ℹ️ 关于  {APP_VERSION}", self)
        act_about.triggered.connect(self._show_about)
        menu.addAction(act_about)

        menu.addSeparator()

        act_quit = QAction("❌ 退出", self)
        act_quit.triggered.connect(QApplication.quit)
        menu.addAction(act_quit)

        menu.exec(pos)

    def _menu_style(self):
        bg = self.cfg.get("bg_color", "#1a1a2e")
        return f"""
            QMenu {{
                background-color: {bg};
                color: {self.cfg.get('text_color','#ffffff')};
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 8px;
                padding: 4px;
                font-size: 13px;
            }}
            QMenu::item {{
                padding: 6px 18px;
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
    # 菜单动作
    # ------------------------------------------------------------------
    def _toggle_always_on_top(self, checked: bool):
        self.cfg["always_on_top"] = checked
        flags = Qt.FramelessWindowHint
        if checked:
            flags |= Qt.WindowStaysOnTopHint
        # 先隐藏再设置标志，避免 setWindowFlags 失效
        self.hide()
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.show()
        save_config(self.cfg)

    def _open_settings(self):
        from settings_dialog import SettingsDialog
        dlg = SettingsDialog(self.cfg, parent=self)
        if dlg.exec():
            new_cfg = dlg.get_config()
            self.cfg.update(new_cfg)
            save_config(self.cfg)
            self._apply_config()

    def _apply_config(self):
        """配置变更后重新应用"""
        # 更新置顶
        flags = Qt.FramelessWindowHint
        if self.cfg.get("always_on_top"):
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # 更新字体大小
        font_size = self.cfg.get("font_size", 14)
        self.lbl_price.setStyleSheet(
            f"color: {self.cfg.get('text_color','#ffffff')}; "
            f"font-size: {font_size+10}px; font-weight: bold; background: transparent;"
        )

        # 更新货币按钮
        self._update_currency_btn_text()
        self._apply_currency_btn_style()

        # 更新自启动设置
        auto_start = self.cfg.get("auto_start", False)
        set_auto_start(auto_start)

        # 重启定时器
        self._restart_timer()
        self.show()
        self.update()

        # 立即刷新数据
        self._fetch_price()

    def _show_about(self):
        from PySide6.QtWidgets import QMessageBox
        box = QMessageBox(self)
        box.setWindowTitle(f"关于 {APP_NAME}")
        box.setText(
            f"<b>{APP_EMOJI} {APP_NAME}</b><br>"
            f"版本: {APP_VERSION}<br>"
            f"开发者: {APP_DEVELOPER}<br>"
            f"<a href='{APP_URL}'>{APP_URL}</a>"
        )
        box.setIcon(QMessageBox.Information)
        box.exec()
