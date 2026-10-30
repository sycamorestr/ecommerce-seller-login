# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv


def switch_area(web_page, target_area_name):
    """广告平台-切换区域"""

    # 判断是否有切换区域按钮存在
    if len(web_page.find_all_by_xpath('//span[contains(.,"当前区域")]', timeout=3)) == 0:
        print('当前托管状态不支持切换区域')
        return 
    
    # 获取区域名称
    area_xpath = '//span[contains(.,"当前区域")]/following-sibling::span'
    area_text = web_page.find_by_xpath(area_xpath).get_text()

    # 判断当前区域是否目标区域
    if area_text == target_area_name:
        return 

    # 点击当前区域，进行展开区域选择
    web_page.find_by_xpath('//span[contains(.,"当前区域")]').click()

    # 点击区域，进行选择
    area_all_xpath = '//div[.="地区"]/../div[last()]//label/div[last()]'
    area_all_sel = web_page.find_all_by_xpath(area_all_xpath)

    # 循环进行判断站点
    for area_sel in area_all_sel:
        if area_sel.get_text() == target_area_name:
            area_sel.click()
            web_page.wait_load_completed()      # 切换区域后等待页面加载完毕
            break
    else:
        raise Exception(f'未找到站点 {target_area_name}')

    # 校验站点是否切换成功
    area_text = web_page.find_by_xpath(area_xpath).get_text()
    if area_text != target_area_name:
        raise Exception(f'{target_area_name} 站点切换失败')
    else:
        print(f'{target_area_name} 站点切换成功')


def test():
    """测试模块"""
    if 'xbot_extensions' in __file__:
        return
    
    web_page = xbot.web.get_active(mode='ziniaobrowser')
    target_area_name = '全球（除美国,欧区）'
    switch_area(web_page, target_area_name)

    exit()

def main(args):
    test()

    web_page = args.get('web_page')
    target_area_name = args.get('targe_area_name')

    switch_area(web_page, target_area_name)
