import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    文件路径 = ""
    数据集对象列表 = []
    if args is None:
        查询日期 = ""
        保存文件夹 = None
        细分来源 = "手淘搜索"
    else:
        查询日期 = args.get("查询日期", "")
        保存文件夹 = args.get("保存文件夹", None)
        细分来源 = args.get("细分来源", "手淘搜索")
    try:
        # ------日期参数校验
        细分来源列表 = ["手淘推荐",
        "手淘搜索",
        "手淘淘宝直播",
        "手猫搜索",
        "手猫其他店铺",
        "淘内待分类",
        "商品详情页头图推荐",
        "店铺超链",
        "逛逛",
        "关注",
        "聚划算",
        "手机浏览器访问天猫",
        "手机浏览器访问淘宝",
        "直通车"]
        xbot_visual.process.run(process="xbot_extensions.activity_47680f64.process5", package=__name__, inputs={
            "传入值": 细分来源,
            "可选项列表": lambda: 细分来源列表,
            "是否多选": False,
            "分隔符": ",",
            }, outputs=[
        ], _block=("流量_店铺来源_流量来源构成_细分来源", 3, "入参校验"))
        默认下载路径, 是否弹窗下载, 下载路径下已存在文件数 = xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.GetDownloadPath", package=__name__, inputs={
            }, outputs=[
            "默认下载路径",
            "是否弹窗下载",
            "下载路径下已存在文件数",
        ], _block=("流量_店铺来源_流量来源构成_细分来源", 4, "获取当前下载保存路径"))
        日期 = xbot_visual.datetime.to_string(datetime=查询日期, format="%Y-%m-%d", _block=("流量_店铺来源_流量来源构成_细分来源", 5, "日期时间转换为文本"))
        url = xbot_visual.programing.variable(value="https://sycm.taobao.com/flow/monitor/shopsource/construction?belong=all&dateRange=" + xbot_visual.sh_str(日期) + "%7C" + xbot_visual.sh_str(日期) + "&dateType=day&device=2&rivalUser1Id="
        , _block=("流量_店铺来源_流量来源构成_细分来源", 6, "设置变量"))
        web_page = xbot_visual.web.create(web_type="chrome", value=url, silent_running=False, wait_load_completed=True, load_timeout="120", stop_load_if_load_timeout="handleExcept", chrome_file_name=None, edge_file_name=None, bro360_file_name=None, firefox_file_name=None, arguments=None, _block=("流量_店铺来源_流量来源构成_细分来源", 7, "打开网页"))
        xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("流量_店铺来源_流量来源构成_细分来源", 8, "等待"))
        xbot_visual.web.browser.scroll_to(browser=web_page, scroll_on_element=False, element=None, search_up=False, location="screen", behavior="smooth", left="0", top="0", timeout="20", _block=("流量_店铺来源_流量来源构成_细分来源", 9, "鼠标滚动网页"))
        细分来源_详情_元素对象 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//*[text()=\"" + xbot_visual.sh_str(细分来源) + "\"]/ancestor::tr//*[text()=\"详情\"]", is_related_parent=False, parent=None, timeout="20", _block=("流量_店铺来源_流量来源构成_细分来源", 10, "获取元素对象(web)"))
        跳转uri = xbot_visual.web.element.get_details(browser=web_page, element=细分来源_详情_元素对象, operation="other", absolute_url=False, attribute_name="href", relative_to="screen", to96dpi=True, timeout="20", _block=("流量_店铺来源_流量来源构成_细分来源", 11, "获取元素信息(web)"))
        xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://sycm.taobao.com" + xbot_visual.sh_str(跳转uri), ignore_cache=False, load_timeout="120", _block=("流量_店铺来源_流量来源构成_细分来源", 12, "跳转至新网址"))
        xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("流量_店铺来源_流量来源构成_细分来源", 13, "等待"))
        #region 数据下载
        web_wait_result = xbot_visual.web.element.wait(browser=web_page, element=package.selector("流量_店铺来源_下载按钮(旧)"), state="appear", iswait=True, timeout="20", _block=("流量_店铺来源_流量来源构成_细分来源", 15, "等待元素(web)"))
        # ------获取页面信息
        店铺名 = xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.GetShopName", package=__name__, inputs={
            "平台名称": "生意参谋",
            "web_page": web_page,
            }, outputs=[
            "店铺名",
        ], _block=("流量_店铺来源_流量来源构成_细分来源", 17, "获取店铺名"))
        页面统计时间 = xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.GetElementInnerText", package=__name__, inputs={
            "web_page": web_page,
            "xpath": "//*[contains(text(), \"统计时间\")]",
            "等待元素存在": lambda: 20,
            }, outputs=[
            "元素内部文本",
        ], _block=("流量_店铺来源_流量来源构成_细分来源", 18, "获取元素String"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("流量_店铺来源_下载按钮(旧)"), simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("流量_店铺来源_流量来源构成_细分来源", 19, "点击元素(web)"))
        数据集 = xbot_visual.programing.variable(value="生意参谋_流量_流量来源_流量来源构成_" + xbot_visual.sh_str(细分来源)
        , _block=("流量_店铺来源_流量来源构成_细分来源", 20, "设置变量"))
        文件名 = xbot_visual.programing.variable(value=xbot_visual.sh_str(数据集) + "_" + xbot_visual.sh_str(日期)
        , _block=("流量_店铺来源_流量来源构成_细分来源", 21, "设置变量"))
        文件路径 = xbot_visual.process.run(process="xbot_extensions.activity_47680f64.process2", package=__name__, inputs={
            "保存文件夹": 保存文件夹,
            "文件名": 文件名,
            "是否弹窗下载": 是否弹窗下载,
            "下载前文件数量": 下载路径下已存在文件数,
            "浏览器下载保存路径": 默认下载路径,
            "最大等待时长": lambda: 120,
            }, outputs=[
            "文件路径",
        ], _block=("流量_店铺来源_流量来源构成_细分来源", 22, "下载一个文件"))
        待插入字段 = xbot_visual.programing.variable(value=lambda: [["RPA店铺名_页面", "RPA日期", "RPA页面统计日期", "RPA细分来源"] , [店铺名, 日期, 页面统计时间, 细分来源]]
        , _block=("流量_店铺来源_流量来源构成_细分来源", 23, "设置变量"))
        xbot_visual.list.append_or_insert(lst=数据集对象列表, insert_way="append", index="0", elem=lambda: {"数据集": 数据集, "文件路径": 文件路径, "待插入字段": 待插入字段, "去重主键": ["RPA日期", "来源名称", "访客数"]}, _block=("流量_店铺来源_流量来源构成_细分来源", 24, "列表插入一项"))
        xbot_visual.programing.log(type="info", text="文件路径:  " + xbot_visual.sh_str(文件路径), _block=("流量_店铺来源_流量来源构成_细分来源", 25, "打印日志"))
        #endregion
        xbot_visual.web.browser.close(operation="close_specified", browser=web_page, web_type="cef", task_kill=False, ignore_beforeunload=False, _block=("流量_店铺来源_流量来源构成_细分来源", 27, "关闭网页"))
    finally:
        args["文件路径"] = 文件路径
        args["数据集对象列表"] = 数据集对象列表
