# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, web
from .import package
from .package import variables as glv



def main(args):
    page = args.get("web_page")
    xpath = args.get("xpath")
    time_out = args.get("等待元素存在")
    element = page.find_by_xpath(xpath_selector=xpath, timeout=time_out)

    code = """
        function (ctx, input) {
            function x(xpath) {
                var result = document.evaluate(xpath, document, null, XPathResult.ANY_TYPE, null);
                return result.iterateNext()
            }

            return x(input).innerText
        }
    """
    args["元素内部文本"] = page.execute_javascript(code, xpath)

    return args["元素内部文本"]