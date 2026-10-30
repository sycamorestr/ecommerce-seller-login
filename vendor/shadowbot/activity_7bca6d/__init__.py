from .import package
import xbot_visual
from . import qn_login
from . import taobao_mini
from . import login_1688
from . import login_tmall_supermarket

def process1(username,password,tj_username,tj_password,web_type,status):
    """
    巨量登录
    该指令实现自动登录巨量引擎后台
    * @param username，
    * @param password，
    * @param tj_username，
    * @param tj_password，
    * @param web_type，
    * @param status，是否退出已登录
    * @return web_page，
    """
    outputs = ["web_page"]
    inputs = {"username":username,"password":password,"tj_username":tj_username,"tj_password":tj_password,"web_type":web_type,"status":status}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_7bca6d.process1", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_7bca6d.process1",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_7bca6d.process1", extension_module, activity_func)

def process4(username,password,验证邮箱,邮箱授权码,获取授权码间隔时长,验证码失败最大重试次数,退出已登录账户,retry_cnt,网页对象):
    """
    抖店登录
    该指令实现自动登录抖店后台（若报错，请考虑切换至“抖店操作 - 抖店多店铺登录”）
    * @param username，登录邮箱
    * @param password，登录密码
    * @param 验证邮箱，
    * @param 邮箱授权码，
    * @param 获取授权码间隔时长，
    * @param 验证码失败最大重试次数，
    * @param 退出已登录账户，
    * @param retry_cnt，登录流程失败重试次数
    * @param 网页对象，不填则默认打开一个新的网页对象
    * @return web_page，网页对象
    """
    outputs = ["web_page"]
    inputs = {"username":username,"password":password,"验证邮箱":验证邮箱,"邮箱授权码":邮箱授权码,"获取授权码间隔时长":获取授权码间隔时长,"验证码失败最大重试次数":验证码失败最大重试次数,"退出已登录账户":退出已登录账户,"retry_cnt":retry_cnt,"网页对象":网页对象}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_7bca6d.process4", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_7bca6d.process4",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_7bca6d.process4", extension_module, activity_func)

def process5(username,password,tj_username,tj_password,web_type):
    """
    有赞登录
    该指令实现自动登录有赞后台
    * @param username，
    * @param password，
    * @param tj_username，
    * @param tj_password，
    * @param web_type，
    * @return web_page，
    """
    outputs = ["web_page"]
    inputs = {"username":username,"password":password,"tj_username":tj_username,"tj_password":tj_password,"web_type":web_type}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_7bca6d.process5", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_7bca6d.process5",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_7bca6d.process5", extension_module, activity_func)

def process6(username,password,web_mode,tj_username,tj_password,rec_count,login_url):
    """
    京东登录
    该指令实现自动登录京东（在滑动验证码的时候可能会产生额外的费用)
    * @param username，
    * @param password，
    * @param web_mode，
    * @param tj_username，
    * @param tj_password，
    * @param rec_count，
    * @param login_url，自定义登录网址
    * @return web_page，
    """
    outputs = ["web_page"]
    inputs = {"username":username,"password":password,"web_mode":web_mode,"tj_username":tj_username,"tj_password":tj_password,"rec_count":rec_count,"login_url":login_url}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_7bca6d.process6", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_7bca6d.process6",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_7bca6d.process6", extension_module, activity_func)

def process7(userid,password,mode,path_to_chrome_exe,加载超时时间,ym_token,是否退出已登录,重试次数):
    """
    淘宝登录
    该指令实现自动登录淘宝后台
    * @param userid，
    * @param password，
    * @param mode，
    * @param path_to_chrome_exe，
    * @param 加载超时时间，加载登录页面的超时时间
    * @param ym_token，
    * @param 是否退出已登录，
    * @param 重试次数，
    * @return web_page，
    """
    outputs = ["web_page"]
    inputs = {"userid":userid,"password":password,"mode":mode,"path_to_chrome_exe":path_to_chrome_exe,"加载超时时间":加载超时时间,"ym_token":ym_token,"是否退出已登录":是否退出已登录,"重试次数":重试次数}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_7bca6d.process7", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_7bca6d.process7",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_7bca6d.process7", extension_module, activity_func)

def process11(web_page,drag_start_element,background_element):
    """
    滑块拖动
    该指令实现模拟人工拖动滑块
    * @param web_page，
    * @param drag_start_element，
    * @param background_element，
    """
    outputs = []
    inputs = {"web_page":web_page,"drag_start_element":drag_start_element,"background_element":background_element}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_7bca6d.process11", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_7bca6d.process11",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_7bca6d.process11", extension_module, activity_func)

def process12(username,password,tj_username,tj_password,web_type):
    """
    巨量纵横登录
    该指令实现自动登录巨量纵横后台
    * @param username，
    * @param password，
    * @param tj_username，
    * @param tj_password，
    * @param web_type，
    * @return web_page，
    """
    outputs = ["web_page"]
    inputs = {"username":username,"password":password,"tj_username":tj_username,"tj_password":tj_password,"web_type":web_type}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_7bca6d.process12", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_7bca6d.process12",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_7bca6d.process12", extension_module, activity_func)

def process15(网页对象,username,password,tj_username,tj_password,登录的店铺名称,是否要退出已登录账号,wait_time):
    """
    电商罗盘登录
    该指令实现自动登录电商罗盘后台
    * @param 网页对象，
    * @param username，
    * @param password，
    * @param tj_username，
    * @param tj_password，
    * @param 登录的店铺名称，选择要登录的店铺名称(可为空，若空值则不做处理)
    * @param 是否要退出已登录账号，勾选会进行自动退出当前已经的登录的账号操作
    * @param wait_time，等待时间
    * @return web_page，
    """
    outputs = ["web_page"]
    inputs = {"网页对象":网页对象,"username":username,"password":password,"tj_username":tj_username,"tj_password":tj_password,"登录的店铺名称":登录的店铺名称,"是否要退出已登录账号":是否要退出已登录账号,"wait_time":wait_time}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_7bca6d.process15", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_7bca6d.process15",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_7bca6d.process15", extension_module, activity_func)

def process20(浏览器类型,登录账号,登录密码,重试次数):
    """
    支付宝登录
    该指令实现自动登录支付宝后台(注:识别验证码会产生额外费用)
    * @param 浏览器类型，
    * @param 登录账号，
    * @param 登录密码，
    * @param 重试次数，重试次数为点选验证码的重试次数, 必须大于等于1
    * @return web_page，
    """
    outputs = ["web_page"]
    inputs = {"浏览器类型":浏览器类型,"登录账号":登录账号,"登录密码":登录密码,"重试次数":重试次数}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_7bca6d.process20", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_7bca6d.process20",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_7bca6d.process20", extension_module, activity_func)

def process21(浏览器类型,账号,密码,识别引擎,验证码重试次数,是否创建新页面):
    """
    拼多多登录
    该指令实现自动登录拼多多后台（注:登录验证码识别会产生额外费用）
    * @param 浏览器类型，
    * @param 账号，请输入拼多多账号
    * @param 密码，请输入拼多多密码
    * @param 识别引擎，
    * @param 验证码重试次数，验证码重试次数
    * @param 是否创建新页面，是否创建新页面
    * @return 网页对象，
    """
    outputs = ["网页对象"]
    inputs = {"浏览器类型":浏览器类型,"账号":账号,"密码":密码,"识别引擎":识别引擎,"验证码重试次数":验证码重试次数,"是否创建新页面":是否创建新页面}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_7bca6d.process21", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_7bca6d.process21",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_7bca6d.process21", extension_module, activity_func)

def process33(验证重试次数,账号,密码,浏览器类型):
    """
    爱库存登录
    在新打开的网页窗口中登录爱库存
    * @param 验证重试次数，
    * @param 账号，
    * @param 密码，
    * @param 浏览器类型，
    * @return web_page，
    """
    outputs = ["web_page"]
    inputs = {"验证重试次数":验证重试次数,"账号":账号,"密码":密码,"浏览器类型":浏览器类型}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_7bca6d.process33", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_7bca6d.process33",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_7bca6d.process33", extension_module, activity_func)

def process39(用户名,密码):
    """
    登录旺店通
    该指令实现自动登录旺店通
    * @param 用户名，
    * @param 密码，
    * @return process_result，
    """
    outputs = ["process_result"]
    inputs = {"用户名":用户名,"密码":密码}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_7bca6d.process39", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_7bca6d.process39",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_7bca6d.process39", extension_module, activity_func)

def process40(登录用户名,登录密码,子平台,退出已登录账户,短信验证码获取接口,识别引擎,网页对象):
    """
    京东登录-京准通
    支持【京速推, 商智-品牌版, 商智-商家版, 京东快车, 京东联盟, 购物触点, 京东展位, 京东数坊, 京东直投, 京东海投】登录成功后跳转到对应主页即可(该指令识别验证码登录会产生额外费用)
    * @param 登录用户名，
    * @param 登录密码，
    * @param 子平台，
    * @param 退出已登录账户，
    * @param 短信验证码获取接口，
    * @param 识别引擎，
    * @param 网页对象，
    * @return 输出网页对象，
    """
    outputs = ["输出网页对象"]
    inputs = {"登录用户名":登录用户名,"登录密码":登录密码,"子平台":子平台,"退出已登录账户":退出已登录账户,"短信验证码获取接口":短信验证码获取接口,"识别引擎":识别引擎,"网页对象":网页对象}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_7bca6d.process40", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_7bca6d.process40",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_7bca6d.process40", extension_module, activity_func)

def process42(账户,密码,短信验证码接口,退出已登录账户,浏览器类型):
    """
    阿里妈妈数智登录
    
    * @param 账户，
    * @param 密码，
    * @param 短信验证码接口，
    * @param 退出已登录账户，
    * @param 浏览器类型，
    * @return web_page，
    """
    outputs = ["web_page"]
    inputs = {"账户":账户,"密码":密码,"短信验证码接口":短信验证码接口,"退出已登录账户":退出已登录账户,"浏览器类型":浏览器类型}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_7bca6d.process42", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_7bca6d.process42",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_7bca6d.process42", extension_module, activity_func)

def process47(登录邮箱,登录密码,验证邮箱,邮箱授权码,获取授权码间隔时长,验证码失败最大重试次数,退出已登录账户,retry_cnt):
    """
    巨量引擎邮箱登录
    使用邮箱账号登录到巨量引擎
    * @param 登录邮箱，登录邮箱
    * @param 登录密码，登录密码
    * @param 验证邮箱，
    * @param 邮箱授权码，
    * @param 获取授权码间隔时长，
    * @param 验证码失败最大重试次数，
    * @param 退出已登录账户，
    * @param retry_cnt，登录流程失败自动重试次数
    * @return web_page，网页对象
    """
    outputs = ["web_page"]
    inputs = {"登录邮箱":登录邮箱,"登录密码":登录密码,"验证邮箱":验证邮箱,"邮箱授权码":邮箱授权码,"获取授权码间隔时长":获取授权码间隔时长,"验证码失败最大重试次数":验证码失败最大重试次数,"退出已登录账户":退出已登录账户,"retry_cnt":retry_cnt}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_7bca6d.process47", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_7bca6d.process47",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_7bca6d.process47", extension_module, activity_func)

def process56(京麦账号,京麦密码,图鉴账号,图鉴密码,重试次数,识别引擎,浏览器类型):
    """
    京麦登录
    京麦登录指令，该指令实现滑动验证码时会产生费用
    * @param 京麦账号，
    * @param 京麦密码，
    * @param 图鉴账号，
    * @param 图鉴密码，
    * @param 重试次数，
    * @param 识别引擎，
    * @param 浏览器类型，
    * @return 保存网页对象，
    """
    outputs = ["保存网页对象"]
    inputs = {"京麦账号":京麦账号,"京麦密码":京麦密码,"图鉴账号":图鉴账号,"图鉴密码":图鉴密码,"重试次数":重试次数,"识别引擎":识别引擎,"浏览器类型":浏览器类型}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_7bca6d.process56", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_7bca6d.process56",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_7bca6d.process56", extension_module, activity_func)

def process59(是否要退出已登陆账号,网页对象,账号,密码,登录的店铺名称):
    """
    电商罗盘策略登陆
    该指令实现自动登录电商罗盘策略后台
    * @param 是否要退出已登陆账号，
    * @param 网页对象，
    * @param 账号，
    * @param 密码，
    * @param 登录的店铺名称，
    """
    outputs = []
    inputs = {"是否要退出已登陆账号":是否要退出已登陆账号,"网页对象":网页对象,"账号":账号,"密码":密码,"登录的店铺名称":登录的店铺名称}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_7bca6d.process59", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_7bca6d.process59",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_7bca6d.process59", extension_module, activity_func)

def process65(网页对象,滑块元素,滑动条背景图元素):
    """
    美团开店宝滑块
    该指令用于通过美团开店宝登录界面的滑块
    * @param 网页对象，
    * @param 滑块元素，
    * @param 滑动条背景图元素，
    """
    outputs = []
    inputs = {"网页对象":网页对象,"滑块元素":滑块元素,"滑动条背景图元素":滑动条背景图元素}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_7bca6d.process65", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_7bca6d.process65",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_7bca6d.process65", extension_module, activity_func)

