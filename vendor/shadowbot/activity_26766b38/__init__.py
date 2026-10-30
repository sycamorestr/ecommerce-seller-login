from .import package
import xbot_visual
from . import server_goods_detail_enquire
from . import server_goods_detail_sale
from . import service_performance_quality_detail

def process2(查询日期,保存文件夹,开启页面统计时间校验):
    """
    品类-宏观监控核心指标监控数据获取
    品类板块下 宏观监控-核心指标监控-商品效率监控-下核心指标监控数据下载
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期选择
    * @param 保存文件夹，
    * @param 开启页面统计时间校验，
    * @return 输出文件路径，
    * @return 执行状态，
    """
    outputs = ["输出文件路径","执行状态"]
    inputs = {"查询日期":查询日期,"保存文件夹":保存文件夹,"开启页面统计时间校验":开启页面统计时间校验}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process2", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process2",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process2", extension_module, activity_func)

def process3(保存文件夹,查询日期,开启页面统计时间校验,网页对象,选择视角,文件名):
    """
    品类-全部商品排行数据获取
    品类板块下 商品排行-商品排行-全部商品排行 数据下载
    * @param 保存文件夹，
    * @param 查询日期，
    * @param 开启页面统计时间校验，
    * @param 网页对象，
    * @param 选择视角，
    * @param 文件名，需要带扩展名
    * @return 输出文件路径，
    * @return 执行状态，
    * @return 数据集对象列表，
    """
    outputs = ["输出文件路径","执行状态","数据集对象列表"]
    inputs = {"保存文件夹":保存文件夹,"查询日期":查询日期,"开启页面统计时间校验":开启页面统计时间校验,"网页对象":网页对象,"选择视角":选择视角,"文件名":文件名}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process3", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process3",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process3", extension_module, activity_func)

def process4(sku列表,终端选择,保存文件夹,查询日期,开启页面统计时间校验):
    """
    品类-商品360销售分析核心概况数据获取
    品类板块下 商品360-销售分析-核心概况数据下载
    * @param sku列表，
    * @param 终端选择，无线端/所有终端
    * @param 保存文件夹，
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期选择
    * @param 开启页面统计时间校验，
    * @return 执行状态，
    * @return 失败sku列表，
    * @return 文件下载路径，
    """
    outputs = ["执行状态","失败sku列表","文件下载路径"]
    inputs = {"sku列表":sku列表,"终端选择":终端选择,"保存文件夹":保存文件夹,"查询日期":查询日期,"开启页面统计时间校验":开启页面统计时间校验}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process4", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process4",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process4", extension_module, activity_func)

def process5(sku列表,终端选择,保存文件夹,查询日期,开启页面统计时间校验):
    """
    品类-商品360销售分析sku销售详情数据获取
    品类板块下 商品360-销售分析-sku销售详情 数据下载
    * @param sku列表，
    * @param 终端选择，
    * @param 保存文件夹，
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期选择
    * @param 开启页面统计时间校验，
    * @return 执行状态，
    * @return 失败sku列表，
    """
    outputs = ["执行状态","失败sku列表"]
    inputs = {"sku列表":sku列表,"终端选择":终端选择,"保存文件夹":保存文件夹,"查询日期":查询日期,"开启页面统计时间校验":开启页面统计时间校验}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process5", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process5",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process5", extension_module, activity_func)

def process6(查询日期,类目选择,保存文件夹,开启页面统计时间校验,网页对象):
    """
    品类-品类360排行数据获取
    品类板块下-品类360-品类排行 标准类目/导购类目 数据下载
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期选择
    * @param 类目选择，
    * @param 保存文件夹，
    * @param 开启页面统计时间校验，
    * @param 网页对象，
    * @return 输出文件路径，
    * @return 执行状态，
    """
    outputs = ["输出文件路径","执行状态"]
    inputs = {"查询日期":查询日期,"类目选择":类目选择,"保存文件夹":保存文件夹,"开启页面统计时间校验":开启页面统计时间校验,"网页对象":网页对象}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process6", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process6",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process6", extension_module, activity_func)

def process7(查询日期,保存文件夹,开启页面统计时间校验):
    """
    服务-核心监控-客服团队概况数据获取
    用于 生意参谋-服务-核心监控-客服团队概况数据的获取
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期日周月
    * @param 保存文件夹，
    * @param 开启页面统计时间校验，
    * @return 输出文件路径，
    * @return 执行状态，
    """
    outputs = ["输出文件路径","执行状态"]
    inputs = {"查询日期":查询日期,"保存文件夹":保存文件夹,"开启页面统计时间校验":开启页面统计时间校验}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process7", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process7",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process7", extension_module, activity_func)

def process8(查询日期,保存文件夹,排名方式,开启页面统计时间校验):
    """
    服务-核心监控-客服排名数据获取
    用于 生意参谋-服务-核心监控-客服排名 数据的获取
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期日周月
    * @param 保存文件夹，
    * @param 排名方式，客服排名/客服组排名
    * @param 开启页面统计时间校验，
    * @return 输出文件路径，
    * @return 执行状态，
    """
    outputs = ["输出文件路径","执行状态"]
    inputs = {"查询日期":查询日期,"保存文件夹":保存文件夹,"排名方式":排名方式,"开启页面统计时间校验":开启页面统计时间校验}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process8", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process8",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process8", extension_module, activity_func)

def process9(查询日期,保存文件夹,分析范围,汇总分析类型,开启页面统计时间校验):
    """
    服务-店铺绩效-业绩分析数据获取
    用于 生意参谋-服务-店铺绩效-业绩分析 数据的获取
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期日周月
    * @param 保存文件夹，
    * @param 分析范围，汇总分析/询单到下单/...
    * @param 汇总分析类型，店铺/客服/静默
    * @param 开启页面统计时间校验，
    * @return 输出文件路径，
    * @return 执行状态，
    """
    outputs = ["输出文件路径","执行状态"]
    inputs = {"查询日期":查询日期,"保存文件夹":保存文件夹,"分析范围":分析范围,"汇总分析类型":汇总分析类型,"开启页面统计时间校验":开启页面统计时间校验}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process9", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process9",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process9", extension_module, activity_func)

def process10(查询日期,保存文件夹,售后退款处理类型,开启页面统计时间校验):
    """
    服务-店铺绩效-售后分析数据获取
    用于 生意参谋-服务-店铺绩效-售后分析数据的获取
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期日周月
    * @param 保存文件夹，
    * @param 售后退款处理类型，店铺/未发货仅退款
    * @param 开启页面统计时间校验，
    * @return 输出文件路径，
    * @return 执行状态，
    """
    outputs = ["输出文件路径","执行状态"]
    inputs = {"查询日期":查询日期,"保存文件夹":保存文件夹,"售后退款处理类型":售后退款处理类型,"开启页面统计时间校验":开启页面统计时间校验}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process10", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process10",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process10", extension_module, activity_func)

def process11(查询日期,保存文件夹,专项分析类型,分析内容,开启页面统计时间校验):
    """
    服务_店铺绩效-专项分析数据获取
    用于 生意参谋-服务-店铺绩效-专项分析数据的获取
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期日周月
    * @param 保存文件夹，
    * @param 专项分析类型，客单价分析/咨询接待分析/商品销售分析/...
    * @param 分析内容，店铺/客服/静默
    * @param 开启页面统计时间校验，
    * @return 输出文件路径，
    * @return 执行状态，
    """
    outputs = ["输出文件路径","执行状态"]
    inputs = {"查询日期":查询日期,"保存文件夹":保存文件夹,"专项分析类型":专项分析类型,"分析内容":分析内容,"开启页面统计时间校验":开启页面统计时间校验}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process11", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process11",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process11", extension_module, activity_func)

def process12(查询日期,保存文件夹,分析范围,开启页面统计时间校验,web_page):
    """
    服务-客服绩效-业绩分析数据获取
    用于 生意参谋-服务-客服绩效-业绩分析数据的获取
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期日周月
    * @param 保存文件夹，
    * @param 分析范围，汇总分析/查询到下单/下单到付款/询单到付款/付款分析
    * @param 开启页面统计时间校验，
    * @param web_page，
    * @return 输出文件路径，
    * @return 执行状态，
    """
    outputs = ["输出文件路径","执行状态"]
    inputs = {"查询日期":查询日期,"保存文件夹":保存文件夹,"分析范围":分析范围,"开启页面统计时间校验":开启页面统计时间校验,"web_page":web_page}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process12", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process12",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process12", extension_module, activity_func)

def process13(查询日期,保存文件夹,分析类型,开启页面统计时间校验,web_page):
    """
    服务-客服绩效-专项分析数据获取
    用于 生意参谋-服务-客服绩效-专项分析数据的获取
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期日周月
    * @param 保存文件夹，
    * @param 分析类型，
    * @param 开启页面统计时间校验，
    * @param web_page，
    * @return 输出文件路径，
    * @return 执行状态，
    """
    outputs = ["输出文件路径","执行状态"]
    inputs = {"查询日期":查询日期,"保存文件夹":保存文件夹,"分析类型":分析类型,"开启页面统计时间校验":开启页面统计时间校验,"web_page":web_page}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process13", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process13",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process13", extension_module, activity_func)

def process14(查询日期,保存文件夹,售后分析类型,开启页面统计时间校验):
    """
    服务-客服绩效-售后分析数据获取
    用于 生意参谋-服务-客服绩效-售后分析数据的获取
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期日周月
    * @param 保存文件夹，
    * @param 售后分析类型，售后退款处理/售后挽留分析
    * @param 开启页面统计时间校验，
    * @return 输出文件路径，
    * @return 执行状态，
    """
    outputs = ["输出文件路径","执行状态"]
    inputs = {"查询日期":查询日期,"保存文件夹":保存文件夹,"售后分析类型":售后分析类型,"开启页面统计时间校验":开启页面统计时间校验}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process14", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process14",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process14", extension_module, activity_func)

def process15(查询日期,保存文件夹,接待明细类型,开启页面统计时间校验):
    """
    服务-绩效明细-接待明细数据获取
    用于 生意参谋-服务-绩效明细-接待明细数据的获取
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期日周月
    * @param 保存文件夹，
    * @param 接待明细类型，
    * @param 开启页面统计时间校验，
    * @return 输出文件路径，
    * @return 执行状态，
    """
    outputs = ["输出文件路径","执行状态"]
    inputs = {"查询日期":查询日期,"保存文件夹":保存文件夹,"接待明细类型":接待明细类型,"开启页面统计时间校验":开启页面统计时间校验}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process15", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process15",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process15", extension_module, activity_func)

def process16(查询日期,保存文件夹,成交明细类型,开启页面统计时间校验):
    """
    服务-绩效明细-成交明细数据下载
    用于 生意参谋-服务-绩效明细-成交明细数据的获取
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期日周月
    * @param 保存文件夹，
    * @param 成交明细类型，
    * @param 开启页面统计时间校验，
    * @return 输出文件路径，
    * @return 执行状态，
    """
    outputs = ["输出文件路径","执行状态"]
    inputs = {"查询日期":查询日期,"保存文件夹":保存文件夹,"成交明细类型":成交明细类型,"开启页面统计时间校验":开启页面统计时间校验}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process16", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process16",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process16", extension_module, activity_func)

def process17(查询日期,保存文件夹,开启页面统计时间校验):
    """
    服务-绩效明细-流失明细数据获取
    用于 生意参谋-服务-绩效明细-流失明细数据的获取
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期日周月
    * @param 保存文件夹，
    * @param 开启页面统计时间校验，
    * @return 输出文件路径，
    * @return 执行状态，
    """
    outputs = ["输出文件路径","执行状态"]
    inputs = {"查询日期":查询日期,"保存文件夹":保存文件夹,"开启页面统计时间校验":开启页面统计时间校验}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process17", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process17",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process17", extension_module, activity_func)

def process18(查询日期,保存文件夹,质量明细类型,开启页面统计时间校验):
    """
    服务-绩效明细-质量明细数据获取
    用于 生意参谋-服务-绩效明细-质量明细数据的获取
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期日周月
    * @param 保存文件夹，
    * @param 质量明细类型，
    * @param 开启页面统计时间校验，
    * @return 输出文件路径，
    * @return 执行状态，
    """
    outputs = ["输出文件路径","执行状态"]
    inputs = {"查询日期":查询日期,"保存文件夹":保存文件夹,"质量明细类型":质量明细类型,"开启页面统计时间校验":开启页面统计时间校验}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process18", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process18",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process18", extension_module, activity_func)

def process19(查询日期,保存文件夹,售后明细类型,开启页面统计时间校验):
    """
    服务-绩效明细-售后明细数据获取
    用于 生意参谋-服务-绩效明细-售后明细数据的获取
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期日周月
    * @param 保存文件夹，
    * @param 售后明细类型，
    * @param 开启页面统计时间校验，
    * @return 输出文件路径，
    * @return 执行状态，
    """
    outputs = ["输出文件路径","执行状态"]
    inputs = {"查询日期":查询日期,"保存文件夹":保存文件夹,"售后明细类型":售后明细类型,"开启页面统计时间校验":开启页面统计时间校验}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process19", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process19",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process19", extension_module, activity_func)

def process20(查询日期,保存文件夹,快捷日期):
    """
    交易-交易概况-交易总览数据获取
    用于 生意参谋-交易-交易概况-交易总览数据的获取
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期选择
    * @param 保存文件夹，
    * @param 快捷日期，
    * @return 输出文件路径，
    """
    outputs = ["输出文件路径"]
    inputs = {"查询日期":查询日期,"保存文件夹":保存文件夹,"快捷日期":快捷日期}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process20", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process20",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process20", extension_module, activity_func)

def process21(查询日期,保存文件夹):
    """
    交易-交易构成-终端构成数据获取
    用于 生意参谋-交易-交易构成-终端构成数据的获取
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期选择
    * @param 保存文件夹，
    * @return 输出文件路径，
    """
    outputs = ["输出文件路径"]
    inputs = {"查询日期":查询日期,"保存文件夹":保存文件夹}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process21", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process21",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process21", extension_module, activity_func)

def process22(查询日期,保存文件夹,终端选择):
    """
    交易-交易构成-类目构成数据获取
    用于 生意参谋-交易-交易构成-类目构成数据的获取
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期选择
    * @param 保存文件夹，
    * @param 终端选择，
    * @return 输出文件路径，
    """
    outputs = ["输出文件路径"]
    inputs = {"查询日期":查询日期,"保存文件夹":保存文件夹,"终端选择":终端选择}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process22", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process22",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process22", extension_module, activity_func)

def process23(查询日期,保存文件夹,终端选择):
    """
    交易-交易构成-品牌构成数据获取
    用于 生意参谋-交易-交易构成-品牌构成数据的获取
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期选择
    * @param 保存文件夹，
    * @param 终端选择，
    * @return 输出文件路径，
    """
    outputs = ["输出文件路径"]
    inputs = {"查询日期":查询日期,"保存文件夹":保存文件夹,"终端选择":终端选择}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process23", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process23",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process23", extension_module, activity_func)

def process24(查询日期,保存文件夹,终端选择):
    """
    交易-交易构成-价格带构成数据获取
    用于 生意参谋-交易-交易构成-价格带构成数据的获取
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期选择
    * @param 保存文件夹，
    * @param 终端选择，
    * @return 输出文件路径，
    """
    outputs = ["输出文件路径"]
    inputs = {"查询日期":查询日期,"保存文件夹":保存文件夹,"终端选择":终端选择}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process24", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process24",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process24", extension_module, activity_func)

def process25(查询日期,保存文件夹,开启页面统计时间校验):
    """
    内容-内容概况-内容全局表现数据获取
    用于 生意参谋-内容-内容概况-内容全局表现数据的获取
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期选择
    * @param 保存文件夹，
    * @param 开启页面统计时间校验，
    * @return 输出文件路径，
    * @return 执行状态，
    """
    outputs = ["输出文件路径","执行状态"]
    inputs = {"查询日期":查询日期,"保存文件夹":保存文件夹,"开启页面统计时间校验":开启页面统计时间校验}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process25", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process25",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process25", extension_module, activity_func)

def process33(查询日期,保存文件夹,开启页面统计时间校验):
    """
    内容-订阅分析-单条效果数据获取
    用于 生意参谋-内容-订阅分析-单条效果数据的获取
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期选择
    * @param 保存文件夹，
    * @param 开启页面统计时间校验，
    * @return 输出文件路径，
    * @return 执行状态，
    """
    outputs = ["输出文件路径","执行状态"]
    inputs = {"查询日期":查询日期,"保存文件夹":保存文件夹,"开启页面统计时间校验":开启页面统计时间校验}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process33", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process33",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process33", extension_module, activity_func)

def process34(查询日期,保存文件夹,开启页面统计时间校验):
    """
    内容-订阅分析-用户分析数据获取
    用于 生意参谋-内容-订阅分析-用户分析数据的获取
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期选择
    * @param 保存文件夹，
    * @param 开启页面统计时间校验，
    * @return 输出文件路径，
    * @return 执行状态，
    """
    outputs = ["输出文件路径","执行状态"]
    inputs = {"查询日期":查询日期,"保存文件夹":保存文件夹,"开启页面统计时间校验":开启页面统计时间校验}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process34", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process34",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process34", extension_module, activity_func)

def process35(查询日期,保存文件夹,开启页面统计时间校验):
    """
    内容-订阅分析-整体概况数据获取
    用于 生意参谋-内容-订阅分析-整体概况数据的获取
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期选择
    * @param 保存文件夹，
    * @param 开启页面统计时间校验，
    * @return 输出文件路径，
    * @return 执行状态，
    """
    outputs = ["输出文件路径","执行状态"]
    inputs = {"查询日期":查询日期,"保存文件夹":保存文件夹,"开启页面统计时间校验":开启页面统计时间校验}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process35", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process35",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process35", extension_module, activity_func)

def process36(查询日期,保存文件夹,开启页面统计时间校验):
    """
    内容-头图视频-整体概况数据获取
    用于 生意参谋-内容-头图视频-整体概况数据的获取
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期选择
    * @param 保存文件夹，
    * @param 开启页面统计时间校验，
    * @return 输出文件路径，
    * @return 执行状态，
    """
    outputs = ["输出文件路径","执行状态"]
    inputs = {"查询日期":查询日期,"保存文件夹":保存文件夹,"开启页面统计时间校验":开启页面统计时间校验}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process36", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process36",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process36", extension_module, activity_func)

def process37(查询日期,保存文件夹,开启页面统计时间校验):
    """
    流量-流量看板-流量总览数据获取
    用于 生意参谋-流量-流量看板-流量总览数据的获取
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期选择
    * @param 保存文件夹，
    * @param 开启页面统计时间校验，
    * @return 输出文件路径，
    * @return 执行状态，
    * @return 数据存放字典，
    """
    outputs = ["输出文件路径","执行状态","数据存放字典"]
    inputs = {"查询日期":查询日期,"保存文件夹":保存文件夹,"开启页面统计时间校验":开启页面统计时间校验}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process37", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process37",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process37", extension_module, activity_func)

def process38(查询日期,保存文件夹,开启页面统计时间校验):
    """
    流量-流量看板-流量来源排行TOP10数据获取
    用于 生意参谋-流量-流量看板-流量来源排行TOP10数据的获取
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期选择
    * @param 保存文件夹，
    * @param 开启页面统计时间校验，
    * @return 流量来源排行TOP10_数据列表，
    * @return 输出文件路径，
    * @return 执行状态，
    """
    outputs = ["流量来源排行TOP10_数据列表","输出文件路径","执行状态"]
    inputs = {"查询日期":查询日期,"保存文件夹":保存文件夹,"开启页面统计时间校验":开启页面统计时间校验}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process38", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process38",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process38", extension_module, activity_func)

def process39(查询日期,保存文件夹,开启页面统计时间校验):
    """
    流量-流量看板-商品流量排行TOP数据获取
    用于 生意参谋-流量-流量看板-商品流量排行TOP数据的获取
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期选择
    * @param 保存文件夹，
    * @param 开启页面统计时间校验，
    * @return 商品流量排行TOP10_数据列表，
    * @return 输出文件路径，
    * @return 执行状态，
    """
    outputs = ["商品流量排行TOP10_数据列表","输出文件路径","执行状态"]
    inputs = {"查询日期":查询日期,"保存文件夹":保存文件夹,"开启页面统计时间校验":开启页面统计时间校验}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process39", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process39",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process39", extension_module, activity_func)

def process41(查询日期,保存文件夹,抓取的页码数,开启页面统计时间校验,等待时间):
    """
    流量-商品来源-本店商品排行榜数据获取
    用于 生意参谋-流量-商品来源-本店商品排行榜数据的获取
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期选择
    * @param 保存文件夹，
    * @param 抓取的页码数，
    * @param 开启页面统计时间校验，
    * @param 等待时间，
    * @return 输出文件路径，
    * @return 执行状态，
    """
    outputs = ["输出文件路径","执行状态"]
    inputs = {"查询日期":查询日期,"保存文件夹":保存文件夹,"抓取的页码数":抓取的页码数,"开启页面统计时间校验":开启页面统计时间校验,"等待时间":等待时间}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process41", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process41",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process41", extension_module, activity_func)

def process42(查询日期,保存文件夹,商品ID列表,开启页面统计时间校验):
    """
    流量-商品来源-商品进店来源数据获取
    用于 生意参谋-流量-商品来源-商品进店来源数据的获取
    * @param 查询日期，自定义单日2023-01-01和当前页面快捷日期选择
    * @param 保存文件夹，
    * @param 商品ID列表，
    * @param 开启页面统计时间校验，
    * @return 输出文件路径，
    * @return 执行状态，
    """
    outputs = ["输出文件路径","执行状态"]
    inputs = {"查询日期":查询日期,"保存文件夹":保存文件夹,"商品ID列表":商品ID列表,"开启页面统计时间校验":开启页面统计时间校验}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process42", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process42",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process42", extension_module, activity_func)

def process44(查询日期,保存文件夹,开启页面统计时间校验,web_page):
    """
    首页-运营视窗整体看板数据获取
    用于 生意参谋-首页-运营视窗整体看板数据的下载
    * @param 查询日期，自定义单日2023-01-01
    * @param 保存文件夹，
    * @param 开启页面统计时间校验，
    * @param web_page，
    * @return 输出文件路径，
    * @return 执行状态，
    * @return 数据集对象列表，
    """
    outputs = ["输出文件路径","执行状态","数据集对象列表"]
    inputs = {"查询日期":查询日期,"保存文件夹":保存文件夹,"开启页面统计时间校验":开启页面统计时间校验,"web_page":web_page}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process44", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process44",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process44", extension_module, activity_func)

def process45(账号,密码,web_page):
    """
    生意参谋登录Plus
    
    * @param 账号，
    * @param 密码，
    * @param web_page，
    * @return 网页对象，
    """
    outputs = ["网页对象"]
    inputs = {"账号":账号,"密码":密码,"web_page":web_page}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process45", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process45",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process45", extension_module, activity_func)

def process50(保存文件夹,终端选择):
    """
    实时-实时总览数据获取
    用于 生意参谋-实时-实时总览数据的获取
    * @param 保存文件夹，
    * @param 终端选择，
    * @return 输出文件路径，
    * @return 执行状态，
    """
    outputs = ["输出文件路径","执行状态"]
    inputs = {"保存文件夹":保存文件夹,"终端选择":终端选择}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process50", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process50",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process50", extension_module, activity_func)

def process52(web_page):
    """
    关闭右侧客服弹窗
    
    * @param web_page，
    """
    outputs = []
    inputs = {"web_page":web_page}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process52", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process52",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process52", extension_module, activity_func)

def process56(查询日期,保存文件夹,选择新版or旧版):
    """
    流量_店铺来源_流量来源构成
    
    * @param 查询日期，仅支持单日，格式： 2023-01-01 
    * @param 保存文件夹，
    * @param 选择新版or旧版，
    * @return 文件路径，
    * @return 数据集对象列表，
    """
    outputs = ["文件路径","数据集对象列表"]
    inputs = {"查询日期":查询日期,"保存文件夹":保存文件夹,"选择新版or旧版":选择新版or旧版}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_26766b38.process56", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_26766b38.process56",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_26766b38.process56", extension_module, activity_func)

