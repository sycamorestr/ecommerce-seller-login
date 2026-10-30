"""紫鸟登录 super_browser/process1.py drives the Windows client, not a web page."""
from __future__ import annotations

from seller_common import DesktopOnlyLogin

SOURCE = "super_browser/process1.py"
CLIENT_TITLE = "紫鸟浏览器专业版"
VERSIONS = ("V5", "V6")
REASON = "紫鸟登录驱动 Windows 客户端（win32 / UIA），源码没有网页登录地址。版本为 V5 或 V6。"


def ziniao_login(*_args, **_kwargs) -> None:
    raise DesktopOnlyLogin(REASON)
