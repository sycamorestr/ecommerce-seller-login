from .import package
import xbot_visual

def to_account_page():
    """
    进入账号管理页面
    从紫鸟浏览器控制台进入账号管理页面
    """
    outputs = []
    inputs = {}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.super_browser.to_account_page", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.super_browser.to_account_page",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.super_browser.to_account_page", extension_module, activity_func)

def open_store(店铺名称,匹配类型,打开账号,超时时间,隐私模式,处理在线人员上限):
    """
    打开店铺
    该指令实现了根据店铺名称打开店铺的功能，调用这个指令会关闭正在打开的所有店铺
    * @param 店铺名称，
    * @param 匹配类型，
    * @param 打开账号，
    * @param 超时时间，
    * @param 隐私模式，
    * @param 处理在线人员上限，处理紫鸟在线人员弹窗
    * @return web_page，
    * @return 完整店铺名称，
    """
    outputs = ["web_page","完整店铺名称"]
    inputs = {"店铺名称":店铺名称,"匹配类型":匹配类型,"打开账号":打开账号,"超时时间":超时时间,"隐私模式":隐私模式,"处理在线人员上限":处理在线人员上限}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.super_browser.open_store", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.super_browser.open_store",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.super_browser.open_store", extension_module, activity_func)

def get_download_path():
    """
    获取下载文件保存位置
    获取紫鸟浏览器默认下载文件保存位置
    * @return download_path，
    * @return is_check，
    """
    outputs = ["download_path","is_check"]
    inputs = {}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.super_browser.get_download_path", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.super_browser.get_download_path",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.super_browser.get_download_path", extension_module, activity_func)

def process1(企业名称,企业用户名,密码,是否填写账号密码,是否退出登录,紫鸟版本):
    """
    紫鸟登录
    该指令实现了自动打开紫鸟控制台，并登录企业号的操作
    * @param 企业名称，
    * @param 企业用户名，
    * @param 密码，
    * @param 是否填写账号密码，
    * @param 是否退出登录，
    * @param 紫鸟版本，
    """
    outputs = []
    inputs = {"企业名称":企业名称,"企业用户名":企业用户名,"密码":密码,"是否填写账号密码":是否填写账号密码,"是否退出登录":是否退出登录,"紫鸟版本":紫鸟版本}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.super_browser.process1", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.super_browser.process1",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.super_browser.process1", extension_module, activity_func)

def process2(网页对象,保存文件夹,保存文件名,超时时间,下载按钮,等待对话框出现):
    """
    紫鸟文件下载
    该指令实现了紫鸟浏览器网页端的文件下载操作
    * @param 网页对象，
    * @param 保存文件夹，
    * @param 保存文件名，
    * @param 超时时间，
    * @param 下载按钮，
    * @param 等待对话框出现，
    * @return download_file_name，
    """
    outputs = ["download_file_name"]
    inputs = {"网页对象":网页对象,"保存文件夹":保存文件夹,"保存文件名":保存文件名,"超时时间":超时时间,"下载按钮":下载按钮,"等待对话框出现":等待对话框出现}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.super_browser.process2", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.super_browser.process2",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.super_browser.process2", extension_module, activity_func)

def process6(所属平台):
    """
    获取店铺列表
    该指令实现了在紫鸟浏览器上获取指定平台的所有店铺名称操作
    * @param 所属平台，
    * @return store_name_list，
    """
    outputs = ["store_name_list"]
    inputs = {"所属平台":所属平台}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.super_browser.process6", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.super_browser.process6",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.super_browser.process6", extension_module, activity_func)

def process7(网页对象,上传按钮,上传文件路径,等待对话框超时时间):
    """
    上传文件到紫鸟
    该指令实现了从本地上传文件到紫鸟网页端的操作
    * @param 网页对象，
    * @param 上传按钮，
    * @param 上传文件路径，
    * @param 等待对话框超时时间，
    """
    outputs = []
    inputs = {"网页对象":网页对象,"上传按钮":上传按钮,"上传文件路径":上传文件路径,"等待对话框超时时间":等待对话框超时时间}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.super_browser.process7", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.super_browser.process7",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.super_browser.process7", extension_module, activity_func)

def process9(店铺名称,匹配类型,打开账号,超时时间,隐私模式):
    """
    打开店铺(UIA)
    该指令通过uia实现了根据店铺名称打开店铺的功能，调用这个指令会关闭正在打开的所有店铺
    * @param 店铺名称，
    * @param 匹配类型，
    * @param 打开账号，
    * @param 超时时间，
    * @param 隐私模式，
    * @return web_page，
    * @return 完整店铺名称，
    """
    outputs = ["web_page","完整店铺名称"]
    inputs = {"店铺名称":店铺名称,"匹配类型":匹配类型,"打开账号":打开账号,"超时时间":超时时间,"隐私模式":隐私模式}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.super_browser.process9", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.super_browser.process9",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.super_browser.process9", extension_module, activity_func)

