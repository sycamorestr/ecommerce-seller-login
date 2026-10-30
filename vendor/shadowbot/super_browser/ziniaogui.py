# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
import uiautomation as auto

class ZiNiao:
    def __init__(self):
        # 初始化紫鸟窗口
        self.ziniao_window = self.__find_ziniao_window()

    def __find_ziniao_window(self):
        """
        查找紫鸟窗口
        """
        try:
            window = auto.PaneControl(searchDepth=1, Name='紫鸟浏览器')
            window.SetActive(waitTime=0)
            if not window.Exists(0, 0):
                raise Exception("未找到紫鸟浏览器，请确保其已打开")
            return window
        except Exception as e:
            print(f"错误: {e}")
            return None

    def __click_control(self, control_name: str, searchDepth: int = 10, control_type: str = 'Control'):
        """
        点击指定控件。

        :param control_name: 控件名称
        :param searchDepth:  搜索深度, 默认为10
        :param control_type: 控件类型，默认为 'Control'
        :return: auto对象
        """
        click_control = getattr(self.ziniao_window, control_type)(searchDepth=searchDepth, Name=control_name)
        if click_control.Exists(1, 0):
            click_control.Click(waitTime=0.1)
        else:
            raise Exception(f"控件 '{control_name}' 未找到")
        return click_control

    def __input_control(self, text_value: str, control_name: str, searchDepth: int = 20, control_type: str = 'EditControl'):
        """
        点击指定控件。

        :param text_value:   输入内容
        :param control_name: 控件名称
        :param searchDepth:  搜索深度, 默认为10
        :param control_type: 控件类型，默认为 'EditControl'
        :return: auto对象
        """
        input_control = self.__click_control(control_name, searchDepth, control_type)
        if input_control:
            input_control.GetValuePattern().SetValue('')
        input_control.SendKeys(text_value, waitTime=0.01)

        return input_control


    def open_store_gui(self, store_name, locate_type='相等'):
        """
        打开店铺
        """
        page_box = self.__click_control("页码", 10, "GroupControl")
        tar_page = self.__click_control("100 条/页", 15)
        sleep(2)
        store_input = self.__input_control(store_name, '请输入关键词 批量搜索用，隔开')
        sleep(2)
        search_box = self.__click_control("search")
        sleep(3)

        error_control = self.ziniao_window.Control(Name='暂无数据')
        if error_control.Exists(1, 0):
            raise ValueError (f"没有包含{store_name}这个店铺")

        "精确模式则全字匹配，模糊模式则包含匹配"
        current_store_name = ''   "方便后续找到对应的网页对象"
        group_control_items = self.ziniao_window.Control(Name='启 动').GetParentControl().GetParentControl()
        for index, child_control_item in enumerate(group_control_items.GetChildren()):
            current_store_name = child_control_item.GetChildren()[1].Name
            if locate_type == "相等":
                current_store_name = store_name
                if store_name == current_store_name:
                    child_control_item.ButtonControl(Name='启 动').Click()
                    break
            else:
                current_store_name = child_control_item.GetChildren()[1].Name
                if store_name in current_store_name:
                    launch_control = self.ziniao_window.Control(searchDepth=20, Name=current_store_name).GetParentControl()
                    launch_control.ButtonControl(Name='启 动').Click()
                    break

        web_window = ''
        for retry in range(10):
            sleep(5)
            desktop = auto.GetRootControl()
            # 遍历桌面的所有子控件（窗口）
            for window in desktop.GetChildren():
                if current_store_name[:4] in window.Name:
                    web_window = window
                    web_window.Maximize()
                    break
            if web_window != '':
                sleep(2)
                break
            if retry == 4:
                raise ValueError ("启动时间过长")
        web_window.ButtonControl(Name='打开账号').Click()
        sleep(2)
        web_page = xbot.web.get_active(mode="ziniaobrowser", load_timeout=0)
        return web_page
        



def main(args):
    zn = ZiNiao()
    zn.open_store_gui("二部", '1')

