# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

from turtle import down
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
import os
import re
import json
import time
import xbot_visual
from typing import Optional, Union, Pattern, List, Tuple
from pathlib import Path
 
from .utils_v6 import *
import uiautomation as auto

import threading
import pythoncom

import ctypes
from ctypes import wintypes        
user32 = ctypes.windll.user32

# Win32 常量
WM_KEYDOWN = 0x0100
WM_KEYUP   = 0x0101
VK_RETURN  = 0x0D

class ZiNiao:
    def __init__(self):
        self._basic_window: Optional[Win32Window] = None
        self._full_window: Optional[Win32Window] = None

    
    @property
    def table(self) -> Win32Element:
        """
        获取账号管理页面表格
        """
        account_text_win = find_element_by_text(self.full_client, "账号")
        account_text_win.click(move_mouse=False, delay_after=0)
        elem = find_element_by_text(self.full_client, "账号名称")
        table = elem.parent().parent().parent().next_sibling().child_at(0)  # 旧版的是表格节点
        symbol_ele_list = elem.parent().parent().parent().next_sibling().child_at(0).child_at(0).children() # 通过向下查找元素获取子元素组，如果子元素组大于1为旧版本
        if  len(symbol_ele_list) <= 1 and symbol_ele_list[0].get_text() != '暂无数据':  # 查找不到店铺时的ui 新版和旧版一样
            table = elem.parent().parent().parent().next_sibling().child_at(0).child_at(0).child_at(0)  # 新版的是组节点
        return table
    
    @property
    def basic_client(self) -> Optional[Win32Element]:
        """精简面板"""
        if self._basic_window:
            return self._basic_window.find("ziniao-client")
        windows = self._windows()
        for window in windows:
            window.activate()
            client = window.find("ziniao-client")
            _, _, width, height = client.get_bounding()


            # if "notification" in ziniao_document_url:
            #     continue

            if width < height:
                self._basic_window = window
                return client
    
    @property
    def full_client(self) -> Win32Element:
        """完整面板，获取不到就通过精简面板打开"""
        if self._full_window:
            return self._full_window.find("ziniao-client", timeout=0)

        basic_client_list = []
        for window in self._windows():
            try:
                window.activate()
                client = window.find("ziniao-client", timeout=0)
            except UIAError:
                continue
            _, _, width, height = client.get_bounding()

            ziniao_selector_json = package.selector("ziniao-client").value 
            ziniao_selector_json["framework"] = "win32"
            ziniao_selector = Selector(ziniao_selector_json)
            ziniao_document_url = xbot.win32.get_by_selector(ziniao_selector).find(ziniao_selector).get_attribute(30045)
            
            if "notification" in ziniao_document_url:
                continue

            if width > height:
                self._full_client = client
                self._full_window = window
                return client
            else:
                basic_client_list.append(client)
        
        for basic_client in basic_client_list:
            try:
                # 处理11弹窗
                try:
                    # 稍后更新弹窗
                    if wait_element_by_text(basic_client, "稍后刷新", timeout=1):
                        
                        find_element_by_text(basic_client, "稍后刷新", no_child=True).click(
                            delay_after=1
                        )
                except Exception as e:
                    pass
                # caret-down 第二个兄弟元素是 打开完整面板按钮
                find_element_by_text(basic_client, "caret-down", timeout=-1, times=1).next_sibling().next_sibling().click()
                sleep(3)
                break
            except:
                pass
            
            
        for window in self._windows():
            client = window.find("ziniao-client")
            _, _, width, height = client.get_bounding()
            if width > height:
                self._full_client = client
                self._full_window = window
                return client
        
        raise Exception("未找到紫鸟完整面板")
    
    def _windows(self) -> List[Win32Window]:
        """获取所有紫鸟v6窗口"""
        def filter_func(w: Win32Window):
            try:
                process_name = w.get_detail('process_name')
                if process_name != "ziniao" and process_name != "ziniaobrowser":
                    return False
                
                title = w.get_detail('title')
                if title != "紫鸟浏览器":
                    return False
                return True                
            except UIAError:
                return False
        

        for _ in Retry(times=2, ignore_exception=True):
            try:
                windows = list(filter(filter_func, xbot.win32.get_list()))
            except UIAError:
                continue
            if not windows:
                continue
            return windows
        return []
    
    def _is_login_complete(self, company_login_elem: Win32Element, timeout: int = 5):
        """
        是否登录完成
        利用 company_login_elem 元素文本变化来判断登录成功
        """        
        for _ in Retry(timeout=timeout, ignore_exception=True):
            try:
                if self.basic_client:
                    error_tip = wait_element_by_text(self.basic_client, re.compile("用户名.*密码错误"), timeout=0)
                    if error_tip:
                        raise Exception(error_tip)
                # company_login_elem 元素失效或者文字改变, 则表示登录成功
                try:
                    if company_login_elem.get_text() != "企业登录":
                        return
                except UIAError:
                    return
                
            except UIAError as e:
                pass
        # TODO: 后台进入的可能不是极简面板, 导致找不到窗口报错, 暂时忽略
        # raise Exception("登录超时")

    def _miss_kernel(self, full_client: Win32Element, times=2) -> bool:
        try:
            find_element_by_text(full_client, "请下载指定内核", timeout=-1, times=times)
            return True
        except UIAError:
            pass
        return False

    def _find_store_start_cell(self, store_name: str, match_type: str = "相等", timeout: int = 10) -> Win32Element:
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
                if search_tip_text is not None and ("暂无数据" in search_tip_text or "没有搜索到相关内容" in search_tip_text):
                    raise Exception("暂无数据 您可以尝试更换筛选条件，再次搜索")

                cell_elems = []
                cells = table.children()
                for index, row in enumerate(cells):
                    cell = row.child_at(1)
                    if cell.get_text() is None: # 为空说明是新版的表格
                        cell = row.child_at(1).child_at(0).child_at(0).child_at(0).child_at(0)  # 得找到底层文本节点
                    if not cell:
                        continue
                    if store_name.upper() in cell.get_text().upper():
                        cell_elems.append((index, cell))

                result_cells: List[Win32Element] = []
                for index, cell in cell_elems:
                    if match_type != "模糊" and len(result_cells) > 0:
                        break
                    try:
                        find_element_by_text(cell, store_name_pattern, no_child=True, timeout=0)
                        result_cell = table.child_at(index).children()[-1]
                        result_cells.append(result_cell)
                        break
                    except UIAError:
                        pass

                if len(result_cells) == 0:
                    raise UIAError(strings.Web_Error_Not_Found_Element.format(store_name), UIAErrorCode.NoSuchElement)

                if len(result_cells) > 1:
                    raise Exception(f"找到多个匹配的店铺，无法唯一确定")

                start_btn = result_cells[0]

                for _ in Retry(timeout=20, ignore_exception=True):
                    start_btn_text = start_btn.get_text()
                    print(start_btn_text)
                    if not start_btn_text or not re.compile("启 *动").search(start_btn_text):
                        if wait_element_by_text(start_btn, re.compile("启 *动"), timeout=0):
                            return start_btn.child_at(0)
                        continue
                    else:
                        return start_btn.child_at(0)

                raise Exception(f"启动按钮文字不是启动：{start_btn_text}")
            except UIAError:
                pass
        raise Exception(f"未搜索到指定店铺：{store_name}")

    def _wait_store_window(self, timeout: int = 20) -> Win32Window:
        """
        等待店铺浏览器窗口出现
        """
        for retrytime, _ in Retry(timeout=timeout, ignore_exception=True):
            try:
                if (retrytime + 1) % 5 == 0:
                    if self._miss_kernel(self.full_client, times=1):
                        raise Exception("启动店铺失败，请下载指定内核，下载升级内核后即可启动")
                window = next((w for w in xbot.win32.get_list() if self.is_store_window(w)), None)
                if not window:
                    continue
                return window              
            except UIAError:
                pass

        raise UIAError("店铺浏览器窗口未出现", UIAErrorCode.NoSuchElement)
        
    def _click_open_account(self, store_window: Win32Window):
        """
        点击打开账号按钮
        """
        xbot.app.dialog.show_notifycation("等待店铺浏览器窗口稳定", placement="top", timeout=5)
        sleep(5)        
        store_client = store_window.find('ziniao-store-client')
        search_tab = find_element_by_text(store_window.find('ziniao-store-window'), "新标签页")
        tab_root = search_tab.parent().parent()
        # first_tab = find_element_by_text(tab_root, "关闭").parent()
        
        # 地址栏的父元素
        pane_root = search_tab.parent().parent()
        # 不管什么情况都去点击第一页
        # first_tab.click(move_mouse=False, delay_after=0)
        xbot.win32.send_keys("^{1}")
        store_client = store_window.find('ziniao-store-client')
        open_account = find_element_by_text(store_client, "打开账号", no_child=True)
        # first_tab.click(move_mouse=False, delay_after=0)
        xbot.win32.send_keys("^{1}")
        open_account.click(move_mouse=False, delay_after=0)
        # 兼容处理"继续"弹窗
        try:
            if wait_element_by_text(store_client, "继 续", timeout=2):
                find_element_by_text(store_client, "继 续", timeout=2).click(delay_after=1)
        except Exception:
            pass
        
    @staticmethod
    def is_store_window(w: Win32Window) -> bool:
        try:
            process_name = w.get_detail('process_name')
            if process_name != "ziniaobrowser":
                return False
            
            title = w.get_detail('title')
            if title in ["紫鸟浏览器", "另存为", "提示", "翻译此页？"]:
                return False
            if "影刀RPA网页自动化" in title:
                return False
            w.activate()
            return w.contains_element('ziniao-store-client')
        except UIAError as e:
            xbot.print(e)            
            return False
        
    def _close_store(self):
        """关闭店铺浏览器，不能直接强制杀死进程，会有风控提示"""
        def close_window(window: Win32Window):             
            try:
                tip_window = xbot.win32.get_by_selector(selector="提示窗口", timeout=0)
                if tip_window:
                    find_element_by_text(tip_window.find("提示窗口"), "确定").click(move_mouse=False, delay_after=0)
                window.activate() 
                window.close()
                tip_window = xbot.win32.get_by_selector(selector="提示窗口", timeout=0)
                if tip_window:
                    find_element_by_text(tip_window.find("提示窗口"), "确定").click(move_mouse=False, delay_after=0)
            except UIAError:
                pass   
               
        for _ in Retry(times=3, ignore_exception=True):
            windows = list(filter(self.is_store_window, xbot.win32.get_list()))
            if len(windows) == 0:
                return
            for window in windows:
                close_window(window)
        raise Exception("关闭店铺超时")

    def check_plugins(self):
        # 即使当前在紫鸟启动页，使用 get_all 也能正常运行， get_active 择不行
        # 如果 get_all 失败，则表示插件有问题
        for _, set_last_error in Retry(timeout=100):
            try:
                xbot.web.get_all(mode="ziniaobrowser")
                return
            except UIAError as e:
                set_last_error(e)

    def scroll_to_view(self, target_elem: Win32Element):
        """
        将表格内元素滚动到表格视图中
        """
        view = self.table.parent()
        view.window.activate()
        view_rect = Rect(view)
        for _ in Retry(times=10, ignore_exception=True):
            target_rect = Rect(target_elem)
            if target_rect.center_y < view_rect.top:
                xbot.win32.mouse_move(view_rect.center_x, view_rect.center_y, delay_after=0)
                xbot.win32.mouse_wheel('up', delay_after=0)
            elif target_rect.center_y > view_rect.bottom:
                xbot.win32.mouse_move(view_rect.center_x, view_rect.center_y, delay_after=0)
                xbot.win32.mouse_wheel('down', delay_after=0)
            else:
                return
        raise Exception("目标元素不在可点击范围内，且无法滚动到视图中")

    def logout(self):
        """
        退出登录，找到任意一个面板都可以进行退出登录
        """
        for _ in Retry(times=2, ignore_exception=True):
            try:
                # 通过精简面板退出
                if self.basic_client:
                    caret_down = wait_element_by_text(self.basic_client, "caret-down", timeout=0)
                    if caret_down:
                        caret_down.click(move_mouse=False)
                        find_element_by_text(self.basic_client, "退出登录").click(move_mouse=False)
                        return
                    
                    if wait_element_by_text(self.basic_client, "企业登录"):
                        return
                
                # 通过完整面板退出
                find_element_by_text(self.full_client, "caret-down", timeout=0).click(move_mouse=False)
                find_element_by_text(self.full_client, "退出登录").click(move_mouse=False)
                return
            except UIAError:
                pass

    def login(self, company_name: str = "", company_username: str = "", password: str = "", is_fill: bool = False, is_close: bool = True):
        """
        登录
        @params: company_name, 企业名称
        @params: company_username, 企业用户名
        @params: password, 企业密码
        @params: is_fill, 是否填写账号密码
        @params: is_close, 是否退出登录，参数名是为了向老版本兼容
        """
        if is_close:
            self.logout()
        basic_client = self.basic_client
        assert basic_client, "未找到紫鸟精简面板"
        try:
            find_element_by_text(basic_client, "企业登录").click(move_mouse=False, delay_after=0)
        except:
            print('当前店铺已登录')
            return 
            
        # 不填写直接登录当前账号
        if is_fill:
            if not company_name:
                raise ValueError("企业名称不能为空")
            if not company_username:
                raise ValueError("企业用户名不能为空")
            company_elem = find_login_input_elem_v6(basic_client, "公司名")
            company_elem.click(move_mouse=False, delay_after=0)
            company_elem.input(company_name, click_before_input=False, delay_after=1)
            xbot.win32.send_keys("{TAB}")
            username_elem = find_login_input_elem_v6(basic_client, "用户名")
            # 兼容输入公司名有下拉框的情况
            find_element_by_text(basic_client, "企业登录").click(move_mouse=False, delay_after=0)
            username_elem.click(move_mouse=False, delay_after=0)
            username_elem.input(company_username, click_before_input=False, delay_after=0)
            
            # 有的用户会记住用户名, 可以选择直接点击登录
            if password:
                xbot.win32.send_keys("{TAB}")
                password_elem = find_login_input_elem_v6(basic_client, "密码")
                # 兼容输入用户名有下拉框的情况
                find_element_by_text(basic_client, "企业登录").click(move_mouse=False, delay_after=0)
                password_elem.click(move_mouse=False, delay_after=0)
                password_elem.input(password, click_before_input=False, delay_after=0)
                
        find_element_by_text(basic_client, re.compile("登 *录")).click(move_mouse=False, delay_after=0)
        self._is_login_complete(find_element_by_text(basic_client, "企业登录"), 10)

    def open_store(self, store_name: str, *, privacy:bool = False, match_type: str="相等", is_open: str="点击", timeout: int=20, user_limit="取 消") -> Tuple[str, Optional[WebBrowser]]:
        if match_type not in ["模糊", "相等"]: 
            raise ValueError("匹配类型输入有误，仅支持： 模糊、相等")
        if is_open not in ["点击", "不点击"]: 
            raise ValueError("打开账号输入有误，仅支持： 点击、不点击")
        
        store_name = store_name.strip()
        self._close_store()            
        full_client = self.full_client
        # 下载内核弹窗
        if self._miss_kernel(full_client, times=1):
            find_element_by_text(full_client, re.compile("取 *消")).click(move_mouse=False, delay_after=0)
        # 处理11弹窗
        try:
            # 稍后更新弹窗
            if wait_element_by_text(full_client, "close-circle", timeout=1):
                find_element_by_text(full_client, "close-circle", no_child=True).click(
                    delay_after=1
                )
        except Exception as e:
            pass

        # 点击账号管理面板
        account_text_win = find_element_by_text(full_client, "账号")
        account_text_win.click(move_mouse=False, delay_after=0)
        
        # 处理资源到期后将被注销，无法找回，请尽快续费 close
        try:
            # 稍后更新弹窗
            if wait_element_by_text(full_client, "close", timeout=1):
                find_element_by_text(full_client, "close", no_child=True).click(
                    delay_after=1
                )
        except Exception as e:
            pass

        search = find_element_by_text(full_client, "search")


        # # 6.26.3.28 版本临时兼容
        # try:
        #     tmp_search_input = find_element_by_text(full_client, "请输入关键词", timeout=3)
        # except:
        #     tmp_search_input = None


        search_input = search.parent().children()[-2].children()[0]
        search_input.click(move_mouse=False, delay_after=0)
        retry_input(search_input, store_name)
        search.click(move_mouse=False, delay_after=2)

        # 先切换每页的数量为 20条/页
        filter_elem = find_element_by_text(self.full_client, "上一页")
        page_number_root = filter_elem.parent()
        
        first_page_elem = find_element_by_text(page_number_root, "1", no_child=True)
        first_page_elem.click(move_mouse=False, delay_after=1)
        page_number_elem = find_element_by_text(page_number_root, re.compile(r"[\s\S]+条/页"))
        total_record_elem = find_element_by_text(page_number_root, re.compile(r"共\d+条记录"))
        page_size = int(re.sub(r"\D", "", page_number_elem.get_text()))
        total_record = int(re.sub(r"\D", "", total_record_elem.get_text()))
        # 紫鸟 6.25.23.9版本 50条/页及以上 会变成组节点，切换为 20条/页
        if page_size >= 50:    
            page_number_elem.click()
            page_select_elem = page_number_elem.parent().parent().child_at(1)
            change_page_ele = find_element_by_text(page_select_elem, '20 条/页')
            change_page_ele.click(move_mouse=False, delay_after=1)
            page_number_elem = find_element_by_text(page_number_root, re.compile(r"[\s\S]+条/页"))
            total_record_elem = find_element_by_text(page_number_root, re.compile(r"共\d+条记录"))
            page_size = int(re.sub(r"\D", "", page_number_elem.get_text()))

        start_btn = self._find_store_start_cell(store_name, match_type, timeout=timeout)
        self.scroll_to_view(start_btn)
        if privacy:
            # 隐私模式启动
            start_btn.click(move_mouse=False, delay_after=0, anchor=('middleRight', -5, 0))
            find_element_by_text(full_client, "临时模式启动").click(move_mouse=False, delay_after=0)
            tmp_dialog = find_element_by_text(full_client, "本次临时启动配置")
            find_element_by_text(tmp_dialog, re.compile("加载插件 *")).check(delay_after=0)
            find_element_by_text(tmp_dialog, re.compile("启 *动")).click(move_mouse=False, delay_after=0)
        else:
            # 正常模式启动
            # 可能会存在点击失效，多点几次
            for _ in Retry(timeout=10, ignore_exception=True):
                start_btn_text = start_btn.parent().get_text()
                if start_btn_text != '启动':
                    break
                else:
                    start_btn.click(move_mouse=False, delay_after=0)
            if user_limit:
                if wait_element_by_text(full_client, "exclamation-circle 当前在线人员已达上限", timeout=1):
                    find_element_by_text(full_client, user_limit, no_child=True).click(
                        delay_after=1,
                    )
                    if user_limit != "申请访问名额":
                        return

        store_window = self._wait_store_window(timeout)
        full_store_name = store_window.get_detail('title')
        web_page = None
        if is_open == "点击":
            for _ in range(3):
                try:
                    self._click_open_account(store_window)
                    self.check_plugins()
                    for _, set_last_error in Retry(timeout=30, ignore_exception=True):
                        try:
                            web_page = xbot.web.get_active(mode="ziniaobrowser", load_timeout=0)
                            break
                        except UIAError:
                            pass
                    if web_page is None:
                        web_pages = xbot.web.get_all(mode="ziniaobrowser")
                        if len(web_pages) == 0:
                            web_page = xbot.web.get_active(mode="ziniaobrowser", load_timeout=0)
                        else:
                            web_page = web_pages[0]            
                    return full_store_name, web_page
                except Exception as e:
                    pass
        return full_store_name, web_page
 
    def get_store_list(self, selected_platform: Optional[str] = None) -> List[str]:
        """
        获取账号管理页面店铺名称列表
        """
        def wait_loaded(last_text: str):
            """通过第一行店铺名称是否变化来判断是否加载完成"""
            for _ in Retry(timeout=5, ignore_exception=True):
                try:
                    elems = table.child_at(0).children()
                    if len(elems) < 2:
                        continue
                    cell = elems[1]
                    if not cell.get_text():
                        continue
                    if last_text == re.sub(r" .+$", "", cell.get_text()):
                        continue
                    return
                except UIAError as e:
                    print(e)

        table = self.table
        search_tip_text = table.child_at(0).child_at(0).get_text()
        if search_tip_text is not None and ("暂无数据" in search_tip_text or "没有搜索到相关内容" in search_tip_text):
            return []
        
        full_client = self.full_client
        filter_elem = find_element_by_text(self.full_client, "left")
        search = find_element_by_text(full_client, "search")
        search_input = search.parent().children()[0]
        search_input.click(move_mouse=False, delay_after=0)
        retry_input(search_input, "")
        search.click(move_mouse=False, delay_after=2)

        page_number_root = filter_elem.parent().parent()
    
        first_page_elem = find_element_by_text(page_number_root, "1", no_child=True)
        first_page_elem.click(move_mouse=False, delay_after=1)
        page_number_elem = find_element_by_text(page_number_root, re.compile(r"[\s\S]+条/页"))
        total_record_elem = find_element_by_text(page_number_root, re.compile(r"共\d+条记录"))
        page_size = int(re.sub(r"\D", "", page_number_elem.get_text()))
        total_record = int(re.sub(r"\D", "", total_record_elem.get_text()))
        
        # 紫鸟 6.25.3.38版本 100条/页及以上 会变成组节点，切换为 50条/页
        if page_size > 20:    
            page_number_elem.click()
            page_select_elem = page_number_elem.parent().parent().child_at(1)
            change_page_ele = find_element_by_text(page_select_elem, '20 条/页')
            change_page_ele.click()
            page_number_elem = find_element_by_text(page_number_root, re.compile(r"[\s\S]+条/页"))
            total_record_elem = find_element_by_text(page_number_root, re.compile(r"共\d+条记录"))
            page_size = int(re.sub(r"\D", "", page_number_elem.get_text()))
            total_record = int(re.sub(r"\D", "", total_record_elem.get_text()))
            table = self.table  # 更新table节点
            
        page_total = int((total_record + page_size - 1) / page_size)
        if page_total != 1:
            page_input = find_element_by_text(page_number_root, "跳至").next_sibling()
        # 将第一个店铺名称作为初始值
        last_text = ""        
        store_name_list = []
        for page_num in range(page_total):
            table.window.activate()
            if page_num != 0:
                page_input.input(str(page_num + 1) + "{ENTER}", contains_hotkey=True)
            else:
                first_page_elem.click(move_mouse=False, delay_after=0)
            sleep(1)
            wait_loaded(last_text)

            page_store_name_list = []
            for row in table.children():
                name_cell, platform_cell = row.children()[1:3]
                
                name_cell = name_cell.get_text()
                if name_cell.strip().endswith("edit"):
                    name_cell = name_cell.replace("edit", "").strip()
                text = re.sub(r"\s+", " ", name_cell.strip())

                store_name, _ = text.rsplit(" ", 1)
                platform = platform_cell.get_text() 
                if selected_platform and selected_platform.upper() != platform.split("-")[0].upper():
                    continue
                page_store_name_list.append(store_name)
                
            if page_store_name_list:
                last_text = page_store_name_list[0]
                store_name_list.extend(page_store_name_list)
        
        return store_name_list


def download_handler(web_page: xbot.web.WebBrowser, element: Union[WebElement, Selector, str], file_folder: str, file_name: str, wait_time: int = 300, dialog_timeout=20) -> str:
    
    is_completed = False
    wait_time = int(wait_time)
    dialog_timeout = int(dialog_timeout)
    
    if isinstance(element, xbot.selector.Selector) or isinstance(element, str):
        element = web_page.find(element, timeout=5)

    assert isinstance(element, xbot.web.WebElement), Exception("传入的元素类型不正确")  

    def wait_and_send_enter(
        window_title_list: list,
        class_name: str = "Chrome_WidgetWin_1",
        timeout: int = 20,
        interval: float = 0.3,
        ):
        """
        循环查找指定窗口，找到后发送回车
        """
        nonlocal is_completed
        end_time = time.time() + timeout + 5
        hwnd = None

        while time.time() < end_time and not is_completed :
            for window_title in window_title_list:
                hwnd = user32.FindWindowW(class_name, window_title)
                if hwnd:
                    # 置前（可选，但强烈建议）
                    user32.SetForegroundWindow(hwnd)

                    # 发送回车
                    user32.SendMessageW(hwnd, WM_KEYDOWN, VK_RETURN, 0)
                    user32.SendMessageW(hwnd, WM_KEYUP, VK_RETURN, 0)

                time.sleep(interval)

        return False

                
    confirm_thread = threading.Thread(
        target=wait_and_send_enter,
        kwargs={
            "window_title_list": ["下载保存地址非当前环境指定保存地址", "保存地址非本环境目录"],
            "timeout": dialog_timeout,
        },
        daemon=True
    )
    confirm_thread.start()

    # TODO: 不带文件扩展名的时候无法通过等待文件完成进行创建
    # file_path = element.download(file_folder, file_name=file_name, wait_complete=True, wait_complete_timeout=wait_time, dialog_timeout=dialog_timeout)
    use_custom_filename = bool(file_name)
    file_path = xbot_visual.web.element.download(browser=web_page, scene="Button", download_button=element, download_url=None, file_folder=file_folder, use_custom_filename=use_custom_filename, file_name=file_name, save_behavior="overwrite", wait_complete=True, wait_complete_timeout=wait_time, simulate=False, clipboard_input=False, input_type="automatic", wait_dialog_appear_timeout=dialog_timeout, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000")

    is_completed = True
    confirm_thread.join()
    return file_path


def upload_handler(web_page: xbot.web.WebBrowser, selector_or_element, file_names: list, simulative: bool=False, dialog_timeout: int=20):
    dialog_timeout = int(dialog_timeout)
    element = None
    if isinstance(selector_or_element, xbot.selector.Selector) or isinstance(selector_or_element, str):
        element = web_page.find(selector_or_element, timeout=5)
    elif isinstance(selector_or_element, xbot.web.WebElement):
        element = selector_or_element
    else:
        raise ValueError("传入的元素类型不正确")

    dialog_timeout = int(dialog_timeout)
    element.upload(file_names, simulative=simulative, dialog_timeout=dialog_timeout)

    sleep(2)
    for _ in Retry(timeout=5, ignore_exception=True):
        try:
            window = xbot.win32.get_by_selector('上传提示窗口', timeout=0)
            if window:
                window.activate()
                client = window.find('上传提示窗口')
                find_element_by_text(client, "确定").click(delay_after=1)
                sleep(1)
                window = xbot.win32.get_by_selector('上传提示窗口', timeout=0)
                if window:
                    continue
                else:
                    return 
        except UIAError as e:
            print(f'上传文件到紫鸟upload_handler失败----{e}')
            pass


def main(args):
    # web_page = xbot.web.get_active('superbrowser')
    # download_handler(web_page=web_page, element=package.selector('导出-jx'), file_folder=r'D:\env_text\紫鸟\1', file_name='',dialog_timeout=20)
    zn = ZiNiao()
    # zn.full_client
    store_name_list = zn.get_store_list('Shopee')
    print(f"[v6 Shopee] 数量={len(store_name_list)}")
    print(store_name_list)
    # print(store_name_list)
    # zn.open_store('凡腾US')
    # store_list = zn.get_store_list()
    # print(store_list)