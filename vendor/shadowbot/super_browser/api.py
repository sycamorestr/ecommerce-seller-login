import xbot

from .ziniao_v6_uia import ZiNiao
from .ziniao_v5 import SuperBrowser
from .utils_v6 import  Version, get_version

from typing import Tuple, Union, Optional


def to_account_page():
    if get_version() != Version.V5:
        # V6不需要这个指令
        print("V6不需要 进入账号管理页面 指令")
        return
    sb = SuperBrowser()
    sb.to_account_page(timeout=120)


# 后续 V5 看情况改成 V6 实现方式
def open_store(store_name, match_type, *, privacy=False, is_open="点击", timeout=20, user_limit="取 消") -> Tuple[str, Optional[xbot.web.WebBrowser]]:
    if get_version() == Version.V5:
        sb = SuperBrowser()
        return sb.open_store(store_name, privacy=privacy, match_type=match_type, is_open=is_open, timeout=timeout)
    else:
        ziniao = ZiNiao()
        return ziniao.open_store(store_name, privacy=privacy, match_type=match_type, is_open=is_open, timeout=timeout, user_limit=user_limit)
        

def login(company_name="", company_username="", password="", is_fill=True, is_close=False, version="V5"):
    if version == Version.V5.value:
        sb = SuperBrowser()
        sb.login(company_name, company_username, password, is_fill, is_close)
    else:
        ziniao = ZiNiao()
        ziniao.login(company_name, company_username, password, is_fill, is_close)    


def get_store_list(selected_platform: Optional[str] = None):
    if get_version() == Version.V5:
        sb = SuperBrowser()
        return sb.get_store_list(selected_platform)
    else:
        ziniao = ZiNiao()
        return ziniao.get_store_list(selected_platform)


def test_open_store():
    if 'xbot_extensions' not in __file__:
        store_name = '百度'
        match_type = '相等'
        is_open = '点击'
        open_store(store_name=store_name, match_type=match_type, is_open=is_open)
        exit()


def main(args):
    test_open_store()