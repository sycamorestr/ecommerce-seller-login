from .import package
import xbot_visual
from . import Start
from . import PopupBlocker
from . import ClickByXpath
from . import InputByXpath
from . import DataSelection
from . import GetElementInnerText
from . import GetDownloadPath
from . import IsElementExists
from . import GetShopName
from . import HoverByXpath

def process1():
    """
    打开下载文件询问窗口
    临时指令，保证流程运行完毕后还原浏览器设置
    """
    outputs = []
    inputs = {}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_fe2a1069.process1", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.process1",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_fe2a1069.process1", extension_module, activity_func)

def process2(web_page,url,跳转最大次数):
    """
    URL检查
    检查页面url是否正确，不正确自动跳转
    * @param web_page，
    * @param url，
    * @param 跳转最大次数，
    """
    outputs = []
    inputs = {"web_page":web_page,"url":url,"跳转最大次数":跳转最大次数}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_fe2a1069.process2", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.process2",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_fe2a1069.process2", extension_module, activity_func)

