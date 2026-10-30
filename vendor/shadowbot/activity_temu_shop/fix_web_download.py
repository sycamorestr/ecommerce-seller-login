# fix_download_all.py
import time
import os

from xbot import win32, print
import xbot_visual
from xbot import package

import uiautomation as auto


def main(args):
    # ------------------------------------------------------------
    # 工具：识别浏览器
    # ------------------------------------------------------------
    def _detect_browser(web_type_arg: str) -> str:
        """
        返回 'chrome' | 'edge' | 'purple'
        规则：
        1) 如果 web_type_arg 里出现 'purple' → 紫鸟
        2) 如果参数里出现 'edge' → Edge
        3) 其余视为 Chrome
        """
        wt = str(web_type_arg).lower()
        if 'ziniaobrowser' in wt or 'superbrowser' in wt:
            return 'purple'
        if 'edge' in wt:
            return 'edge'
        return 'chrome'

    # ------------------------------------------------------------
    # 工具：紫鸟二次确认
    # ------------------------------------------------------------
    def _purple_confirm():
        # 循环直到二次确认消失
        for _ in range(10):
            dlg = auto.GetForegroundControl()
            if dlg and '保存地址' in dlg.Name and '非' in dlg.Name and '环境' in dlg.Name:
                btn = dlg.ButtonControl(Name='确定',NameRegex='确认|确定|OK')
                if btn.Exists(0.2):
                    btn.Click()
                    time.sleep(0.5)
                    continue
                else:
                    # 兜底：回车
                    dlg.SendKeys('{ENTER}')
                    time.sleep(0.5)
                    continue

    # ------------------------------------------------------------
    # 工具：Edge 另存为
    # ------------------------------------------------------------
    EDGE_SAVE_AS_BTN = {"type":"win32", "value":"edge_save_as_ele", "timeout":5}   # 你在可视化里配好的“另存为”按钮

    def _edge_click_save_as():
        try:
            win = xbot_visual.win32.window.get(window_type="window_selector",
                                            selector=EDGE_SAVE_AS_BTN,
                                            timeout=5)
            xbot_visual.win32.element.click(window=win,
                                            element=EDGE_SAVE_AS_BTN,
                                            button="left",
                                            timeout=5)
        except Exception:
            pass   # 按钮没出现就继续

    # ------------------------------------------------------------
    # 重写底层 API
    # ------------------------------------------------------------
    raw_download         = xbot_visual.web.element.download
    raw_handle_save      = xbot_visual.web.handle_save_dialog

    def _wrap_download(**kwargs):
        browser = _detect_browser(kwargs.get('web_type', ''))

        # 1. Edge 前置动作：点“另存为”
        if browser == 'edge':
            _edge_click_save_as()

        # 2. 执行影刀原生下载 / 保存
        file_path = raw_download(**kwargs)

        # 3. 紫鸟后置动作：二次确认
        if browser == 'purple':
            try:
                _purple_confirm()
            except:
                pass

        return file_path

    def _wrap_handle(**kwargs):
        browser = _detect_browser(kwargs.get('web_type', ''))

        if browser == 'edge':
            _edge_click_save_as()

        file_path = raw_handle_save(**kwargs)

        if browser == 'purple':
            try:
                _purple_confirm()
            except:
                pass

        return file_path

    # ------------------------------------------------------------
    # 挂到影刀
    # ------------------------------------------------------------
    xbot_visual.web.element.download   = _wrap_download
    xbot_visual.web.handle_save_dialog = _wrap_handle