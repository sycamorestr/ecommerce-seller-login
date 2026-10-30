# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, web 
from .import package
from .package import variables as glv
from .utils import Tools

def create_coupon(web_page, coupon_name, start_time, end_time, coupon_file_path):
    Tools.check_web(web_page, 'activity/marketing-tools/create-coupon')
    web_page.find_by_xpath("//*[text()='券名称']//ancestor::div[@data-testid='beast-core-grid-col-wrapper']//following-sibling::div").input(coupon_name)
    Tools.select_date(web_page, start_time, end_time)
    web_page.find_by_xpath("//span[text()='批量导入']").click()
    web_page.find_by_xpath("//*[text()='上传文件']").upload(coupon_file_path)
    try:
        web_page.find_by_xpath("//*[text()='已同意并查看']//ancestor::label[@data-checked='false']/div[1]", timeout=2).click()
    except:
        pass
    web_page.find_by_xpath("//*[text()='确认创建']").click()


def main(args):
    
    web_page = args.get("web_page")
    coupon_name = args.get("coupon_name","测试")
    start_time = args.get("start_time","2025-01-10")
    end_time = args.get("end_time", "2025-02-10")
    coupon_file_path = args.get("coupon_file_path",'')
 
    # web_page = web.get_active(mode='chrome')
    create_coupon(web_page, coupon_name, start_time, end_time, coupon_file_path)

