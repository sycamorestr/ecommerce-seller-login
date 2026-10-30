from .import package
import xbot_visual
from . import DSR_requests
from . import cuopon_date_select

def process1(账号,密码,店铺名称,图鉴账号,图鉴密码,是否退出已登录,加载超时时间,浏览器对象,验证重试次数):
    """
    抖店多店铺登录
    用于抖店登录操作（注意：该指令会产生"影刀验证码-云码"识别费用，调用"通用单图滑块类型1"）
    * @param 账号，请输入抖店邮箱登录账号
    * @param 密码，请输入抖店邮箱登录密码
    * @param 店铺名称，请输入目标店铺名称全称；同时支持输入数字来选择第几个店铺进入。（单店铺账号无需进行店铺选择，请勿填写此项）
    * @param 图鉴账号，请输入您的图鉴账号
    * @param 图鉴密码，请输入您的图鉴密码
    * @param 是否退出已登录，勾选表示退出已登录店铺，不勾选反之
    * @param 加载超时时间，包含网页加载超时时间、等待元素超时时间等，请根据网速情况自行调整
    * @param 浏览器对象，输入的浏览器对象
    * @param 验证重试次数，验证码的重试次数
    * @return web_page，保存登录后的抖店网页对象至
    """
    outputs = ["web_page"]
    inputs = {"账号":账号,"密码":密码,"店铺名称":店铺名称,"图鉴账号":图鉴账号,"图鉴密码":图鉴密码,"是否退出已登录":是否退出已登录,"加载超时时间":加载超时时间,"浏览器对象":浏览器对象,"验证重试次数":验证重试次数}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_966451c9.process1", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_966451c9.process1",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_966451c9.process1", extension_module, activity_func)

def process3(网页对象,筛选类别,时间类别,开始日期,结束日期):
    """
    抖店售后工作台时间选择
    抖店售后工作台的时间选择
    * @param 网页对象，
    * @param 筛选类别，
    * @param 时间类别，
    * @param 开始日期，
    * @param 结束日期，
    """
    outputs = []
    inputs = {"网页对象":网页对象,"筛选类别":筛选类别,"时间类别":时间类别,"开始日期":开始日期,"结束日期":结束日期}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_966451c9.process3", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_966451c9.process3",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_966451c9.process3", extension_module, activity_func)

def process4(网页对象,筛选类别,时间类别,开始日期,结束日期):
    """
    抖店订单管理时间选择
    抖店订单管理处的时间选择
    * @param 网页对象，
    * @param 筛选类别，
    * @param 时间类别，
    * @param 开始日期，
    * @param 结束日期，
    """
    outputs = []
    inputs = {"网页对象":网页对象,"筛选类别":筛选类别,"时间类别":时间类别,"开始日期":开始日期,"结束日期":结束日期}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_966451c9.process4", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_966451c9.process4",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_966451c9.process4", extension_module, activity_func)

def process5(web_page,隐藏显示):
    """
    抖店商家助手隐藏显示
    抖店页面旁边小图标隐藏和显示
    * @param web_page，
    * @param 隐藏显示，
    """
    outputs = []
    inputs = {"web_page":web_page,"隐藏显示":隐藏显示}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_966451c9.process5", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_966451c9.process5",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_966451c9.process5", extension_module, activity_func)

def process13(店铺名称,网页对象,全局超时时间):
    """
    抖店店铺切换
    抖店登录状态下，切换店铺
    * @param 店铺名称，请输入目标店铺名称全称；同时支持输入数字来选择第几个店铺进入。（单店铺账号无需进行店铺选择，请勿填写此项）
    * @param 网页对象，请传入需要切换店铺的网页对象
    * @param 全局超时时间，包含网页加载超时时间、等待元素超时时间等，请根据网速情况自行调整
    """
    outputs = []
    inputs = {"店铺名称":店铺名称,"网页对象":网页对象,"全局超时时间":全局超时时间}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_966451c9.process13", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_966451c9.process13",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_966451c9.process13", extension_module, activity_func)

def process22(网页对象,全局超时时间):
    """
    飞鸽工作台去除开屏广告
    用于去除跳转飞鸽工作台后弹出的开屏广告
    * @param 网页对象，请传入需要去除广告的网页对象
    * @param 全局超时时间，包含网页加载超时时间、等待元素超时时间等，请根据网速情况自行调整
    """
    outputs = []
    inputs = {"网页对象":网页对象,"全局超时时间":全局超时时间}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_966451c9.process22", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_966451c9.process22",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_966451c9.process22", extension_module, activity_func)

def process25(开始时间,开始日期触发器,结束时间,web_page):
    """
    抖店时分秒日期选择
    抖店平台带时分秒处的时间选择
    * @param 开始时间，
    * @param 开始日期触发器，
    * @param 结束时间，
    * @param web_page，
    """
    outputs = []
    inputs = {"开始时间":开始时间,"开始日期触发器":开始日期触发器,"结束时间":结束时间,"web_page":web_page}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_966451c9.process25", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_966451c9.process25",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_966451c9.process25", extension_module, activity_func)

def process30(开始时间,结束时间,开始日期触发器,结束日期触发器):
    """
    抖店评价管理时间选择
    对抖店-订单-评价管理的时间进行选择
    * @param 开始时间，格式为YYYY-MM-DD_HH-MM-SS
    * @param 结束时间，格式为YYYY-MM-DD_HH-MM-SS
    * @param 开始日期触发器，
    * @param 结束日期触发器，
    """
    outputs = []
    inputs = {"开始时间":开始时间,"结束时间":结束时间,"开始日期触发器":开始日期触发器,"结束日期触发器":结束日期触发器}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_966451c9.process30", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_966451c9.process30",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_966451c9.process30", extension_module, activity_func)

def process35(网页对象,店铺ID,全局超时时间):
    """
    抖店店铺切换(ID)
    该指令实现了基于ID进行抖店店铺切换
    * @param 网页对象，网页对象
    * @param 店铺ID，店铺ID
    * @param 全局超时时间，全局超时时间
    """
    outputs = []
    inputs = {"网页对象":网页对象,"店铺ID":店铺ID,"全局超时时间":全局超时时间}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_966451c9.process35", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_966451c9.process35",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_966451c9.process35", extension_module, activity_func)

