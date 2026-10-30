import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    输出文件路径 = ""
    执行状态 = "成功"
    if args is None:
        查询日期 = ""
        保存文件夹 = None
        分析类型 = ""
        开启页面统计时间校验 = True
        web_page = None
    else:
        查询日期 = args.get("查询日期", "")
        保存文件夹 = args.get("保存文件夹", None)
        分析类型 = args.get("分析类型", "")
        开启页面统计时间校验 = args.get("开启页面统计时间校验", True)
        web_page = args.get("web_page", None)
    try:
        # 获取网页对象类型
        mode = xbot_visual.process.invoke_module(module="utils", package=__name__, function="get_active_by_web_page", params={
            "web_page": web_page,
        }, _block=("服务-客服绩效-专项分析数据获取", 2, "调用模块"))
        #region 跳转至目标页面
        # ---此指令自动关闭浏览器下载文件手动保存框，并获取下载保存路径
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type=mode, mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("服务-客服绩效-专项分析数据获取", 5, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("服务-客服绩效-专项分析数据获取", 5,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://sycm.taobao.com/qos/service/frame/customer/performance/new", ignore_cache=False, load_timeout="20", _block=("服务-客服绩效-专项分析数据获取", 6, "跳转至新网址"))
        xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("服务-客服绩效-专项分析数据获取", 7, "等待"))
        # xbot_extensions.activity_fe2a1069.PopupBlocker
        #endregion
        # 处理弹窗
        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("生意参谋_AI询问弹窗"), _block=("服务-客服绩效-专项分析数据获取", 11, "IF 元素可见(web)")):
            xbot_visual.web.element.click(browser=web_page, element=package.selector("生意参谋_AI询问弹窗"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("服务-客服绩效-专项分析数据获取", 12, "点击元素(web)"))
        #endif
        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("生意参谋_618弹窗"), _block=("服务-客服绩效-专项分析数据获取", 14, "IF 元素可见(web)")):
            xbot_visual.web.element.click(browser=web_page, element=package.selector("生意参谋_618弹窗"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("服务-客服绩效-专项分析数据获取", 15, "点击元素(web)"))
        #endif
        # 此处插入时间选择&校验指令
        页面统计时间 = xbot_visual.process.run(process="xbot_extensions.activity_c80700f1.process7", package=__name__, inputs={
            "日期": 查询日期,
            "web_page": lambda: web_page,
            }, outputs=[
            "页面统计时间",
        ], _block=("服务-客服绩效-专项分析数据获取", 18, "服务-绩效-通用时间选择"))
        #region 功能模块 : 开启页面统计时间校验 
        if xbot_visual.workflow.test(operand1=开启页面统计时间校验, operator="is true", operand2="", operator_options="{}", _block=("服务-客服绩效-专项分析数据获取", 20, "IF 条件")):
            _Res = xbot_visual.process.run(process="process46", package=__name__, inputs={
                "查询日期": 查询日期,
                "页面统计时间": 页面统计时间,
                }, outputs=[
                "判断结果",
            ], _block=("服务-客服绩效-专项分析数据获取", 21, "调用流程"))
            if xbot_visual.workflow.test(operand1=_Res.判断结果, operator="in", operand2="异常", operator_options="{\"ignoreCase\":\"False\"}", _block=("服务-客服绩效-专项分析数据获取", 22, "IF 条件")):
                执行状态 = xbot_visual.programing.variable(value=_Res.判断结果
                , _block=("服务-客服绩效-专项分析数据获取", 23, "设置变量"))
                return
            #endif
        #endif
        #endregion
        #region 类型选择
        xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.ClickByXpath", package=__name__, inputs={
            "web_page": web_page,
            "xpathSelector": "//*[text()=\"专项分析\"]",
            "获取元素超时": lambda: 5,
            "执行成功后等待": lambda: 0,
            "是否模拟人工": False,
            "按钮": "left",
            "retry_count": lambda: 1,
            "refresh": False,
            "是否为iframe对象": True,
            }, outputs=[
        ], _block=("服务-客服绩效-专项分析数据获取", 29, "点击Xpath元素"))
        xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.ClickByXpath", package=__name__, inputs={
            "web_page": web_page,
            "xpathSelector": "//*[text()=\"" + xbot_visual.sh_str(分析类型.strip()) + "\"]",
            "获取元素超时": lambda: 5,
            "执行成功后等待": lambda: 0,
            "是否模拟人工": False,
            "按钮": "left",
            "retry_count": lambda: 1,
            "refresh": False,
            "是否为iframe对象": True,
            }, outputs=[
        ], _block=("服务-客服绩效-专项分析数据获取", 30, "点击Xpath元素"))
        #endregion
        # 文件下载到默认文件夹后再转存到目标文件夹
        #region 处理下载文件并重命名
        xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.ClickByXpath", package=__name__, inputs={
            "web_page": web_page,
            "xpathSelector": "//*[text()=\"下载\"]",
            "获取元素超时": lambda: 5,
            "执行成功后等待": lambda: 0,
            "是否模拟人工": False,
            "按钮": "left",
            "retry_count": lambda: 1,
            "refresh": False,
            "是否为iframe对象": True,
            }, outputs=[
        ], _block=("服务-客服绩效-专项分析数据获取", 34, "点击Xpath元素"))
        店铺名 = xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.GetElementInnerText", package=__name__, inputs={
            "web_page": web_page,
            "xpath": "//span[contains(@class, \"module-title\")]",
            "等待元素存在": lambda: 20,
            }, outputs=[
            "元素内部文本",
        ], _block=("服务-客服绩效-专项分析数据获取", 35, "获取元素String"))
        文件名 = xbot_visual.programing.variable(value="生意参谋-服务-客服绩效-专项分析-" + xbot_visual.sh_str(分析类型) + "-" + xbot_visual.sh_str(页面统计时间)
        , _block=("服务-客服绩效-专项分析数据获取", 36, "设置变量"))
        输出文件路径 = xbot_visual.web.handle_save_dialog(web_type=mode, dialog_result="OK", file_folder=保存文件夹, use_custom_filename=True, file_name=xbot_visual.sh_str(文件名) + ".xlsx", save_behavior="overwrite", wait_complete=False, wait_complete_timeout="", simulate=False, clipboard_input=False, input_type="automatic", wait_appear_timeout="20", force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", _block=("服务-客服绩效-专项分析数据获取", 37, "处理下载对话框"))
        xbot_visual.programing.log(type="info", text=文件名, _block=("服务-客服绩效-专项分析数据获取", 38, "打印日志"))
        #endregion
        # web.element.click
        # web.element.click
        # web.element.click
        # web.handle_save_dialog
    finally:
        args["输出文件路径"] = 输出文件路径
        args["执行状态"] = 执行状态
