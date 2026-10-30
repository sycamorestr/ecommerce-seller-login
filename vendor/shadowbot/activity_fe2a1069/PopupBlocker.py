# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, web
from .import package
from .package import variables as glv
import xbot_visual


def get_feature(platform_name):
    feature_map = {
        "抖店": [
            {"xpath": "//*[@class='y-guide']"},
            {"xpath": "//*[@class='auxo-modal-root']"}
        ],
        "生意参谋": [
            {"xpath": '//*[contains(@class,"ant-popover")]'},
            {"xpath": '//*[contains(@class, "scenario-widget")]'},
        ],
        "引力魔方": [{"xpath": '//*[contains(text(), "日常公告")]/ancestor::*[contains(@id, "popover")]'}],
        "拼多多商家后台" : [
            {"xpath": '//*[@id="umd_kits_message_box"]'},
            {"xpath": '//*[@id="umd_kits_bapp_sign"]'},
            {"xpath": '//*[@id="umd_kits_PDD_chick"]'},
            {"xpath": '//*[@id="umd_kits_SuspendPendant"]'},
            {"xpath": '//*[@id="beast-core-modal-mask"]'},
            {"xpath": '//*[@id="beast-core-modal"]'},
            {"xpath": '//*[contains(@class, "PT_popover")]'},
        ],
        "拼多多推广平台": [
            {"xpath": '//*[contains(@class, "ModalController")]'},
            {"xpath": '//*[contains(@class, "anq-popover")]'},
        ],
        "万相台": [
            {"xpath": '//*[contains(@id, "mask_dlg")]'},
        ],
        "巨量千川": [
            {"xpath": '//*[@class="my-simple-modal-container"]'},
            {"xpath": '//*[@class="effect-entry-wrapper"]'},
            {"xpath": '//*[@class="bui-popover-panel"]'},
            {"xpath": '//*[contains(@class, "byted-modal-backdrop")]'},
        ],
        "京东商智": [
            {"xpath": '//*[@class="bd-notice-modal"]'},
        ],
    }
    if platform_name not in feature_map:
        raise Exception("暂不支持此平台")

    return feature_map[platform_name]



def hide_element(page, xpathSelector):
    # 使用js后台异步隐藏元素
    js = """
        function (context, xpathSelector) {
            function find_element_by_xpath(xpath) {
                let result = document.evaluate(xpath, document, null, XPathResult.ANY_TYPE, null);
                return result
            }

            function findAndHideElement() {
                    var all_element = find_element_by_xpath(xpathSelector);
                    element = all_element.iterateNext();

                    var element_list = new Array();

                    while (element) {
                        element_list.push(element);
                        element = all_element.iterateNext();
                    }

                    console.log(element_list.length)
                    for (let i=0; i < element_list.length; i++){
                        element_list[i].hidden = true;
                    }

                    setTimeout(findAndHideElement, 300)
            }
            
            setTimeout(findAndHideElement, 300)
            
            return null;
        }
    """
    page.execute_javascript(js, xpathSelector)



def main(args):
    """
    隐藏符合条件的元素
    """

    platform_name = args.get("平台名称", "抖店")
    page = web.get_active(mode="chrome")

    features = get_feature(platform_name)
    for feature in features:
        xpath_selector = feature.get("xpath")
        hide_element(page, xpath_selector)

    # 覆盖body style属性，删除hidden
    # style="background: rgb(250, 251, 252) !important; width: calc(100% - 17px); overflow: hidden;"
    body = None
    try:
        body = xbot_visual.web.element.get_element(browser=page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//body", is_related_parent=False, parent=None, timeout="5", _block=("main", 9, "获取元素对象(web)"))
        if body is not None:
            body_style = xbot_visual.web.element.get_details(browser=page, element=body, operation="other", absolute_url=False, attribute_name="style", relative_to="screen", to96dpi=True, timeout="20", _block=("main", 11, "获取元素信息(web)"))
            body_style = body_style.replace("hidden", "")
            xbot_visual.web.element.set_attribute(browser=page, element=body, attribute_name="style", value=body_style, timeout="20", _block=("main", 13, "设置元素属性(web)"))
    except Exception as e:
        pass
