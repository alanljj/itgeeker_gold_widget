"""
ITGeeker Gold Widget - 配置管理模块
开发者: 技术奇客ITGeeker.net
网址: https://www.itgeeker.net
版本: v1.3.1.0
"""

import json
import os

APP_NAME = "ITGeeker Gold Widget"
APP_VERSION = "v1.3.1.0"
APP_DEVELOPER = "技术奇客ITGeeker.net"
APP_URL = "https://www.itgeeker.net"
APP_EMOJI = "🧈"

# 配置文件路径（存放在用户目录下）
CONFIG_DIR = os.path.join(os.path.expanduser("~"), "itgeeker_widget_config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config_gold.json")

DEFAULT_CONFIG = {
    # 窗口位置和大小
    "window_x": 100,
    "window_y": 100,
    "window_width": 320,
    "window_height": 180,
    "always_on_top": False,

    # 外观
    "bg_color": "#1a1a2e",
    "bg_opacity": 220,          # 0-255
    "font_size": 14,
    "text_color": "#ffffff",

    # 数据刷新间隔（秒）
    "refresh_interval": 60,

    # 价格单位（CNY/USD）
    "currency": "CNY",

    # 开机自启动
    "auto_start": False,
}


def set_auto_start(enable: bool) -> bool:
    """设置/取消开机自启动（Windows注册表）"""
    import sys
    import winreg

    app_name = "ITGeekerGoldWidget"
    exe_path = sys.executable

    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        if enable:
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
        else:
            try:
                winreg.DeleteValue(key, app_name)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


def is_auto_start_enabled() -> bool:
    """检查是否已启用开机自启动"""
    import sys
    import winreg

    app_name = "ITGeekerGoldWidget"
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_READ
        )
        try:
            value, _ = winreg.QueryValueEx(key, app_name)
            winreg.CloseKey(key)
            return bool(value)
        except FileNotFoundError:
            winreg.CloseKey(key)
            return False
    except Exception:
        return False


def load_config() -> dict:
    """加载配置，不存在则返回默认值"""
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # 用默认值补全缺失字段
        cfg = DEFAULT_CONFIG.copy()
        cfg.update(data)
        return cfg
    except Exception:
        return DEFAULT_CONFIG.copy()


def save_config(cfg: dict) -> None:
    """保存配置到文件"""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
