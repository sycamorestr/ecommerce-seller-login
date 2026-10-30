# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
import xbot_visual
from xbot import print, sleep, win32, web
from .import package
from .package import variables as glv

from typing import Union, List
from os.path import exists
import re

from .utils import find_any_one_by_xpath, start_monitor_network, wait_responses
from .utils_beta import find_by_xpath
from . import _amazon_api
from datetime import datetime


months = [None,"January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

# 计算月份差值
def month_diff(date1, date2):  
    years_diff = date2.year - date1.year
    months_diff = date2.month - date1.month
    return years_diff * 12 + months_diff


class PostHandler:


    class XPaths:
        PageUrl = '//a[@data-menu-id="nemo-campaign-mgr-new"]'
        SettingAd = '''//button[@data-takt-id="aac-user-name-dropdown"]'''                                                                 # 广告页设置
        PostUrl = '''//a[@data-takt-id="aac-menu-item-brand-posts"]'''                                                                 # post url

        CreatePostBtn = '//*[contains(@id, "publisher:author-detail-page:create-post-")]'
        CreateImagePostBtn = '//a[@href]//button[contains(@id, "create-image")]'
        CreateVideoPostBtn = '//a[@href]//button[contains(@id, "create-video")]'
        UploadBtn1 = "//ul[contains(@id,'-uploader:upload-btn')]//li[@role='menuitem'][1]"
        UploadBtnTrigger = '//*[contains(@id,"uploader:upload-btn-trigger")]'
        CaptionIn = '//*[@id="publisher:create-post:caption-input"]'

        UpsAsinsTab = '//button[@data-takt-id="ups_asins_list_tab"]'
        # AsinIn = '//*[@id="publisher:create-post:multi-asin-picker:ups:ups-asin-search-input"]'
        AsinIn = '//*[@id="publisher:create-post:multi-asin-picker:ups:ups-product-list-input"]'
        Add = '//button[@data-takt-id="ups_add_product_list"]'

        TimePicker = '//*[@id="publisher:create-post:scheduler:time-picker"]'
        EndDatePopoverBtn = '//*[@id="publisher:create-post:scheduler:end-date-popover-btn"]'
        StartDatePopoverBtn = '//*[@id="publisher:create-post:scheduler:start-date-popover-btn"]'
        Title = '//*[@id="publisher:create-post:post-header-title"]'
        Profiles = '//*[@id="publisher:manage-profiles-page:profile-display-name" and text()="{}"]/../..//button'
        ProfilesFirst = '(//*[@id="publisher:manage-profiles-page:profile-display-name"])[1]'

        SubmitBtn = '//*[@id="publisher:create-post:submit-btn"]'
        BrandName = '//*[@id="publisher:author-detail-page:header:brand-name"]'
        NextMonth = '//button[@aria-label="go to next month"]'
        PreMonth = '//button[@aria-label="go to previous month"]'
        Day = '//*[@data-iso-date and .={}]'
        TimeIn = '//*[@id="publisher:create-post:scheduler:time-picker"]'
        Menu = '//*[@id="portal"]//button[@aria-haspopup="menu"]'

        # ==========
        UpsNotificationMessage = '//*[@data-e2e-id="ups-notification-message"]'
        UpsAsinCount = '//*[@data-e2e-id="ups-asin-list-count"]'
        PostCardImage = '//img[contains(@id,"publisher:create-post:preview:post-card-")]'
        PostCardVideo = "//div[@class='publisher-post__preview-pane']//video"
        pass


    def __init__(self, web_page: xbot.web.WebBrowser):
        self.web_page = web_page

    def check_params(self, file_path: str, title: str, asin_list: list, start_time: str, end_time: str):

        if not exists(file_path):
            raise ValueError("文件不存在，请检查 - {}".format(file_path))        

        if not isinstance(title, str) or title.strip() == "":
            raise ValueError("标题参数异常，请输入正确的标题")

        if not asin_list or len(asin_list) == 0:
            raise ValueError("asin_list 参数不能为空")


        if bool(start_time):
            try:
                xbot_visual.datetime.from_string(text=start_time, is_custom_format=True, format="%Y-%m-%d %H:%M")
            except Exception as e:
                print(e)
                raise ValueError("时间格式不正确，请按照格式 %Y-%m-%d %H:%M 输入")
        
        if bool(end_time):
            try:
                xbot_visual.datetime.from_string(text=end_time, is_custom_format=True, format="%Y-%m-%d %H:%M")
            except Exception as e:
                print(e)
                raise ValueError("时间格式不正确，请按照格式 %Y-%m-%d %H:%M 输入")            


    def to_post_page(self, post_url):
        if post_url != self.web_page.get_url():
            self.web_page.navigate(post_url, load_timeout=100)
        try:
            find_by_xpath(self.web_page, self.XPaths.CreatePostBtn, timeout=50)
            sleep(1)
        except Exception as e:
            raise Exception("进入帖子页面失败 - {}".format(e))


    def input_date(self, date, xpath):
        """填写日期"""

        dt = datetime.strptime(date, "%Y-%m-%d %H:%M")
        date_str = dt.strftime("%Y-%m-%d")
        time_str = dt.strftime("%H:%M")
        print(f"date_str: {date_str}")
        print(f"time_str: {time_str}")
        find_by_xpath(self.web_page, xpath).click(simulative=False)
        find_by_xpath(self.web_page, f'//*[@data-iso-date="{date_str}"]').click(simulative=False)
        find_by_xpath(self.web_page, f'//input[@type="time"]').hover(2)
        find_by_xpath(self.web_page, f'//input[@type="time"]').input(time_str)
        # find_by_xpath(self.web_page, xpath).click(simulative=False)
        # # 计算页面显示的日期
        # page_date_text = find_by_xpath(self.web_page, self.XPaths.Menu).get_text()
        # month, year = page_date_text.split(" ")
        # month = months.index(month)
        # page_date = datetime.strptime("{}-{}-01".format(year, month), "%Y-%m-%d") 
        # # date = str(page_date)
        # print(page_date)
        # # 计算月份差值
        # tmp_date, tmp_time = date.split(" ")
        # print(tmp_time)
        # h, m, _ = tmp_time.split(":")
        # date = datetime.strptime(tmp_date, "%Y-%m-%d")  
        # offset = month_diff(page_date, date)      

       
        # xpath = self.XPaths.NextMonth if offset > 0 else self.XPaths.PreMonth
        # for _ in range(abs(offset)):
        #     find_by_xpath(self.web_page, xpath).click(simulative=False, delay_after=0.3)
        # print(date.day)
        # find_by_xpath(self.web_page, f'//*[@data-iso-date="{date}"]').click(simulative=False)
        # find_by_xpath(self.web_page, self.XPaths.TimeIn).input(h+m)
        # find_by_xpath(self.web_page, self.XPaths.Title).click(simulative=False)
        

    def run(self, post_url, post_type, file_path: str, title: str, asin_list: list, start_time: str, end_time: str):

        # self.check_params(file_path, title, asin_list, start_time, end_time)
        self.to_post_page(post_url)
        for retry in range(3):
            find_by_xpath(self.web_page, self.XPaths.CreatePostBtn).click()
            try:
                find_by_xpath(self.web_page, self.XPaths.CreateVideoPostBtn)
                break
            except Exception as e:
                print(f"下拉框选择点击报错咯，{e}")
                
        self.web_page = web.get_active(mode=self.web_page.product_name)
        if post_type == "video" or post_type == "视频":
            find_by_xpath(self.web_page, self.XPaths.CreateVideoPostBtn).click() 
        else:
            find_by_xpath(self.web_page, self.XPaths.CreateImagePostBtn).click()
            # find_by_xpath(self.web_page, self.XPaths.CreateImagePostBtn).click()
        sleep(2)
        # find_by_xpath(self.web_page, self.XPaths.CaptionIn)
        self.web_page = web.get_active(mode=self.web_page.product_name)
        find_by_xpath(self.web_page, self.XPaths.CaptionIn)

        # find_by_xpath(self.web_page, self.XPaths.CaptionIn).input(111)
        find_by_xpath(self.web_page, self.XPaths.UploadBtnTrigger, timeout=1).click()
        find_by_xpath(self.web_page, self.XPaths.UploadBtn1).upload([file_path])     

        
        #出现上传地址非当前指定环境上传文件地址的情况
        retry = 0
        while retry < 3:
            print(retry)
            try:
                win = win32.get(class_name='Chrome_WidgetWin_1',timeout=3)
                win.find('send_post_confirm').click()
                break
            except:
                sleep(1)
                retry += 1       

        # 上传图片
        if post_type == "video" or post_type == "视频":
            try:
                find_by_xpath(self.web_page, self.XPaths.PostCardVideo, timeout=100)
            except Exception as e:
                raise ValueError("上传图片失败 - {}".format(e).replace("\n", " ")) 
        else:
            try:
                find_by_xpath(self.web_page, self.XPaths.PostCardImage, timeout=100)
            except Exception as e:
                raise ValueError("上传图片失败 - {}".format(e).replace("\n", " "))

        # 标题
        find_by_xpath(self.web_page, self.XPaths.CaptionIn).clipboard_input(title)
        
        # asins
        find_by_xpath(self.web_page, self.XPaths.UpsAsinsTab).click(simulative=False)
        find_by_xpath(self.web_page, self.XPaths.AsinIn).input("{ENTER}".join(asin_list), contains_hotkey=True)
        find_by_xpath(self.web_page, self.XPaths.Add).click(simulative=False)
        find_by_xpath(self.web_page, self.XPaths.UpsNotificationMessage, timeout=100)
        ele = find_by_xpath(self.web_page, self.XPaths.UpsAsinCount)
        if ele.get_text() == "0 products":
            raise ValueError("asin输入失败")
        if start_time:
            self.input_date(start_time, self.XPaths.StartDatePopoverBtn)
        if end_time:
            self.input_date(end_time, self.XPaths.EndDatePopoverBtn)

        
        submit_ele = find_by_xpath(self.web_page, self.XPaths.SubmitBtn)
        attr = submit_ele.get_attribute("disabled")
        if attr == "True":
            raise Exception("提交按钮不可点击")
        
        start_monitor_network(self.web_page)
        submit_ele.click()
        url = "*/brand-content-manager/api/post/updatePost"
        res = wait_responses(self.web_page, url)
        print(res)

        

        


def main(args):
    # xbot.web.close_all(mode="chrome", task_kill=True)
    web_page = xbot.web.get_active(mode="superbrowser")
    ph = PostHandler(web_page)
    ph.input_date("2025-04-16", ph.XPaths.StartDatePopoverBtn)
    # # web_page = xbot.web.create("https://advertising.amazon.com/cm/campaigns", mode="chrome")
 

