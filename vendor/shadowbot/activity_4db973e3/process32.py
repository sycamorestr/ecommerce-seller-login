import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time

def main(args):
    if args is None:
        背景图片_元素对象 = None
        提示词_元素对象 = None
        偏移 = 0
        滑块_元素对象 = None
    else:
        背景图片_元素对象 = args.get("背景图片_元素对象", None)
        提示词_元素对象 = args.get("提示词_元素对象", None)
        偏移 = args.get("偏移", 0)
        滑块_元素对象 = args.get("滑块_元素对象", None)
    try:
        for _xbot_retry_time in range(4):
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("A 单次运行", 1, "获取已打开的网页对象"))
                break
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info', text=f'第1条指令: {e}')
            time.sleep(3)
        图片的base64 = xbot_visual.web.element.get_details(browser=web_page, element=背景图片_元素对象, operation="other", absolute_url=False, attribute_name="src", relative_to="screen", to96dpi=True, timeout="20", _block=("A 单次运行", 2, "获取元素信息(web)"))
        web_element_bounding = xbot_visual.web.element.get_details(browser=web_page, element=背景图片_元素对象, operation="bound", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("A 单次运行", 3, "获取元素信息(web)"))
        # programing.log
        # ---------------保存到临时文件夹
        temp_path = xbot_visual.dir.get_special_dir(special_dir_name="TEMP", _block=("A 单次运行", 6, "获取系统文件夹路径"))
        # 320*180
        背景图片路径 = xbot_visual.sh_str(temp_path) + "\\background.png"
        success_save = xbot_visual.process.invoke_module(module="B_Tools", package=__name__, function="save_base64_image", params={
            "base64_str": 图片的base64,
            "save_path": 背景图片路径,
        }, _block=("A 单次运行", 9, "调用模块"))
        for _xbot_retry_time in range(4):
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("A 单次运行", 10, "获取已打开的网页对象"))
                break
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info', text=f'第10条指令: {e}')
            time.sleep(3)
        提示语base64 = xbot_visual.web.element.get_details(browser=web_page, element=提示词_元素对象, operation="other", absolute_url=False, attribute_name="src", relative_to="screen", to96dpi=True, timeout="20", _block=("A 单次运行", 11, "获取元素信息(web)"))
        提示语图片路径 = xbot_visual.sh_str(temp_path) + "\\提示语.png"
        success_save = xbot_visual.process.invoke_module(module="B_Tools", package=__name__, function="save_base64_image", params={
            "base64_str": 提示语base64,
            "save_path": 提示语图片路径,
        }, _block=("A 单次运行", 13, "调用模块"))
        提示语 = xbot_visual.ocr.general_text(ai_engine="shadowbot", baidu_ocr_edition="general_basic", tencent_ocr_edition="GeneralBasicOCR", aliyun_ocr_edition="ocr_general", image_source="disk", window=None, path=提示语图片路径, url="", image_region="all_region", region_x1="0", region_y1="0", region_x2="0", region_y2="0", is_pdf=False, pdf_page_number="1", detect_direction=False, detect_language=False, paragraph=False, probability=False, min_size="16", output_prob=True, output_keypoints=False, skip_detection=False, without_predicting_direction=False, prob=False, char_info=False, rotate=False, table=False, sort_page=False, _block=("A 单次运行", 14, "通用文字识别"))
        提示语 = 提示语.text
        xbot_visual.programing.log(type="info", text="备注：" + xbot_visual.sh_str(提示语), _block=("A 单次运行", 16, "打印日志"))
        提示语 = xbot_visual.text.replace_content_from_text(text=提示语, regular_pattern="", replace_way="content", replace_text="拖动滑块出现完整的", just_get_first=True, ignore_case=False, dest_text=lambda: '', _block=("A 单次运行", 17, "文本替换"))
        物品 = xbot_visual.text.replace_content_from_text(text=提示语, regular_pattern="", replace_way="content", replace_text="后就松开", just_get_first=True, ignore_case=False, dest_text=lambda: '', _block=("A 单次运行", 18, "文本替换"))
        提示语 = "帮我点击 【第" + xbot_visual.sh_str(物品) + "】的【最右侧】坐标"
        # 先通过OCR
        验证码坐标列表 = xbot_visual.web_service.captcha(engine_type="shadowbot", username=None, password=xbot_visual.decrypt(""), captcha_type="19", third_party_code="ttshitu_19_predict", image_source="image_file", image_file=背景图片路径, image_browser="", image_web_selector=None, image_window="", image_win_selector=None, image_region_x1="0", image_region_y1="0", image_region_x2="0", image_region_y2="0", imageback_source="screen", back_image_file=None, imageback_browser="", imageback_web_selector=None, imageback_window="", imageback_win_selector=None, imageback_region_x1="0", imageback_region_y1="0", imageback_region_x2="0", imageback_region_y2="0", typename=None, is_to96dpi=False, remark=提示语, _block=("A 单次运行", 21, "验证码识别"))
        # programing.log
        # 取最大的x
        max_x = xbot_visual.process.invoke_module(module="B_Tools", package=__name__, function="get_max_x", params={
            "coordinates": 验证码坐标列表,
        }, _block=("A 单次运行", 24, "调用模块"))
        for _xbot_retry_time in range(4):
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("A 单次运行", 25, "获取已打开的网页对象"))
                break
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info', text=f'第25条指令: {e}')
            time.sleep(3)
        start_element_bounding = xbot_visual.web.element.get_details(browser=web_page, element=滑块_元素对象, operation="bound", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("A 单次运行", 26, "获取元素信息(web)"))
        # programing.log
        # 待修改点：TODO   鼠标移动+sleep 2S 是为 测试看拖拽位置对不对，后续要删除
        # win32.move_mouse
        # programing.sleep
        xbot_visual.web.element.drag_to(browser=web_page, element=滑块_元素对象, drag_way="default", target_element=None, left=lambda: start_element_bounding.center_x +int( max_x)+偏移, top=start_element_bounding.center_y, delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", move_speed="slow", release_anchor_type="center", release_sudoku_part="MiddleCenter", release_offset_x="0", release_offset_y="0", timeout="20", _block=("A 单次运行", 31, "拖拽元素(web)"))
        # 验证成功后的判断，可能有别的方法
        xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("A 单次运行", 33, "等待"))
        # web.browser.wait_load_completed
    finally:
        pass
