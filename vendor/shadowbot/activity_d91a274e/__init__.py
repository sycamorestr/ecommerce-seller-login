from .import package
import xbot_visual

def process1(报表类型,转化周期,日期,web_page):
    """
    直通车-报表-汇总数据获取
    阿里妈妈直通车-报表-汇总数据获取
    * @param 报表类型，
    * @param 转化周期，
    * @param 日期，
    * @param web_page，
    * @return data，
    """
    outputs = ["data"]
    inputs = {"报表类型":报表类型,"转化周期":转化周期,"日期":日期,"web_page":web_page}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_d91a274e.process1", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_d91a274e.process1",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_d91a274e.process1", extension_module, activity_func)

def process6(平台名称,账户,密码,浏览器类型):
    """
    阿里妈妈_平台登录
    
    * @param 平台名称，
    * @param 账户，
    * @param 密码，
    * @param 浏览器类型，
    * @return web_page，
    """
    outputs = ["web_page"]
    inputs = {"平台名称":平台名称,"账户":账户,"密码":密码,"浏览器类型":浏览器类型}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_d91a274e.process6", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_d91a274e.process6",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_d91a274e.process6", extension_module, activity_func)

def process7(日期,文件保存路径,效果,周期,web_page):
    """
    引力魔方-报表-汇总数据获取
    阿里妈妈引力魔方-报表-自定义分析，汇总数据获取
    * @param 日期，
    * @param 文件保存路径，保存本地文件路径
    * @param 效果，['点击效果','展现效果']
    * @param 周期，['转化效果周期1天','转化效果周期3天','转化效果周期7天','转化效果周期15天','转化效果周期30天']
    * @param web_page，
    * @return file_path，
    """
    outputs = ["file_path"]
    inputs = {"日期":日期,"文件保存路径":文件保存路径,"效果":效果,"周期":周期,"web_page":web_page}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_d91a274e.process7", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_d91a274e.process7",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_d91a274e.process7", extension_module, activity_func)

def process9(web_page,日期,周期):
    """
    万象台-报表-汇总数据获取
    阿里妈妈万象台-报表-账户总览汇总数据获取
    * @param web_page，
    * @param 日期，
    * @param 周期，
    * @return 消耗汇总数据，
    * @return 推广汇总数据，
    """
    outputs = ["消耗汇总数据","推广汇总数据"]
    inputs = {"web_page":web_page,"日期":日期,"周期":周期}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_d91a274e.process9", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_d91a274e.process9",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_d91a274e.process9", extension_module, activity_func)

def process13(web_page,日期,周期,效果,文件保存路径):
    """
    品销宝-报表-明星店铺报表数据获取
    阿里妈妈品销宝-报表-明星店铺报表数据获取
    * @param web_page，
    * @param 日期，
    * @param 周期，
    * @param 效果，
    * @param 文件保存路径，
    * @return file_path，
    """
    outputs = ["file_path"]
    inputs = {"web_page":web_page,"日期":日期,"周期":周期,"效果":效果,"文件保存路径":文件保存路径}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_d91a274e.process13", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_d91a274e.process13",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_d91a274e.process13", extension_module, activity_func)

def process15(日期,周期,效果,web_page,文件保存路径):
    """
    超级钻展-报表-账户汇总数据获取
    阿里妈妈超级钻展-报表-账户汇总数据获取
    * @param 日期，
    * @param 周期，
    * @param 效果，
    * @param web_page，
    * @param 文件保存路径，
    * @return file_path，
    """
    outputs = ["file_path"]
    inputs = {"日期":日期,"周期":周期,"效果":效果,"web_page":web_page,"文件保存路径":文件保存路径}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_d91a274e.process15", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_d91a274e.process15",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_d91a274e.process15", extension_module, activity_func)

def process17(web_page,日期):
    """
    商家中心-数据分析-汇总数据获取
    淘宝联盟商家中心-数据分析-推广概览，汇总数据获取
    * @param web_page，
    * @param 日期，
    * @return data，
    """
    outputs = ["data"]
    inputs = {"web_page":web_page,"日期":日期}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_d91a274e.process17", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_d91a274e.process17",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_d91a274e.process17", extension_module, activity_func)

