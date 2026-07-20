# -*- mode: python ; coding: utf-8 -*-
import sys, os
# 添加项目路径以便导入 version_info
sys.path.insert(0, r'd:\git_geeker\geeker_dev\python_dev\py_fin\itgeeker_gold_widget')
from version_info import VERSION

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[r'd:\git_geeker\geeker_dev\python_dev\py_fin\itgeeker_gold_widget'],
    binaries=[],
    datas=[],
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
