#
# 次模块统一编写 【C 库存和销量报告】 分组下的对外api
from ._customer_returns_core import CustomerReturnsHandler
from ._storage_fee_charges_core import MonthlyStorageFeesHandler
from ._vat_transaction_core import VatTransactionHandler
from ._inventory_reports_core import InventoryReportsHandler



def customer_returns(web_page, save_dir, save_name, start_date,end_date, report_type="CSV", wait_time=300):
    """买家退货"""
    handler = CustomerReturnsHandler(web_page)
    return handler.run(save_dir, save_name, start_date,end_date,report_type, wait_time)



def monthly_storage_fees(web_page, save_dir, save_name, report_type="CSV", year_month=None, wait_time=300):
    """月度仓储费"""
    handler = MonthlyStorageFeesHandler(web_page)
    res = handler.run( save_dir, save_name, report_type, year_month, wait_time)
    print(res)
    return res


def vat_transaction(web_page, site_name, save_dir, save_name, report_type="CSV", date_range=None, wait_time=300):
    """亚马逊增值税交易报告"""
    handler = VatTransactionHandler(web_page)
    return handler.run(site_name, save_dir, save_name, report_type, date_range, wait_time)


def inventory_reports(web_page, site_name, save_dir, save_name, report_type, wait_time=300):
    """库存报告"""
    handler = InventoryReportsHandler(web_page)
    return handler.run(site_name, save_dir, save_name, report_type, wait_time)