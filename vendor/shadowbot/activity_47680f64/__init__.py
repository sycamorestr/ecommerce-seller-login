from .import package
import xbot_visual
from . import DownAndMoveFile
from . import CreateDir
from . import MoveToPardir
from . import DateStringCheck
from . import latest_email
from . import get_SMS_code

def process1(压缩文件路径,删除原文件):
    """
    解压文件到当前目录
    
    * @param 压缩文件路径，
    * @param 删除原文件，
    * @return 文件路径列表，
    """
    outputs = ["文件路径列表"]
    inputs = {"压缩文件路径":压缩文件路径,"删除原文件":删除原文件}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_47680f64.process1", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_47680f64.process1",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_47680f64.process1", extension_module, activity_func)

def process2(是否弹窗下载,保存文件夹,文件名,下载前文件数量,浏览器下载保存路径,最大等待时长):
    """
    下载一个文件
    兼容弹窗下载和无弹窗下载，弹窗下载不修改文件名
    * @param 是否弹窗下载，
    * @param 保存文件夹，
    * @param 文件名，
    * @param 下载前文件数量，
    * @param 浏览器下载保存路径，
    * @param 最大等待时长，
    * @return 文件路径，
    """
    outputs = ["文件路径"]
    inputs = {"是否弹窗下载":是否弹窗下载,"保存文件夹":保存文件夹,"文件名":文件名,"下载前文件数量":下载前文件数量,"浏览器下载保存路径":浏览器下载保存路径,"最大等待时长":最大等待时长}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_47680f64.process2", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_47680f64.process2",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_47680f64.process2", extension_module, activity_func)

def process3(日期范围或快捷日期,quick_select_map):
    """
    快捷日期检验和转换
    检验快捷日期是否合规并转换为指定形式
    * @param 日期范围或快捷日期，
    * @param quick_select_map，
    * @return 勾选日期，返回quick_select_map匹配结果 或 日期区间字符串 
    """
    outputs = ["勾选日期"]
    inputs = {"日期范围或快捷日期":日期范围或快捷日期,"quick_select_map":quick_select_map}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_47680f64.process3", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_47680f64.process3",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_47680f64.process3", extension_module, activity_func)

def process5(传入值,可选项列表,是否多选,分隔符):
    """
    入参校验
    检验传入参数是否合规
    * @param 传入值，
    * @param 可选项列表，
    * @param 是否多选，
    * @param 分隔符，
    """
    outputs = []
    inputs = {"传入值":传入值,"可选项列表":可选项列表,"是否多选":是否多选,"分隔符":分隔符}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_47680f64.process5", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_47680f64.process5",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_47680f64.process5", extension_module, activity_func)

