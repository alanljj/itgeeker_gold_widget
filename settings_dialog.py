"""
ITGeeker Gold Widget - 设置对话框
开发者: 技术奇客ITGeeker.net
版本: v1.3.5.0
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSlider, QSpinBox, QComboBox,
    QGroupBox, QFormLayout, QColorDialog, QFrame,
    QDialogButtonBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette

from config import APP_NAME, APP_EMOJI


class ColorButton(QPushButton):
    """颜色选择按钮"""
    def __init__(self, color: str = "#1a1a2e", parent=None):
        super().__init__(parent)
        self._color = color
        self.setFixedSize(60, 28)
        self._update_style()

    def _update_style(self):
        self.setStyleSheet(
            f"background-color: {self._color}; "
            f"border: 1px solid rgba(255,255,255,0.3); "
            f"border-radius: 4px;"
        )

    def get_color(self) -> str:
        return self._color

    def set_color(self, color: str):
        self._color = color
        self._update_style()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            current = QColor(self._color)
            chosen = QColorDialog.getColor(current, self, "选择颜色")
            if chosen.isValid():
                self._color = chosen.name()
                self._update_style()
        super().mousePressEvent(event)


class SettingsDialog(QDialog):
    def __init__(self, cfg: dict, parent=None):
        super().__init__(parent)
        self._cfg = cfg.copy()
        self.setWindowTitle(f"{APP_EMOJI} {APP_NAME} - 设置")
        self.setMinimumWidth(380)
        self.setModal(True)
        self._build_ui()
        self._apply_dark_style()

    # ------------------------------------------------------------------
    # 构建 UI
    # ------------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # ===== 外观设置 =====
        grp_appearance = QGroupBox("🎨 外观")
        grp_appearance.setStyleSheet(self._group_style())
        form_ap = QFormLayout(grp_appearance)
        form_ap.setSpacing(10)

        # 背景颜色
        self.btn_bg_color = ColorButton(self._cfg.get("bg_color", "#1a1a2e"))
        form_ap.addRow("背景颜色:", self.btn_bg_color)

        # 背景透明度
        opacity_row = QHBoxLayout()
        self.slider_opacity = QSlider(Qt.Horizontal)
        self.slider_opacity.setRange(30, 255)
        self.slider_opacity.setValue(self._cfg.get("bg_opacity", 220))
        self.lbl_opacity_val = QLabel(str(self._cfg.get("bg_opacity", 220)))
        self.lbl_opacity_val.setFixedWidth(30)
        self.slider_opacity.valueChanged.connect(
            lambda v: self.lbl_opacity_val.setText(str(v))
        )
        opacity_row.addWidget(self.slider_opacity)
        opacity_row.addWidget(self.lbl_opacity_val)
        form_ap.addRow("背景透明度:", opacity_row)

        # 文字颜色
        self.btn_text_color = ColorButton(self._cfg.get("text_color", "#ffffff"))
        form_ap.addRow("文字颜色:", self.btn_text_color)

        # 字体大小
        self.spin_font = QSpinBox()
        self.spin_font.setRange(8, 32)
        self.spin_font.setValue(self._cfg.get("font_size", 14))
        self.spin_font.setSuffix(" px")
        form_ap.addRow("字体大小:", self.spin_font)

        layout.addWidget(grp_appearance)

        # ===== 数据设置 =====
        grp_data = QGroupBox("📊 数据")
        grp_data.setStyleSheet(self._group_style())
        form_data = QFormLayout(grp_data)
        form_data.setSpacing(10)

        # 刷新间隔
        self.spin_refresh = QSpinBox()
        self.spin_refresh.setRange(10, 3600)
        self.spin_refresh.setValue(self._cfg.get("refresh_interval", 60))
        self.spin_refresh.setSuffix(" 秒")
        form_data.addRow("刷新间隔:", self.spin_refresh)

        # 货币单位
        self.combo_currency = QComboBox()
        self.combo_currency.addItems(["CNY (人民币/克)", "USD (美元/盎司)"])
        cur = self._cfg.get("currency", "CNY")
        self.combo_currency.setCurrentIndex(0 if cur == "CNY" else 1)
        form_data.addRow("价格单位:", self.combo_currency)

        layout.addWidget(grp_data)

        # ===== 窗口设置 =====
        grp_win = QGroupBox("🪟 窗口")
        grp_win.setStyleSheet(self._group_style())
        form_win = QFormLayout(grp_win)
        form_win.setSpacing(10)

        # 置顶
        from PySide6.QtWidgets import QCheckBox
        self.chk_top = QCheckBox("启用窗口置顶")
        self.chk_top.setChecked(self._cfg.get("always_on_top", False))
        self.chk_top.setStyleSheet("color: #ffffff; background: transparent;")
        form_win.addRow("", self.chk_top)

        # 开机自启动
        self.chk_auto_start = QCheckBox("开机自动启动")
        self.chk_auto_start.setChecked(self._cfg.get("auto_start", False))
        self.chk_auto_start.setStyleSheet("color: #ffffff; background: transparent;")
        form_win.addRow("", self.chk_auto_start)

        layout.addWidget(grp_win)

        # ===== 分割线 =====
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: rgba(255,255,255,0.1);")
        layout.addWidget(line)

        # ===== 按钮 =====
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.1);
                color: #ffffff;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 6px;
                padding: 6px 18px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.2);
            }
            QPushButton:pressed {
                background: rgba(255,255,255,0.05);
            }
        """)
        btn_box.button(QDialogButtonBox.Ok).setText("✅ 确定")
        btn_box.button(QDialogButtonBox.Cancel).setText("❌ 取消")
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    # ------------------------------------------------------------------
    # 样式
    # ------------------------------------------------------------------
    def _group_style(self):
        return """
            QGroupBox {
                color: rgba(255,255,255,0.85);
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
                font-size: 13px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
            }
            QLabel {
                color: rgba(255,255,255,0.8);
                background: transparent;
                font-size: 12px;
            }
        """

    def _apply_dark_style(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a2e;
                color: #ffffff;
            }
            QSpinBox, QComboBox {
                background: rgba(255,255,255,0.08);
                color: #ffffff;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 5px;
                padding: 4px 8px;
                font-size: 12px;
                min-height: 26px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background: rgba(255,255,255,0.1);
                border: none;
                border-radius: 3px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background: #1a1a2e;
                color: #ffffff;
                border: 1px solid rgba(255,255,255,0.2);
                selection-background-color: rgba(255,255,255,0.15);
            }
            QSlider::groove:horizontal {
                height: 4px;
                background: rgba(255,255,255,0.2);
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #ffd700;
                border: none;
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            QSlider::sub-page:horizontal {
                background: #ffd700;
                border-radius: 2px;
            }
        """)

    # ------------------------------------------------------------------
    # 读取设置结果
    # ------------------------------------------------------------------
    def get_config(self) -> dict:
        cur_text = self.combo_currency.currentText()
        currency = "CNY" if cur_text.startswith("CNY") else "USD"
        return {
            "bg_color": self.btn_bg_color.get_color(),
            "bg_opacity": self.slider_opacity.value(),
            "text_color": self.btn_text_color.get_color(),
            "font_size": self.spin_font.value(),
            "refresh_interval": self.spin_refresh.value(),
            "currency": currency,
            "always_on_top": self.chk_top.isChecked(),
            "auto_start": self.chk_auto_start.isChecked(),
        }
