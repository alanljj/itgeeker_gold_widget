# -*- coding: utf-8 -*-
"""生成 PyInstaller VERSIONINFO 对象"""
from PyInstaller.utils.win32.versioninfo import (
    VSVersionInfo,
    FixedFileInfo,
    StringFileInfo,
    StringTable,
    StringStruct,
    VarFileInfo,
    VarStruct,
)

# UTF-8 with BOM for Windows compatibility
UTF8_BOM = '\ufeff'

# 生成 VERSIONINFO
VERSION = VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=(1, 3, 2, 0),
        prodvers=(1, 3, 2, 0),
        mask=0x3F,
        flags=0x0,
        OS=0x40004,   # VOS_NT_WINDOWS32
        fileType=0x1,  # VFT_APP
        subtype=0x0,
        date=(0, 0)
    ),
    kids=[
        StringFileInfo([
            StringTable(
                '040904B0',  # en-US + Unicode
                [
                    StringStruct(u'CompanyName',     u'技术奇客ITGeeker.net'),
                    StringStruct(u'FileDescription', u'ITGeeker Gold Widget - Gold Price Desktop Widget'),
                    StringStruct(u'FileVersion',     u'1.3.2.0'),
                    StringStruct(u'InternalName',  u'ITGeekerGoldWidget'),
                    StringStruct(u'OriginalFilename', u'ITGeekerGoldWidget.exe'),
                    StringStruct(u'ProductName',    u'ITGeeker Gold Widget'),
                    StringStruct(u'ProductVersion', u'1.3.2.0'),
                    StringStruct(u'LegalCopyright', u'Copyright (C) 2024-2026 ITGeeker.net'),
                    StringStruct(u'Comments',       u'https://www.itgeeker.net'),
                ]
            )
        ]),
        VarFileInfo([
            VarStruct(u'Translation', [0x04B0, 1200])
        ])
    ]
)
