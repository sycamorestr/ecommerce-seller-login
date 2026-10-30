# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块


import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv

from xbot.win32 import Win32Element, Win32Window
from xbot.web import WebBrowser, WebElement
from xbot._core.retry import Retry
from xbot.errors import UIAError, UIAErrorCode
from xbot import strings
from xbot import logging
from xbot.selector import Selector
import math

import re
import json
import xbot_visual
from typing import Optional, Union, Pattern, List, Tuple
from pathlib import Path

import os
from os import path, system
from os.path import join, expanduser, basename
import xml.etree.ElementTree as ET

from .utils_v6 import find_element_by_bfs, find_element_by_text, wait_element_by_text, find_element_by_text2

def check_input(text):
    xbot.win32.send_keys("^a")
    input_text = xbot.win32.get_selected_text()
    return input_text.strip() == text.strip()

_doc_url = "https://ying-dao.feishu.cn/docx/GvcUdZd1Eo9rJsxVMx8cGe0bnCh?from=from_copylink"

class _StoreNotFound(Exception):
    pass

class SuperBrowser:
    def __init__(self):
        pass

    @property
    def _window(self):
        return xbot.win32.get_by_selector(selector="SB-Client_1")

    @property
    def window(self):
        return self._window._create_element(f"WND:{self._window.hWnd}")

    @property
    def client(self):
        return self._window.find("SB-Client-EX")

    @property
    def login_client(self):
        for _, setlast_error in Retry(timeout=10):
            try:
                return xbot.win32.get_by_selector(selector="SB-Login-Client").find("SB-Login-Client", timeout=0)
            except UIAError as e:
                setlast_error(e)


    @property
    def logout_client(self):
        return xbot.win32.get_by_selector(selector="SB-Logout-Client").find("SB-Logout-Client")


    @property
    def table(self):
        """
        获取账号管理页面表格
        """
        elem = find_element_by_text(self.client, "账号名称")
        table = elem.parent().parent().parent().next_sibling().child_at(0)
        return table


    @staticmethod
    def get_superBrowser_exePath():
        """获取紫鸟浏览器启动文件路径"""
        config_path = join(expanduser('~'), 'AppData', 'Local', 'ShadowBot', 'ChromiumBrowser.config')
        tip_msg = f"紫鸟浏览器插件未正确安装，请用记事本打开 {config_path}, "
        if not path.exists(config_path):
            raise Exception("未安装紫鸟浏览器插件，请根据文档步骤安装紫鸟浏览器插件 {}".format(_doc_url))

        # 解析XML文件
        tree = ET.parse(config_path)
        root = tree.getroot()

        # 查找匹配的产品名称
        matching_nodes = root.findall(".//ChromiumBrowserInfo[ProductName='{}']".format("superbrowser"))
        if len(matching_nodes) == 0:
            raise Exception("请根据文档步骤安装紫鸟浏览器插件 {}".format(_doc_url))
        # 提取ProcessName和ExePath
        node = matching_nodes[0]
        ProcessName, ExePath = node.find('ProcessName').text, node.find('ExePath').text
        assert ProcessName == "superbrowser", tip_msg + "将 ProcessName 修改为 superbrowser"
        return ExePath

    # noinspection PyBroadException
    def start_super_browser(self):
        # 启动紫鸟控制台
        try:
            xbot.win32.get(title="紫鸟浏览器专业版", use_wildcard=True, timeout=1)
            return
        except:
            pass
        try:
            exe_path = self.get_superBrowser_exePath()
            if basename(exe_path) != "superbrowser.exe":
                print("打开紫鸟浏览器客户端")
                os.system(exe_path)
        except:
            pass
        xbot.win32.get(title="紫鸟浏览器专业版", use_wildcard=True, timeout=30)

    def get_table_data(self):
        """
        获取账号管理页面表格数据
        """
        table = self.table
        table_data = []
        for row in table.children():
            for cell in row.children()[1:]:
                table_data.append(cell.get_text())
        # print(json.dumps(table_data, ensure_ascii=False))
        return table_data

    def _find_store_start_cell(self, store_name: str, match_type: str = "相等", timeout: int = 10, *, single_page=False) -> Tuple[Win32Element, Win32Element]:
        """
        查找店铺启动Cell
        """
        if match_type == "模糊":
            # re.escape() 函数用于转义正则表达式中的特殊字符
            store_name_pattern = re.compile(f".*{re.escape(store_name)}.*", re.IGNORECASE)
        else:
            store_name_pattern = re.compile(f"^{re.escape(store_name)}$", re.IGNORECASE)
        for _ in Retry(timeout=timeout, ignore_exception=True):
            try:
                table = self.table
                search_tip_text = table.child_at(0).child_at(0).get_text()
                if search_tip_text is not None and "暂无数据" in search_tip_text:
                    raise Exception("暂无数据 您可以尝试更换筛选条件，再次搜索")

                cell_elems = []
                cells = table.children()
                texts = []
                for index, row in enumerate(cells):
                    cell = row.child_at(1)
                    if not cell:
                        continue
                    text = cell.get_text() or ""
                    texts.append(text)
                    if store_name.upper() in text.upper():
                        cell_elems.append((index, cell))
                result_cells = []
                for index, cell in cell_elems:
                    if match_type != "模糊" and len(result_cells) > 0:
                        break
                    try:
                        self._store_to_view(table.parent(), cell)
                        find_element_by_text(cell, store_name_pattern, timeout=1)
                        result_cell = table.child_at(index).children()[-1]
                        result_cells.append(result_cell)
                        continue
                    except UIAError:
                        pass

                if len(result_cells) == 0:
                    if single_page:
                        raise _StoreNotFound(f"未搜索到指定店铺：{store_name}")
                    raise UIAError(strings.Web_Error_Not_Found_Element.format(store_name), UIAErrorCode.NoSuchElement)

                if len(result_cells) > 1:
                    raise Exception(f"找到多个匹配的店铺，无法唯一确定")

                # 老版的start_btn, more_btn只需要向下找一个children，新版的需要找两个
                if len(result_cells[0].children()) == 2:
                    start_btn, more_btn = result_cells[0].children()
                elif len(result_cells[0].children()) == 1:
                    start_btn, more_btn = result_cells[0].children()[0].children()

                try:
                    start_btn = find_element_by_text(start_btn, re.compile("启 *动"), timeout=timeout)
                    return start_btn, more_btn
                except UIAError:
                    button = find_element_by_text(result_cell, re.compile(r"[\s\S]+"))
                    raise Exception(f"启动按钮文字不是启动：{button.get_text()}")
            except UIAError:
                pass
        raise _StoreNotFound(f"未搜索到指定店铺：{store_name}")


    def wait_store_window(self, timeout: int = 50) -> Win32Window:
        """
        等待店铺浏览器窗口出现
        """
        def filter_func(w: Win32Window):
            try:
                process_name = w.get_detail('process_name')
                if process_name != "superbrowser":
                    return False

                title = w.get_detail('title')
                if title in ["紫鸟浏览器专业版", "另存为", "提示", "翻译此页？"]:
                    return False
                if "影刀RPA网页自动化" in title:
                    return False
                w.activate()

                return w.contains_element('sb-Client') or w.contains_element("sb-Client-firefox-v5")
            except UIAError as e:
                return False

        for _ in Retry(timeout=timeout, ignore_exception=True):
            try:
                if wait_element_by_text(self.client, re.compile(".*在线人员已达上限.*"), timeout=0):
                    xbot.win32.send_keys("{ESCAPE}")
                    raise Exception("在线人员已达上限")
            except UIAError:
                pass

            try:
                window = next((w for w in xbot.win32.get_list() if filter_func(w)), None)
            except UIAError:
                continue
            if not window:
                continue
            return window
        raise UIAError("店铺浏览器窗口未出现", UIAErrorCode.NoSuchElement)

    def get_all_page(self, timeout: int = 10) -> List[WebBrowser]:
        for _ in Retry(timeout=timeout, ignore_exception=True):
            try:
                pages = xbot.web.get_all(mode="superbrowser")
                if pages:
                    return pages
            except UIAError:
                pass
        return xbot.web.get_all(mode="superbrowser")

    def click_open_account(self, store_window: Win32Window):

        sb_root = store_window._create_element(f"WND:{store_window.hWnd}")
        sleep(5)
        for _ in Retry(times=3, ignore_exception=True):
            root_elem = None
            try:
                root_elem = find_element_by_text(sb_root, re.compile(".+ - Chromium"))
            except UIAError:
                pass

            if root_elem:
                root_elem = find_element_by_text(sb_root, re.compile(".+ - Chromium"))
                tab_text = root_elem.get_text().replace(" - Chromium", "")
                root_elem = find_element_by_text(root_elem, "新标签页").parent()
                first_tab = find_element_by_text(root_elem, "关闭").parent()

                # 当前tab不是 `紫鸟浏览器专业版Superbrower-跨境电商环境安全提速系统`, 需要切换到第一个tab
                if tab_text != "紫鸟浏览器专业版Superbrower-跨境电商环境安全提速系统":
                    first_tab.click(move_mouse=True, delay_after=0)
                    root_elem = find_element_by_text(sb_root, re.compile(".+ - Chromium"))
                    tab_text = root_elem.get_text().replace(" - Chromium", "")

                # 如果第一个 tab 是 `紫鸟浏览器专业版Superbrower-跨境电商环境安全提速系统`, 才需要点击打开账号
                if tab_text == "紫鸟浏览器专业版Superbrower-跨境电商环境安全提速系统":
                    client = store_window.find("sb-Client")
                    open_account = find_element_by_text(client, "打开账号", no_child=True)

                    first_tab.click(move_mouse=False, delay_after=0)
                    open_account.click(move_mouse=False, delay_after=0)

                sleep(5)
                root_elem = find_element_by_text(sb_root, re.compile(".+ - Chromium"))
                tab_text = root_elem.get_text().replace(" - Chromium", "")

                # 还在第一个 tab, 可能有风险提示弹窗
                if tab_text == "紫鸟浏览器专业版Superbrower-跨境电商环境安全提速系统":
                    elem = wait_element_by_text(root_elem, re.compile(".*本地设备有多个出口设.*"), timeout=3)
                    if elem:
                        logging.info(elem.get_text())
                        find_element_by_text(root_elem, re.compile("^继 *续$")).click(move_mouse=False)
                        sleep(5)

                    root_elem = find_element_by_text(sb_root, re.compile(".+ - Chromium"))
                    tab_text = root_elem.get_text().replace(" - Chromium", "")

                # 还在第一个 tab, 进入下一次重试
                if tab_text == "紫鸟浏览器专业版Superbrower-跨境电商环境安全提速系统":
                    continue
                break
            else:
                xbot.logging.info(f"点击打开账号")
                open_account = find_element_by_text(sb_root, "打开账号", no_child=False)
                open_account.click(move_mouse=False, delay_after=0)
                return


    @staticmethod
    def close_store():
        def filter_func(w: Win32Window):
            try:
                process_name = w.get_detail('process_name')
                if process_name != "superbrowser":
                    return False

                title = w.get_detail('title')
                if title in ["紫鸟浏览器专业版", "另存为", "提示"]:
                    return False
                w.activate()
                return w.contains_element('sb-Client')
            except UIAError:
                return False

        def close_other_window():
            tip_window = xbot.win32.get_by_selector(selector="提示窗口", timeout=0)
            if tip_window:
                find_element_by_text(tip_window.find("提示窗口"), "确定").click(move_mouse=False, delay_after=0)
            leave_window = xbot.win32.get_by_selector(selector="离开此网站", timeout=0)
            if leave_window:
                find_element_by_text(leave_window.find("离开此网站"), "离开").click(move_mouse=False, delay_after=0)

        def close_window(window: Win32Window):
            try:
                close_other_window()
                window.activate()
                window.close()
                close_other_window()
            except UIAError:
                pass

        for _ in Retry(times=5, ignore_exception=True):
            windows = list(filter(filter_func, xbot.win32.get_list()))
            if len(windows) == 0:
                return
            for window in windows:
                close_window(window)
        raise Exception("关闭店铺超时")


    def is_login_complete(self, login_form: Win32Element, timeout: int = 20):
        for _ in Retry(timeout=timeout, ignore_exception=True):
            try:

                error_tip = wait_element_by_text(login_form, re.compile(".*请重新输入.*"), timeout=0)
                if error_tip:
                    raise Exception(error_tip.get_text())

                login_tip = wait_element_by_text(login_form, re.compile(".*正在登录中.*"), timeout=0)
                if login_tip:
                    continue

                form_field = wait_element_by_text(login_form,  re.compile(".*公司名"), timeout=0)
                if form_field:
                    continue

                return
            except UIAError as e:
                pass
        raise Exception("登录超时")

    def check_plugins(self):
        # 即使当前在紫鸟启动页，使用 get_all 也能正常运行， get_active 择不行
        # 如果 get_all 失败，则表示插件有问题
        for _, set_last_error in Retry(timeout=20):
            try:
                xbot.web.get_all(mode="superbrowser")
                return
            except UIAError as e:
                set_last_error(e)

    def _is_login(self) -> bool:
        """是否已经登录"""
        elem = find_element_by_text(self.window, re.compile("个人中心|立即登录"))
        return "个人中心" in elem.get_text()

    def logout(self):
        for _, set_last_error in Retry(timeout=30):
            try:
                try:
                    elem = find_element_by_text(self.window, re.compile("个人中心|立即登录"))
                    if "立即登录" in elem.get_text():
                        return
                except UIAError as e:
                    raise Exception(e)
                elem.click(move_mouse=False, delay_after=0)
                find_element_by_text(self.logout_client, re.compile("退出登录"), timeout=-1, times=2).click(move_mouse=False, delay_after=0)
                elem = wait_element_by_text(self.window, re.compile("立即登录"), timeout=10)
                if elem:
                    return
                continue
            except UIAError as e:
                set_last_error(e)

    def login(self, company_name: str = "", company_username: str = "", password: str = "", is_fill: bool = False, is_close: bool = True):
        """
        登录
        @params: company_name, 企业名称
        @params: company_username, 企业用户名
        @params: password, 企业密码
        @params: is_fill, 是否填写账号密码
        @params: is_close, 是否退出登录，参数名是为了向老版本兼容
        """
        self.start_super_browser()
        if is_close:
            self.logout()

        elem = find_element_by_text(self.window, re.compile("个人中心|立即登录"), timeout=20)
        find_element_by_text(self.window, re.compile("环境管理"), no_child=True, timeout=30).click(move_mouse=False, delay_after=0)
        if "个人中心" in elem.get_text():
            return

        login_form = find_element_by_text(self.login_client, re.compile("企业登录|验证码登录")) # type: ignore
        if "验证码登录" in login_form.get_text():
            find_element_by_text(self.login_client, "切换企业登录").click(move_mouse=False, delay_after=0) # type: ignore
            login_form = find_element_by_text(self.login_client, "企业登录") # type: ignore
        login_form = login_form.next_sibling()

        # 不填写直接登录当前账号
        if is_fill:
            if not company_name:
                raise ValueError("企业名称不能为空")
            if not company_username:
                raise ValueError("企业用户名不能为空")

            company_elem = find_element_by_text(login_form.child_at(0), re.compile(".*公司名"))
            company_elem.click(move_mouse=False, delay_after=0)
            sleep(2)
            company_elem.input(company_name, click_before_input=True, delay_after=1)
            username_elem = find_element_by_text(login_form, re.compile(".*企业用户名"))
            username_elem.click(move_mouse=False, delay_after=0)
            sleep(2)
            username_elem.input(company_username, click_before_input=True, delay_after=1)

            # 有的用户会记住用户名, 可以选择直接点击登录
            if password:
                password_elem = find_element_by_text(login_form, re.compile(".*密码"))
                password_elem.click(move_mouse=False, delay_after=0)
                password_elem.input(password.strip(), click_before_input=False, delay_after=0)
        sleep(2)
        find_element_by_text(login_form, re.compile("登 *录")).click(move_mouse=False, delay_after=0)
        self.is_login_complete(login_form)

    def _search_to_view(self, search: Win32Element, timeout: int = 10):
        account_btn = find_element_by_text(self.client, "账号管理", timeout=timeout)
        for _ in Retry(times=5, ignore_exception=True):
            left, top, _, _ = search.get_bounding()
            if left == top == 0:
                account_btn.click(move_mouse=False, delay_after=0)
                xbot.win32.send_keys("{RIGHT}" * 50, send_key_delay=0)
            else:
                break

    def _store_to_view(self, parent: Win32Element, elem: Win32Element):
        _, table_top, _, table_height = parent.get_bounding()
        for _ in Retry(times=20, ignore_exception=True):
            left, top, width, height = elem.get_bounding()
            if top + height // 2 >= table_top + table_height or (top == 0 and height == 0):
                parent.hover(delay_after=0)
                xbot.win32.mouse_wheel(wheel_times=5, delay_after=0)
            else:
                break

    def to_account_page(self, timeout):
        # if wait_element_by_text(self.window, "close", timeout=3):
        #     find_element_by_text(self.window, "close", no_child=True).click(delay_after=0)

        # 使用重试机制确保账号管理页面正确加载
        for i in range(3):
            # 查找窗口
            wnd = xbot.win32.get_by_selector(selector="SB-Client")
            client = wnd.find("SB-Client")
            try:
                # 检查是否已经在账号管理页面
                if wait_element_by_text(client, "账号管理", timeout=2):
                    account_manage = find_element_by_text(client, "账号管理", timeout=5, controlType="50019")
                    account_manage.dblclick(move_mouse=False, delay_after=0)
                    return
                window_first_tab = xbot.win32.get_by_selector('SB-first-tab-client').find('SB-first-tab-client')
                # 如果不在账号管理页面，点击环境管理进入
                find_element_by_text(window_first_tab, re.compile("环境管理"), no_child=True).click(move_mouse=False, delay_after=0)

                # 通过标题找到窗口, 再找到元素 再次尝试查找账号管理
                wnd = xbot.win32.get("紫鸟浏览器专业版")
                client = wnd.find("SB-Client-EX")
                account_manage = find_element_by_text(client, "账号管理", timeout=5, controlType="50019")
                account_manage.dblclick(move_mouse=False, delay_after=0)
                find_element_by_text(self.client, "search")
                return
                    

            except UIAError as e:
                title_info = str([ item for item in client.get_all_attributes() if item[0] == "Name"])
                logging.warning(f"尝试进入账号管理页面失败: {e}, 窗口标题为: {title_info}")
                sleep(1)  # 失败后等待1秒再重试
                continue

        # 如果所有重试都失败，抛出异常
        raise Exception(f"无法进入账号管理页面，超时时间: {timeout}秒")


    def open_store(self, store_name: str, *, match_type: str = "相等", privacy: bool = False, is_open: str="点击", timeout=20) -> Tuple[str, Optional[WebBrowser]]:
        if match_type not in ["模糊", "相等"]:
            raise ValueError("匹配类型输入有误，仅支持： 模糊、相等")
        if is_open not in ["点击", "不点击"]:
            raise ValueError("打开账号输入有误，仅支持： 点击、不点击")

        store_name = store_name.strip()
        self.close_store()
        
        self.to_account_page(timeout)
        
        search = find_element_by_text(self.client, "search")
        
        self._search_to_view(search, timeout)
        search_input = search.parent().children()[-2]
        try:
            if wait_element_by_text(self.client, "close", timeout=1):
                
                find_element_by_text(self.client, "close", no_child=True).click(
                    delay_after=1
                )
        except Exception as e:
            pass
        
        search_input.click(move_mouse=False, delay_after=0)

        for i in range(5):
            search_input.input(store_name)
            if check_input(store_name):
                break
        
        search.click(move_mouse=False, delay_after=0)

        # 紫鸟 V5.290.1.15 版本 50条/页及以上 会变成组节点，切换为 20条/页 
        filter_elem = find_element_by_text(self.client, "上一页")
        page_number_root = filter_elem.parent()
        
        first_page_elem = find_element_by_text(page_number_root, "1", no_child=True)
        first_page_elem.click(move_mouse=False, delay_after=1)
        page_number_elem = find_element_by_text(page_number_root, re.compile(r"[\s\S]+条/页"))
        total_record_elem = find_element_by_text(page_number_root, re.compile(r"共\d+条记录"))
        page_size = int(re.sub(r"\D", "", page_number_elem.get_text()))
        total_record = int(re.sub(r"\D", "", total_record_elem.get_text()))
        if page_size >= 50:    
            page_number_elem.click()
            page_select_elem = page_number_elem.parent().parent().child_at(1)
            change_page_ele = find_element_by_text(page_select_elem, '20 条/页')
            change_page_ele.click(move_mouse=False, delay_after=1)
            page_number_elem = find_element_by_text(page_number_root, re.compile(r"[\s\S]+条/页"))
            total_record_elem = find_element_by_text(page_number_root, re.compile(r"共\d+条记录"))
            page_size = int(re.sub(r"\D", "", page_number_elem.get_text()))
            total_record = int(re.sub(r"\D", "", total_record_elem.get_text()))

        target_name = store_name.casefold()
        start_btn = more_btn = None
        for page_num in range(math.ceil(total_record / page_size)):
            if page_num:
                input_ele = find_element_by_text(page_number_root, "跳至")
                input_ele.input("{}{{ENTER}}".format(page_num + 1), delay_after=1, contains_hotkey=True)
            for row in self.table.children():
                cell = row.child_at(1)
                if not cell:
                    continue
                name = (cell.get_text() or "").strip().casefold()
                if target_name in name:
                    try:
                        start_btn, more_btn = self._find_store_start_cell(store_name, match_type, timeout=timeout, single_page=True)
                    except _StoreNotFound:
                        pass
                    break
            if start_btn is not None:
                break
        if start_btn is None:
            raise Exception(f"未搜索到指定店铺：{store_name}")
        if privacy:
            # 隐私模式启动
            more_btn.click(move_mouse=False, delay_after=0)
            find_element_by_text(self.client, "临时模式启动").click(move_mouse=False, delay_after=0)
            tmp_dialog = find_element_by_text(self.client, "本次临时启动配置")
            elem = find_element_by_text(tmp_dialog, re.compile("加载插件 *"), no_child=True)
            elem.screenshot_to_clipboard()
            find_element_by_text(tmp_dialog, re.compile("加载插件 *"), no_child=True).check(delay_after=0)
            find_element_by_text(tmp_dialog, re.compile("启 *动")).click(move_mouse=False, delay_after=0)
        else:
            # 影刀v5 click 方法不生效
            start_btn.hover()
            xbot.win32.mouse_click()

        store_window = self.wait_store_window(timeout)

        full_store_name = store_window.get_detail('title')
        
        web_page = None
        if is_open == "点击":
            self.click_open_account(store_window)
            self.check_plugins() 
            for _ in Retry(timeout=timeout, ignore_exception=True):
                try:
                    web_page = xbot.web.get_active(mode="superbrowser", load_timeout=0)
                    break
                except UIAError:
                    pass

            if web_page is None:
                web_pages = xbot.web.get_all(mode="superbrowser")
                if len(web_pages) == 0:
                    web_page = xbot.web.get_active(mode="superbrowser", load_timeout=0)
                else:
                    web_page = web_pages[0]
            return full_store_name, web_page
        return full_store_name, web_page

    def get_store_list(self, selected_platform=None, timeout=20):
        """获取店铺列表"""
        if selected_platform: selected_platform = selected_platform.strip().upper()
        self.to_account_page(timeout)
        table = self.table
        # 紫鸟 V5.290.1.15 版本 50条/页及以上 会变成组节点，切换为 20条/页 
        filter_elem = find_element_by_text(self.client, "页码")
        page_number_root = filter_elem.parent().parent()
        
        first_page_elem = find_element_by_text(page_number_root, "1", no_child=True)
        first_page_elem.click(move_mouse=False, delay_after=1)
        page_number_elem = find_element_by_text(page_number_root, re.compile(r"[\s\S]+条/页"))
        total_record_elem = find_element_by_text(page_number_root, re.compile(r"共\d+条记录"))
        page_size = int(re.sub(r"\D", "", page_number_elem.get_text()))
        total_record = int(re.sub(r"\D", "", total_record_elem.get_text()))
        if page_size >= 50:    
            page_number_elem.click()
            page_select_elem = page_number_elem.parent().parent().child_at(1)
            change_page_ele = find_element_by_text(page_select_elem, '20 条/页')
            change_page_ele.click(move_mouse=False, delay_after=1)
            page_number_elem = find_element_by_text(page_number_root, re.compile(r"[\s\S]+条/页"))
            total_record_elem = find_element_by_text(page_number_root, re.compile(r"共\d+条记录"))
            page_size = int(re.sub(r"\D", "", page_number_elem.get_text()))
        total = total_record
        platform_store_map = {}
        store_name_list = []
        for page_num in range(math.ceil(total / page_size)):
            if page_num != 0:
                input_ele = find_element_by_text(page_number_root, "跳至")
                input_ele.input("{}{{ENTER}}".format(page_num + 1), delay_after=0, contains_hotkey=True)
            else:
                find_element_by_text(page_number_root, "1", no_child=False).click(move_mouse=False, delay_after=1)
            wait_element_by_text(table, "账号名称", timeout=5)

            # 全选获取所有文本
            xbot.win32.clipboard.clear()
            total_record_elem.click()
            xbot.win32.send_keys("^{a}^{c}")
            total_record_elem.click(delay_after=0.1)
            page_text = xbot.win32.clipboard.get_text()
            result = []
            header_match = re.search(r'账号名称', page_text)
            footer_match = re.search(r'共\s*\d+\s*条记录', page_text)
            if header_match and footer_match:
                header_end = re.search(r'\n\s*\n', page_text[header_match.end():])
                data_start = header_match.end() + header_end.end() if header_end else header_match.end()
                data_text = page_text[data_start:footer_match.start()]
                # 按单空行切分，过短的块持续合并直到够3行（兼容行内空行导致的误拆）
                blocks = re.split(r'\n\s*\n', data_text.strip())
                i = 0
                while i < len(blocks):
                    lines = [l.strip() for l in blocks[i].strip().split('\n') if l.strip()]
                    while len(lines) < 3 and i + 1 < len(blocks):
                        i += 1
                        next_lines = [l.strip() for l in blocks[i].strip().split('\n') if l.strip()]
                        lines = lines + next_lines
                    if len(lines) >= 3:
                        result.append((lines[0], lines[2]))
                    i += 1
                    
            for store_name, platform in result:
                platform = re.sub(r"-[\s\S]*", "", platform).upper()
                # platform = platform.upper()
                store_name_list.append(store_name)
                platform_store_map.setdefault(platform, [])
                platform_store_map.get(platform).append(store_name)

        if not bool(selected_platform): return store_name_list

        if selected_platform not in platform_store_map: raise Exception("没有此平台：{}".format(selected_platform))

        return platform_store_map[selected_platform]

def main(args):
    sb = SuperBrowser()
    # sb.login("xxx", "xxxx", "xxxx", is_fill=True)
    # sb.login(is_fill=False, is_close=True)
    # sb.open_store("huhuanxiasong@tom.com不续费")
    # root = sb._window._create_element(f"WND:{sb._window.hWnd}")
    # find_element_by_text(root, re.compile("企业登录")).click()
    # store_name = "Snuggle usmain"
    # store_name_pattern = re.compile(f".*{re.escape(store_name)}.*", re.IGNORECASE)
    # text = "Snuggle USMain"
    # print(store_name_pattern.match(text))
    # wnd = sb.wait_store_window(50)
    # sb.click_open_account(wnd)

    # 测试打开店铺
    # sb.open_store('jusjojo')
    # 测试获取店铺列表
    store_list = sb.get_store_list("")
    print(store_list)
