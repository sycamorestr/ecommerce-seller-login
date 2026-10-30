from .import package
import xbot_visual
from . import sponsored_activities_download
from . import total_balance
from . import buyer_message
from . import payment_report_lib_month
from . import translation_view_trans
from . import sale_control_pannel
from . import sales_flow_dep_date
from . import sponsored_ads_reports
from . import remove_order_detail
from . import sku_cost_report
from . import classified_product_reports
from . import get_policy_compliance
from . import get_service_performance
from . import get_delivery_performance
from . import check_performance_notification
from . import screenshot_price_discount
from . import payments_past_settlements
from . import screenshot_manage_quote
from . import logistics_delivery_report
from . import get_seller_news
from . import screenshot_return_mark
from . import download_purchase_cost
from . import download_shipping_report
from . import download_erppay_report
from . import download_returnfee_report
from . import download_ad_productpromotion
from . import fill_goods_ien
from . import download_popular_terms
from . import get_advertising_history
from . import download_tax_invoice
from . import download_rating_resale
from . import screenshot_promotion_detail
from . import download_business_report
from . import download_order_report
from . import get_message_response
from . import check_dashboard_card
from . import check_home_exception
from . import get_product_policies
from . import get_order_unshipped
from . import get_inbound_performance
from . import get_lobby
from . import get_inventory_miss
from . import get_quotes_quantity
from . import return_red_warn
from . import get_stranded_inventory
from . import get_pricing_unusual
from . import get_history_day
from . import download_reports_repository
from . import delivery_manage_storage
from . import sale_deliver_goods
from . import delivery_allmanage_storage
from . import delivery_manage_health
from . import sale_all_orders
from . import delivery_inventory_bill
from . import business_reports_sub
from . import sales_comment
from . import sales_listing_control
from . import download_reports_returns
from . import download_ad_tax
from . import sponsored_reports_download
from . import epr_report
from . import new_get_deal
from . import delivery_fba_inventory
from . import pay_aged_report
from . import get_payment_amount
from . import tax_invoce
from . import all_settlements
from . import remove_shipment_details
from . import print_patment_data
from . import compensation_amount
from . import order_sales_completed
from . import vat_report
from . import switch_old_ul
from . import reserved_inventory
from . import new_ui_get_deal

def process1(网页对象):
    """
    亚马逊-店铺登录
    该指令实现了亚马逊店铺登录，只做点击登录按钮和提交验证码操作，不自动输入账号密码
    * @param 网页对象，
    """
    outputs = []
    inputs = {"网页对象":网页对象}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.amazon_ext_op.process1", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.amazon_ext_op.process1",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.amazon_ext_op.process1", extension_module, activity_func)

def process2(网页对象,站点名称):
    """
    亚马逊-切换站点
    该指令实现了亚马逊切换站点操作，自动点击切换过程出现的登录以及二次验证
    * @param 网页对象，
    * @param 站点名称，
    """
    outputs = []
    inputs = {"网页对象":网页对象,"站点名称":站点名称}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.amazon_ext_op.process2", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.amazon_ext_op.process2",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.amazon_ext_op.process2", extension_module, activity_func)

def process29(网页对象,切换语言):
    """
    亚马逊-切换语言
    该指令实现了在亚马逊后台切换页面语言的操作
    * @param 网页对象，
    * @param 切换语言，
    """
    outputs = []
    inputs = {"网页对象":网页对象,"切换语言":切换语言}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.amazon_ext_op.process29", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.amazon_ext_op.process29",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.amazon_ext_op.process29", extension_module, activity_func)

def process30(网页对象,切换语言):
    """
    亚马逊-广告页切换语言
    该指令实现了在亚马逊广告页切换语言的操作
    * @param 网页对象，
    * @param 切换语言，
    """
    outputs = []
    inputs = {"网页对象":网页对象,"切换语言":切换语言}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.amazon_ext_op.process30", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.amazon_ext_op.process30",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.amazon_ext_op.process30", extension_module, activity_func)

def process3(网页对象,站点名称,报告类型,报告标签,日期范围,保存文件夹,保存文件名,超时时间,账户类型):
    """
    亚马逊-付款报告下载
    该指令实现了付款报告库-报告库页面的文件下载操作
    * @param 网页对象，
    * @param 站点名称，
    * @param 报告类型，
    * @param 报告标签，
    * @param 日期范围，
    * @param 保存文件夹，
    * @param 保存文件名，
    * @param 超时时间，
    * @param 账户类型，
    * @return run_status，
    * @return err_msg，
    * @return download_file_path，
    """
    outputs = ["run_status","err_msg","download_file_path"]
    inputs = {"网页对象":网页对象,"站点名称":站点名称,"报告类型":报告类型,"报告标签":报告标签,"日期范围":日期范围,"保存文件夹":保存文件夹,"保存文件名":保存文件名,"超时时间":超时时间,"账户类型":账户类型}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.amazon_ext_op.process3", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.amazon_ext_op.process3",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.amazon_ext_op.process3", extension_module, activity_func)

def process4(网页对象,站点名称,最小提现金额,逗号处理):
    """
    亚马逊-自动提现
    该指令实现亚马逊切换站点并提现的操作
    * @param 网页对象，
    * @param 站点名称，
    * @param 最小提现金额，
    * @param 逗号处理，
    * @return run_status，
    * @return err_msg，
    * @return wd_amount，
    * @return standard_current_balance，
    * @return invoice_payment_current_balance，
    * @return total_amount，
    """
    outputs = ["run_status","err_msg","wd_amount","standard_current_balance","invoice_payment_current_balance","total_amount"]
    inputs = {"网页对象":网页对象,"站点名称":站点名称,"最小提现金额":最小提现金额,"逗号处理":逗号处理}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.amazon_ext_op.process4", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.amazon_ext_op.process4",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.amazon_ext_op.process4", extension_module, activity_func)

def process5(网页对象,站点名称,保存文件夹,保存文件名,结算周期,账户类型,截图区域):
    """
    亚马逊-结算一览截图
    该指令实现亚马逊切换站点并在结算一览页面截图的操作
    * @param 网页对象，
    * @param 站点名称，
    * @param 保存文件夹，
    * @param 保存文件名，
    * @param 结算周期，
    * @param 账户类型，
    * @param 截图区域，
    * @return run_status，
    * @return err_msg，
    * @return screenshot_file_name，
    * @return currency_total_amount，
    """
    outputs = ["run_status","err_msg","screenshot_file_name","currency_total_amount"]
    inputs = {"网页对象":网页对象,"站点名称":站点名称,"保存文件夹":保存文件夹,"保存文件名":保存文件名,"结算周期":结算周期,"账户类型":账户类型,"截图区域":截图区域}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.amazon_ext_op.process5", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.amazon_ext_op.process5",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.amazon_ext_op.process5", extension_module, activity_func)

def process10(网页对象,站点名称,ASIN列表,上次更新天数):
    """
    亚马逊-买家之声
    该指令实现了自动切换站点，根据ASIN抓取买家之声页面的数据以及sku的详细数据的操作
    * @param 网页对象，
    * @param 站点名称，
    * @param ASIN列表，
    * @param 上次更新天数，
    * @return run_status，
    * @return err_msg，
    * @return asin_data，
    * @return not_exist_asin_list，
    """
    outputs = ["run_status","err_msg","asin_data","not_exist_asin_list"]
    inputs = {"网页对象":网页对象,"站点名称":站点名称,"ASIN列表":ASIN列表,"上次更新天数":上次更新天数}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.amazon_ext_op.process10", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.amazon_ext_op.process10",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.amazon_ext_op.process10", extension_module, activity_func)

def process12(网页对象,保存文件夹,保存文件名,下载类型,起始日期,等待时间,结束日期):
    """
    亚马逊-买家退货
    该指令实现亚马逊切换站点并下载【买家退货报表】
    * @param 网页对象，
    * @param 保存文件夹，
    * @param 保存文件名，
    * @param 下载类型，
    * @param 起始日期，
    * @param 等待时间，
    * @param 结束日期，
    * @return run_status，
    * @return err_msg，
    * @return download_file_path，
    """
    outputs = ["run_status","err_msg","download_file_path"]
    inputs = {"网页对象":网页对象,"保存文件夹":保存文件夹,"保存文件名":保存文件名,"下载类型":下载类型,"起始日期":起始日期,"等待时间":等待时间,"结束日期":结束日期}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.amazon_ext_op.process12", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.amazon_ext_op.process12",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.amazon_ext_op.process12", extension_module, activity_func)

def process14(网页对象,保存文件夹,保存文件名,下载类型,下载年月,等待时间):
    """
    亚马逊-月度仓储费
    该指令实现亚马逊切换站点并下载【月度仓储费报表】
    * @param 网页对象，
    * @param 保存文件夹，
    * @param 保存文件名，
    * @param 下载类型，
    * @param 下载年月，
    * @param 等待时间，
    * @return run_status，
    * @return err_msg，
    * @return download_file_path，
    """
    outputs = ["run_status","err_msg","download_file_path"]
    inputs = {"网页对象":网页对象,"保存文件夹":保存文件夹,"保存文件名":保存文件名,"下载类型":下载类型,"下载年月":下载年月,"等待时间":等待时间}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.amazon_ext_op.process14", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.amazon_ext_op.process14",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.amazon_ext_op.process14", extension_module, activity_func)

def process19(网页对象,站点名称):
    """
    亚马逊-查询优惠券
    该指令实现了自动切换站点，查找所有优惠券的操作
    * @param 网页对象，
    * @param 站点名称，
    * @return run_status，
    * @return err_msg，
    * @return coupons，
    * @return header_fields，
    """
    outputs = ["run_status","err_msg","coupons","header_fields"]
    inputs = {"网页对象":网页对象,"站点名称":站点名称}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.amazon_ext_op.process19", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.amazon_ext_op.process19",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.amazon_ext_op.process19", extension_module, activity_func)

def process27(网页对象,站点名称,报告类型,保存文件夹,保存文件名):
    """
    亚马逊-库存报告
    该指令实现亚马逊切换站点并进入库存报告页面，下载指定类型的报告
    * @param 网页对象，
    * @param 站点名称，
    * @param 报告类型，
    * @param 保存文件夹，
    * @param 保存文件名，
    * @return run_status，
    * @return err_msg，
    * @return download_file_path，
    """
    outputs = ["run_status","err_msg","download_file_path"]
    inputs = {"网页对象":网页对象,"站点名称":站点名称,"报告类型":报告类型,"保存文件夹":保存文件夹,"保存文件名":保存文件名}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.amazon_ext_op.process27", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.amazon_ext_op.process27",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.amazon_ext_op.process27", extension_module, activity_func)

def process32(网页对象,站点名称,结算周期,切换语言为中文,账户类型):
    """
    亚马逊-结算一览账户数据
    该指令实现亚马逊切换站点并在结算一览页面抓取账户数据的操作
    * @param 网页对象，
    * @param 站点名称，
    * @param 结算周期，
    * @param 切换语言为中文，
    * @param 账户类型，
    * @return run_status，
    * @return err_msg，
    * @return amount_data，
    """
    outputs = ["run_status","err_msg","amount_data"]
    inputs = {"网页对象":网页对象,"站点名称":站点名称,"结算周期":结算周期,"切换语言为中文":切换语言为中文,"账户类型":账户类型}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.amazon_ext_op.process32", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.amazon_ext_op.process32",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.amazon_ext_op.process32", extension_module, activity_func)

def process34(网页对象,品牌帖子网址,文件路径,标题,asin列表,开始时间,结束时间,发送类型):
    """
    亚马逊-发送POST
    该指令实现了在亚马逊后台指定品牌发送POST的操作
    * @param 网页对象，
    * @param 品牌帖子网址，
    * @param 文件路径，
    * @param 标题，
    * @param asin列表，
    * @param 开始时间，
    * @param 结束时间，
    * @param 发送类型，
    """
    outputs = []
    inputs = {"网页对象":网页对象,"品牌帖子网址":品牌帖子网址,"文件路径":文件路径,"标题":标题,"asin列表":asin列表,"开始时间":开始时间,"结束时间":结束时间,"发送类型":发送类型}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.amazon_ext_op.process34", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.amazon_ext_op.process34",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.amazon_ext_op.process34", extension_module, activity_func)

def process43(网页对象,站点,最小提现金额,银行卡尾号):
    """
    亚马逊-自动提现-标准订单
    该指令实现亚马逊切换站点并提现标准订单的操作
    * @param 网页对象，
    * @param 站点，
    * @param 最小提现金额，
    * @param 银行卡尾号，
    * @return 运行结果，
    * @return 错误信息，
    * @return 标准订单金额，
    """
    outputs = ["运行结果","错误信息","标准订单金额"]
    inputs = {"网页对象":网页对象,"站点":站点,"最小提现金额":最小提现金额,"银行卡尾号":银行卡尾号}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.amazon_ext_op.process43", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.amazon_ext_op.process43",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.amazon_ext_op.process43", extension_module, activity_func)

def process44(网页对象,站点,最小提现金额,银行卡尾号):
    """
    亚马逊-自动提现-发票支付订单
    该指令实现亚马逊切换站点并提现标准订单的操作
    * @param 网页对象，
    * @param 站点，
    * @param 最小提现金额，
    * @param 银行卡尾号，
    * @return 运行结果，
    * @return 错误信息，
    * @return 发票支付订单金额，
    """
    outputs = ["运行结果","错误信息","发票支付订单金额"]
    inputs = {"网页对象":网页对象,"站点":站点,"最小提现金额":最小提现金额,"银行卡尾号":银行卡尾号}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.amazon_ext_op.process44", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.amazon_ext_op.process44",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.amazon_ext_op.process44", extension_module, activity_func)

def process47(网页对象,站点,最小提现金额,银行卡尾号,提现类型):
    """
    亚马逊-自动提现-自定义类型
    该指令实现亚马逊切换站点并自定义提现类型操作提现的操作
    * @param 网页对象，
    * @param 站点，
    * @param 最小提现金额，
    * @param 银行卡尾号，
    * @param 提现类型，
    * @return 提现结果，
    """
    outputs = ["提现结果"]
    inputs = {"网页对象":网页对象,"站点":站点,"最小提现金额":最小提现金额,"银行卡尾号":银行卡尾号,"提现类型":提现类型}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.amazon_ext_op.process47", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.amazon_ext_op.process47",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.amazon_ext_op.process47", extension_module, activity_func)

