from .import package
import xbot_visual

def process1(邮箱账号,邮箱密码,图鉴账号,图鉴密码,是否退出已登录):
    """
    巨量引擎登录
    巨量纵横登录
    * @param 邮箱账号，
    * @param 邮箱密码，
    * @param 图鉴账号，
    * @param 图鉴密码，
    * @param 是否退出已登录，
    """
    outputs = []
    inputs = {"邮箱账号":邮箱账号,"邮箱密码":邮箱密码,"图鉴账号":图鉴账号,"图鉴密码":图鉴密码,"是否退出已登录":是否退出已登录}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_52aea4a0.process1", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_52aea4a0.process1",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_52aea4a0.process1", extension_module, activity_func)

