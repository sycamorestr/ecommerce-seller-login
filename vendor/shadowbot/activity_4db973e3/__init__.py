from .import package
import xbot_visual
from . import emphasize_color

def process15(验证码图片,滑块元素,网页对象,滑动条,图鉴账号,图鉴密码,偏移,是否模拟人工):
    """
    图片旋转验证
    基于验证码识别指令实现图片旋转验证
    * @param 验证码图片，
    * @param 滑块元素，
    * @param 网页对象，
    * @param 滑动条，
    * @param 图鉴账号，
    * @param 图鉴密码，
    * @param 偏移，
    * @param 是否模拟人工，
    """
    outputs = []
    inputs = {"验证码图片":验证码图片,"滑块元素":滑块元素,"网页对象":网页对象,"滑动条":滑动条,"图鉴账号":图鉴账号,"图鉴密码":图鉴密码,"偏移":偏移,"是否模拟人工":是否模拟人工}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_4db973e3.process15", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_4db973e3.process15",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_4db973e3.process15", extension_module, activity_func)

def process16(网页对象,验证码图片,图鉴账号,图鉴密码):
    """
    推理拼图验证
    基于验证码识别指令实现推理图片验证
    * @param 网页对象，
    * @param 验证码图片，
    * @param 图鉴账号，
    * @param 图鉴密码，
    """
    outputs = []
    inputs = {"网页对象":网页对象,"验证码图片":验证码图片,"图鉴账号":图鉴账号,"图鉴密码":图鉴密码}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_4db973e3.process16", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_4db973e3.process16",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_4db973e3.process16", extension_module, activity_func)

def get_scaling():
    """
    获取当前屏幕缩放比例
    获取当前显示器屏幕的缩放比例
    * @return scaling，
    """
    outputs = ["scaling"]
    inputs = {}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_4db973e3.get_scaling", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_4db973e3.get_scaling",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_4db973e3.get_scaling", extension_module, activity_func)

def process19(图块所在背景,目标图块,拖拽元素,网页对象,缺口or单缺口,图鉴帐号,图鉴密码,重试次数,偏移距离,识别引擎,移动速度):
    """
    滑动拼图验证
    基于验证码识别指令实现滑块拼图验证
    * @param 图块所在背景，
    * @param 目标图块，
    * @param 拖拽元素，
    * @param 网页对象，
    * @param 缺口or单缺口，
    * @param 图鉴帐号，
    * @param 图鉴密码，
    * @param 重试次数，滑动失败时的重试次数，最小为0，默认为5
    * @param 偏移距离，调整滑块的拖拽距离
    * @param 识别引擎，
    * @param 移动速度，移动滑块的速度
    """
    outputs = []
    inputs = {"图块所在背景":图块所在背景,"目标图块":目标图块,"拖拽元素":拖拽元素,"网页对象":网页对象,"缺口or单缺口":缺口or单缺口,"图鉴帐号":图鉴帐号,"图鉴密码":图鉴密码,"重试次数":重试次数,"偏移距离":偏移距离,"识别引擎":识别引擎,"移动速度":移动速度}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_4db973e3.process19", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_4db973e3.process19",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_4db973e3.process19", extension_module, activity_func)

def process20(网页对象,验证码元素,账号,密码,验证码类型,软件ID):
    """
    验证码识别(超级鹰)
    该指令使用超级鹰引擎进行验证码识别
    * @param 网页对象，待处理的网页对象
    * @param 验证码元素，待识别的元素对象
    * @param 账号，超级鹰平台的登录账号
    * @param 密码，超级鹰平台的登录密码
    * @param 验证码类型，验证码类型
    * @param 软件ID，软件ID
    * @return 识别结果，验证码识别结果
    """
    outputs = ["识别结果"]
    inputs = {"网页对象":网页对象,"验证码元素":验证码元素,"账号":账号,"密码":密码,"验证码类型":验证码类型,"软件ID":软件ID}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_4db973e3.process20", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_4db973e3.process20",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_4db973e3.process20", extension_module, activity_func)

def process21(网页对象,验证码图片,点选提示,识别模式,图鉴账号,图鉴密码):
    """
    坐标点选验证
    基于验证码识别指令实现坐标点选验证
    * @param 网页对象，
    * @param 验证码图片，
    * @param 点选提示，
    * @param 识别模式，
    * @param 图鉴账号，
    * @param 图鉴密码，
    """
    outputs = []
    inputs = {"网页对象":网页对象,"验证码图片":验证码图片,"点选提示":点选提示,"识别模式":识别模式,"图鉴账号":图鉴账号,"图鉴密码":图鉴密码}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_4db973e3.process21", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_4db973e3.process21",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_4db973e3.process21", extension_module, activity_func)

def process24(账号,密码,验证码类型,本地图片路径,软件ID):
    """
    本地验证码识别(超级鹰)
    该指令使用超级鹰引擎进行本地验证码识别
    * @param 账号，超级鹰平台的登录账号
    * @param 密码，超级鹰平台的登录密码
    * @param 验证码类型，验证码类型
    * @param 本地图片路径，
    * @param 软件ID，软件ID
    * @return 识别结果，验证码识别结果
    """
    outputs = ["识别结果"]
    inputs = {"账号":账号,"密码":密码,"验证码类型":验证码类型,"本地图片路径":本地图片路径,"软件ID":软件ID}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_4db973e3.process24", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_4db973e3.process24",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_4db973e3.process24", extension_module, activity_func)

def process35(图块所在背景,目标图块,拖拽元素,网页对象,缺口or单缺口,图鉴帐号,图鉴密码,重试次数,偏移距离,识别引擎,移动速度):
    """
    京东风控滑块验证
    该指令用户京东风控验证码的识别
    * @param 图块所在背景，
    * @param 目标图块，
    * @param 拖拽元素，
    * @param 网页对象，
    * @param 缺口or单缺口，
    * @param 图鉴帐号，
    * @param 图鉴密码，
    * @param 重试次数，滑动失败时的重试次数，最小为0，默认为5
    * @param 偏移距离，调整滑块的拖拽距离
    * @param 识别引擎，
    * @param 移动速度，移动滑块的速度
    """
    outputs = []
    inputs = {"图块所在背景":图块所在背景,"目标图块":目标图块,"拖拽元素":拖拽元素,"网页对象":网页对象,"缺口or单缺口":缺口or单缺口,"图鉴帐号":图鉴帐号,"图鉴密码":图鉴密码,"重试次数":重试次数,"偏移距离":偏移距离,"识别引擎":识别引擎,"移动速度":移动速度}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_4db973e3.process35", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_4db973e3.process35",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_4db973e3.process35", extension_module, activity_func)

