# -*- mode: python ; coding: utf-8 -*-
import sys, os
# 添加项目路径以便导入 version_info
sys.path.insert(0, os.path.dirname(os.path.abspath(SPEC)))
from version_info import VERSION

block_cipher = None

# 项目根目录（spec 文件所在目录）
PROJECT_ROOT = os.path.dirname(os.path.abspath(SPEC))
ICON_PATH = os.path.join(PROJECT_ROOT, 'img', 'gold_widget.ico')

a = Analysis(
    ['main.py'],
    pathex=[PROJECT_ROOT],
    binaries=[],
    datas=[
        # 打包时把 img/ 目录下的图标一并带进 exe 资源目录（运行时通过 resource_path 加载）
        (os.path.join(PROJECT_ROOT, 'img', 'gold_widget.ico'),
         'img'),
        (os.path.join(PROJECT_ROOT, 'img', 'gold_widget_310x310_Logo.png'),
         'img'),
    ],
    hiddenimports=[
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtSvg',
        'PySide6.QtXml',
        'shiboken6',
        'requests',
        'urllib3',
        'charset_normalizer',
        'certifi',
        'config',
        'gold_api',
        'main_window',
        'settings_dialog',
        'tray',
    ],
    hookspath=[],
    hooksconfig={},
    bridges=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ITGeekerGoldWidget',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,     # 无控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_PATH,    # ⭐ EXE 文件图标（任务栏 / 资源管理器 / 快捷方式）
    version=VERSION,  # Windows 版本信息
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='',  # 输出到项目根目录
)
