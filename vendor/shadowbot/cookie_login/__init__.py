from .import package
import xbot_visual

def process1(网页对象,保存路径,partition_key):
    """
    保存Cookie
    保存当前网页的 Cookie 和 local_storage，用于下次登录
    * @param 网页对象，
    * @param 保存路径，
    * @param partition_key，
    """
    outputs = []
    inputs = {"网页对象":网页对象,"保存路径":保存路径,"partition_key":partition_key}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.cookie_login.process1", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.cookie_login.process1",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.cookie_login.process1", extension_module, activity_func)

def process2(网页对象,Cookie文件路径,添加本地存储):
    """
    Cookie登录
    使用保存的Cookie实现登录操作
    * @param 网页对象，
    * @param Cookie文件路径，
    * @param 添加本地存储，
    """
    outputs = []
    inputs = {"网页对象":网页对象,"Cookie文件路径":Cookie文件路径,"添加本地存储":添加本地存储}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.cookie_login.process2", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.cookie_login.process2",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.cookie_login.process2", extension_module, activity_func)

def process3(网页对象,删除本地存储):
    """
    Cookie退出登录
    通过删除Cookie实现退出登录操作
    * @param 网页对象，
    * @param 删除本地存储，
    """
    outputs = []
    inputs = {"网页对象":网页对象,"删除本地存储":删除本地存储}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.cookie_login.process3", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.cookie_login.process3",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.cookie_login.process3", extension_module, activity_func)

