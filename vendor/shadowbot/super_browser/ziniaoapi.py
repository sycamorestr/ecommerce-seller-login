# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
from cgi import test
import xbot
import time
import base64
import win32gui
import webbrowser
import win32gui
import win32process
import win32con
import ctypes
import os
import itertools
import psutil

from .import package
from .package import variables as glv

from xml.etree import ElementTree as ET
from xbot import print, sleep
from ziniao_oapi.common.OpenClient import OpenClient
from ziniao_oapi.request.AppTokenRequest import (
    AppTokenRequest,
    BaseRequest,
    RequestTypes,
)

from ziniao_oapi.request.UserLoginRequest import UserLoginRequest

## TODO: token过期处理, 数据获取的分页处理, 打开店铺的参数没有映射全, 未等待窗口出现
class ZiniaoAPI:
    def __init__(self, app_id, private_key):
        self.app_id = app_id  # 应用id
        self.private_key = private_key  # 应用私钥
        self.url = "https://sbappstoreapi.ziniao.com"  # 请求URL
        self.client = OpenClient(self.app_id, self.private_key, self.url)
        self.token = self.get_app_token()
        self.company_id = self.get_company_id()

    def get_app_token(self):
        """获取token"""
        request = AppTokenRequest()
        response = self.client.execute(request)

        if response.is_success():
            token = response.data.get("appAuthToken")
            return token
        else:
            print(
                "请求失败,code:%s, msg:%s, sub_code:%s, sub_msg:%s"
                % (response.code, response.msg, response.sub_code, response.sub_msg)
            )
            raise Exception("获取token失败")

    def get_company_id(self):
        """获取公司id"""

        class CompanyIdRequest(BaseRequest):
            def __init__(self):
                BaseRequest.__init__(self)

            def get_method(self):
                return "/app/builtin/company"

            def get_request_type(self):
                return RequestTypes.GET

        # get company id
        request = CompanyIdRequest()
        response = self.client.execute(request, app_token=self.token)
        if response.is_success():
            company_id = response.data.get("companyId")
            return company_id
        else:
            print("失败, response: ", response)
            raise Exception("获取公司id失败")

    def get_user_list(self) -> list:
        """获取用户列表"""
        user_list = []
        user_count = 0

        class UserIdRequest(BaseRequest):
            def __init__(self):
                BaseRequest.__init__(self)

            def get_method(self):
                return "/superbrowser/rest/v1/erp/staff/list"

            def get_request_type(self):
                return RequestTypes.POST_JSON

        request = UserIdRequest()
        # 按接口文档设置业务参数

        for page in itertools.count(1):
            request.biz_model = {
                "companyId": self.company_id,
                "level": "",
                "isAccurate": "",
                "limit": "100",
                "page": page,
                "departmentIds": [],
                "delflag": "",
                "name ": "",
                "username": "",
            }
            # 发送请求
            response = self.client.execute(request, app_token=self.token)

            if response.is_success():
                user_count = response.data.get("count")
                user_list.extend(response.data.get("data"))
                
                if len(user_list) == user_count:
                    break
            else:
                print("失败, response: ", response)
        
        return user_list

    def get_store_list_by_userid(self, user_id:str):
        """获取指点账号下的全部店铺ID"""
        store_list = []
        store_list_count = 0

        class StoreRequest(BaseRequest):
            def __init__(self):
                BaseRequest.__init__(self)

            def get_method(self):
                return "/superbrowser/rest/v1/erp/store/list/by/user"

            def get_request_type(self):
                return RequestTypes.POST_JSON

        request = StoreRequest()

        for page in itertools.count(1):
            request.biz_model = {
                "companyId": self.company_id,
                "limit": 100,
                "page": page,
                "userId": user_id,
            }

            response = self.client.execute(request, app_token=self.token)

            if response.is_success():
                # print("成功, response: ", response)
                store_list_count = response.data.get("count")
                store_list.extend(response.data.get("data"))
                if store_list_count == len(store_list):
                    break
            else:
                print("失败, response: ", response)
                raise Exception("获取店铺id失败")

        return store_list

    def open_store(self, user_id, store_id, timeout=30, auto_open='true'):
        """打开店铺"""
        start_time = time.time()
        if auto_open == 'true':
            url = f"superbrowser://OpenStrore?storeId={store_id}&openapiToken={self.token}&userId={user_id}&lanuchUrl=aHR0cHM6Ly93d3cuYmFpZHUuY29t&autoopen={auto_open}&debuggPort=60001&notPromptForDownload=0"
        else:
            url = f"superbrowser://OpenStrore?storeId={store_id}&openapiToken={self.token}&userId={user_id}&autoopen={auto_open}&debuggPort=60001&notPromptForDownload=0"
        # if forceDownloadPath != '':
        #     convert_path = base64.b64encode(forceDownloadPath.encode("utf-8"))
        #     convert_path = convert_path.decode('utf-8')
        #     url += f"&forceDownloadPath={convert_path}"
        webbrowser.open(url)

        # # 获取用户 token
        # request = UserLoginRequest()
        # request.biz_model = {"companyId": self.company_id, "userId": user_id}
        # response = self.client.execute(request, app_token=self.token)

        # user_token = response.data.get("data").get("token")

        # url = f"superbrowser://OpenStrore?storeId={store_id}&openapiToken={user_token}&userId={user_id}&lanuchUrl=aHR0cHM6Ly93d3cuYmFpZHUuY29t&autoop en=true&debuggPort=60001&notPromptForDownload=0"
        # # if forceDownloadPath != '':
        # #     convert_path = base64.b64encode(forceDownloadPath.encode("utf-8"))
        # #     convert_path = convert_path.decode('utf-8')
        # #     url += f"&forceDownloadPath={convert_path}"
        # webbrowser.open(url)

        # 等待窗口创建, 影刀插件被激活
        while time.time() - start_time < timeout:
            if self._is_ziniao_browser_created():
                return True
            sleep(1)
        print("打开店铺失败或店铺未启动紫鸟插件")
        return False

    def close_store(self, store_id):
        """关闭店铺"""
        timeout = 20
        start_time = time.time()

        webbrowser.open(f"superbrowser://CloseStrore?storeId={store_id}")

        # 等待窗口关闭
        while time.time() - start_time < timeout:
            if not self._is_ziniao_browser_created():
                return True
            sleep(1)
        print("关闭店铺失败")
        return False

    def exit_ziniao(self):
        """退出紫鸟"""
        webbrowser.open("superbrowser://exit")

    def _get_ziniao_product_name(self):
        """获取紫鸟插件的名称"""
        ziniao_exe_list = ["superbrowser.exe", "ziniaobrowser.exe"]
        ziniao_product_name_list = []

        config_path = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'ShadowBot', 'ChromiumBrowser.config')
        if not os.path.exists(config_path): 
            raise Exception("未安装紫鸟浏览器插件，请根据文档步骤安装紫鸟浏览器插件")

        # 解析XML文件
        tree = ET.parse(config_path)
        root = tree.getroot()

        # 查找匹配的产品名称
        for browser in root.findall('.//ChromiumBrowserInfo'):
            exe_path = browser.find('ExePath').text
            _, exe_name = os.path.split(exe_path)
            if exe_name in ziniao_exe_list:
                ziniao_product_name_list.append(browser.find("ProductName").text)
        
        return ziniao_product_name_list

    def _is_ziniao_browser_created(self):
        """通过判断 ShadowBot.ChromeBridge.exe 父进程判断紫鸟新窗口是否启动"""
        target_name = "ShadowBot.ChromeBridge.exe"
        flags = []
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                if proc.info["name"] == target_name:
                    parent = proc.parent()
                    if parent:
                        grandparent = parent.parent()
                        if grandparent:
                            flag = grandparent.name().lower() in [
                                "superbrowser.exe",
                                "ziniaobrowser.exe",
                            ]
                            flags.append(flag)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return any(flags)

    def create_account(self, nickname, name, password, role_id, auth_device, is_update_person_info, is_limit_login, is_two_step_verify, allow_login_windows, allow_login_mac, allow_login_android, allow_login_web, allow_login_ios, allow_login_miniprog, department_ids, login_limit_start_time=None, login_limit_end_time=None, login_limit_start_date=None, login_limit_end_date=None):
        ''' 员工新增v2
        :param nickname: 用户账号
        :param name: 用户真实姓名
        :param password: 密码
        :param role_id: 角色id (number)
        :param auth_device: 设备授权方式 1:全部设备自动永久授权 2:首设备永久授权 3:每次登入新设备，都需要上级审批 4:首设备授权,后续终端需验证手机号 (number)
        :param is_update_person_info: 是否允许成员修改个人信息 1允许 0不允许 (number)
        :param is_limit_login: 是否限制登录时间0.否；1.是 (number)
        :param is_two_step_verify: 开启二步验证 0:否 1:是 (number)
        :param allow_login_windows: 允许登录windows 1允许 0不允许 (string)
        :param allow_login_mac: 允许登录mac 1允许 0不允许 (string)
        :param allow_login_android: 允许登录android 1允许 0不允许 (string)
        :param allow_login_web: 允许登录web 1允许 0不允许 (string)
        :param allow_login_ios: 允许登录IOS 1允许 0不允许 (string)
        :param allow_login_miniprog: 允许登录小程序 1允许 0不允许 (string)
        :param department_ids: 部门id列表 (list)
        :param login_limit_start_time: 授权用户登入开始时间 HH:mm (string)
        :param login_limit_end_time: 授权用户登入结束时间 HH:mm (string)
        :param login_limit_start_date: 可登录起始时间 yyyy-MM-dd (string)
        :param login_limit_end_date: 可登录结束时间 yyyy-MM-dd (string)
        :return: 员工id
        '''
        
        class CreateAccountRequest(BaseRequest):
            def __init__(self):
                BaseRequest.__init__(self)

            def get_method(self):
                return "/superbrowser/rest/v2/erp/staff/add"

            def get_request_type(self):
                return RequestTypes.POST_JSON
        
        if isinstance(department_ids, list):
            department_ids = department_ids
        elif isinstance(department_ids, str) or isinstance(department_ids, int):
            department_ids = [department_ids]
        else:
            raise Exception("部门id格式错误")

        request = CreateAccountRequest()
        request.biz_model = {
            "companyId": self.company_id,
            "nickname": nickname,
            "name": name,
            "password": password,
            "roleId": role_id,
            "authDevide": auth_device,
            "isUpdatePersonInfo": is_update_person_info,
            "isLimitLogin": is_limit_login,
            "isTwoStepVerify": is_two_step_verify,
            "departmentIds": department_ids,
            "loginLimitStartTime": login_limit_start_time,
            "loginLimitEndTime": login_limit_end_time,
            "loginLimitStartDate": login_limit_start_date,
            "loginLimitEndDate": login_limit_end_date,
            "authClient": {
                "allowLoginWindows": allow_login_windows,
                "allowLoginMac": allow_login_mac,
                "allowLoginAndroid": allow_login_android,
                "allowLoginWeb": allow_login_web,
                "allowLoginIos": allow_login_ios,
                "allowLoginMiniprog": allow_login_miniprog
            }
        }
        response = self.client.execute(request, app_token=self.token)
        if response.is_success():
            return response.data
        else:
            print("失败, response: ", response)
            raise Exception("创建账号失败")

    def delete_account(self, staff_ids, status="2"):
        ''' 员工启用禁用/删除
        :param staff_ids: 员工id (str or list)
        :param status: 状态 0启用 1禁用 2删除
        '''
        staff_id_list = []
        if isinstance(staff_ids, list):
            staff_id_list = staff_ids
        elif isinstance(staff_ids, str):
            staff_id_list.append(staff_ids)
        else:
            raise Exception("员工id格式错误")

        class DeleteAccountRequest(BaseRequest):
            def __init__(self):
                BaseRequest.__init__(self)
            
            def get_method(self):
                return "/superbrowser/rest/v1/erp/staff/status"

            def get_request_type(self):
                return RequestTypes.POST_JSON

        request = DeleteAccountRequest()
        request.biz_model = {
            "companyId": self.company_id,
            "staffIds": staff_id_list,
            "status": status
        }
        response = self.client.execute(request, app_token=self.token)
        if response.is_success():
            return response.data
        else:
            print("失败, response: ", response)
            raise Exception("操作失败")

    def store_auth_add(self, storeIdList, staffId):
        ''' 账号授权新增
        :params storeIdList: 店铺id列表
        :params staffId: 授权用户id
        '''
        store_id_list = []
        if isinstance(storeIdList, list):
            store_id_list = storeIdList
        elif isinstance(storeIdList, str):
            store_id_list.append(storeIdList)
        else:
            raise Exception("店铺id列表格式错误")
        
        class StoreAuthIdRequest(BaseRequest):
            def __init__(self):
                BaseRequest.__init__(self)
            
            def get_method(self):
                return "/superbrowser/rest/v1/erp/store/auth/add"

            def get_request_type(self):
                return RequestTypes.POST_JSON

        request = StoreAuthIdRequest()
        request.biz_model = {
            "companyId": self.company_id,
            "storeIdList": store_id_list,
            "staffId": staffId
        }
        response = self.client.execute(request, app_token=self.token)
        if response.is_success():
            return response.data
        else:
            print("失败, response: ", response)
            raise Exception("账号授权失败")

    def store_auth_delete(self, storeIdList, staffId):
        ''' 账号授权删除
        :params storeIdList: 店铺id列表
        :params staffId: 授权用户id
        '''
        store_id_list = []
        if isinstance(storeIdList, list):
            store_id_list = storeIdList
        elif isinstance(storeIdList, str):
            store_id_list.append(storeIdList)
        else:
            raise Exception("店铺id列表格式错误")
        
        class StoreAuthDeleteRequest(BaseRequest):
            def __init__(self):
                BaseRequest.__init__(self)
            
            def get_method(self):
                return "/superbrowser/rest/v1/erp/store/auth/delete"

            def get_request_type(self):
                return RequestTypes.POST_JSON

        request = StoreAuthDeleteRequest()
        request.biz_model = {
            "companyId": self.company_id,
            "storeIdList": store_id_list,
            "staffId": staffId
        }
        response = self.client.execute(request, app_token=self.token)
        if response.is_success():
            return response.data
        else:
            print("失败, response: ", response)
            raise Exception("账号授权删除失败")

    def query_department_list(self):
        ''' 部门列表
        '''
        class QueryDepartmentList(BaseRequest):
            def __init__(self):
                BaseRequest.__init__(self)
            
            def get_method(self):
                return "/superbrowser/rest/v1/erp/department/list"

            def get_request_type(self):
                return RequestTypes.POST_JSON

        request = QueryDepartmentList()
        request.biz_model = {
            "companyId": self.company_id,
        }
        response = self.client.execute(request, app_token=self.token)
        if response.is_success():
            return response.data
        else:
            print("失败, response: ", response)
            raise Exception("获取部门列表失败")

    def query_role_list(self):
        ''' 用户角色列表
        '''
        class queryDepartmentList(BaseRequest):
            def __init__(self):
                BaseRequest.__init__(self)
            
            def get_method(self):
                return "/superbrowser/rest/v1/erp/per/role/list"

            def get_request_type(self):
                return RequestTypes.POST_JSON

        request = queryDepartmentList()
        request.biz_model = {
            "companyId": self.company_id,
        }
        response = self.client.execute(request, app_token=self.token)
        if response.is_success():
            return response.data
        else:
            print("失败, response: ", response)
            raise Exception("账号授权删除失败")

def test_func():
    appid = '202602241475891241412587520'
    appsecret = '1MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQCuCtQH464BqtGh5Z30i1otZP4metw0XF17I43kMCLi1JMBZROYIO75HG57TCNlFUEM5ZH+7D2An8/cY/pQT+qV21A5S6gBHP3S6ypJhPYlxSuKTDmy2BEhOjoffTryZsAqEcoc4Hln4ypr2KRxnAAwF8QqtEO5Hm/03kUf6KYXKKEtnMzpSXpQb2XVfE2BNj6R4jvOZ7yfulHaAwnvhr9yuCd0593L4Rsui4XTwoE+nJ2wWzNEQU4gqySMVoemlygQBr9ATFVpojZNUF05+f85LM8sDn25aA05eUiqui7V5uaWOs5l98yc7IZ3uKkfjFEpkTkTWRFG8NhrD5FxJEh1AgMBAAECggEAaxoKxRgdWrVN7/0nqPegdNLze6aboDU+6apFhSkCLuh11qPm3PVXWkFe081U8r2TnGYh4+hpKKAwAAYeYhHr4HBn+/pM1vKKWKOTEE8cUr31P1QNJbvFPtdgMUSVY9pLYxgzcnXJAF9RGbDl8Wv4yZ+2fjkUe/T5HI0zqKE4pIK5zKWLArHj8qSvYy2ABZkGS4QcC4JEJc2eJJbFR7+l7OG1flNmJX8WWiKNQFygVLdkXGOdJ8KAUC4AmtuDa62A/Y5imBCG5TWA5+5fH5UhBUECxVqk4m7wK6hfhfqVaZIVLmIsS9/uzL8N1WNKUMjUDedjeEq/hdGdcE9m6ZRWeQKBgQD+9eKzc2Aa/SQ01H0T9PAZZ+cppw0euntH3ofRIVlwNhOS8An2q7MLY0ifqSwmkZUckbZqn1M0Vdmg3LqrXKHjzt4sPWuNtHAmMO2PN4EJ+GuA7rCoYz8CqoF19dfGZfdGcI31MoN7a1DXw6FFt3wuP/357OypkR1u1hr5UgWOVwKBgQCuwHwI1AqQ/6C+ntTg49Ob8zx3jaAC4sjsL2yvyDeOgbhbY928G8RPpLZ3zPXk9PZiYseCGcRLdunVYyG+NM1I9S5pwvAFYhB+9PJEZ+5y6IKXQrPHXWxSgu3zjAfGI9gFMtGij24a2o7BRhrrYo8IbOlGFW+RQh0tN2LRxvgIEwKBgQCuZEuDSUiUTVAlnq5LJz/PcOWJ9QyhVxaaCxlFL5V4jlSHLg7ynXDjOi7jnphnbS7cEsL+XSpRYuNwB2rbaYoGQ2puQji9/Yy0YsUrL+Dgi/4ke590HiZsUWop4FWODBK+KKDA9aM/mSD75ID8KcwT6otzFt6uAWdrd6GNpc/NEwKBgQCTKiiKar+HQq+FOE9AILz5DUszx0IkjAX22S1nj24yBc5SsHRwUNXu2GCN3T6LFTxUuKkZSEfF4Zukh3pIK0FiGpB+oprtfZs0v2Uy9G+bt3EanyK1V1i81+Q6AQge9dqa7iQbCT0JQluMKlTLO9IGn2mICs9M/eeCR61hynTgnwKBgQDbAtmkF6r3rNjFmFWRGfLGR01Gt8KvLzW7LHl2VtxJnbLaoMqk3k17r+nlMCxoTdG3q4n8mi4/LWQEncTGlEy4E4qEfZ6+4RBRA1j2hwLZ/D8aQ08eI5G5kL/rkoWGqk3uwFl+NXXR8eoo0/HrphhHpYd6A5asXXH1FcE+z95HHw=='
    staffId = '17703601878008'
    zn = ZiniaoAPI(appid, appsecret)
    print('token', zn.get_app_token())
    print("company_id", zn.company_id)

    # 获取用户角色列表
    # user_role_list = zn.query_role_list()
    # print(user_role_list)

    # 获取部门列表
    # department_list = zn.query_department_list()
    # print(department_list)
    department = '17022947974301'
    # 创建账号
    # create_result = zn.create_account("测试RPA", "江诚", "sjc030614.", "16808677948111", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", department, login_limit_start_time="09:00", login_limit_end_time="18:00", login_limit_start_date="2026-02-24", login_limit_end_date="2026-02-24")
    # print(create_result)
    account_id = '17719310817969'
    # 删除账号
    delete_result = zn.delete_account(account_id)
    print(delete_result)
    # 账号授权新增
    # print(zn.store_auth_add(['16312460989784'], staffId))
    # # 账号授权删除
    # print(zn.store_auth_delete(['16312460989784'], staffId))

def main(args):
    # appid = "202504091359548590430744576"
    # appsecret = ""
    # zn = ZiniaoAPI(appid, appsecret)

    # print(zn._get_ziniao_product_name())

    # xbot.web.get_active(mode=zn._get_ziniao_product_name()[0], load_timeout=1)
    
    # token = za.token
    # print(token)

    # company_id = za.company_id
    # print(company_id)

    # user_id = za.get_user_list(6)
    # print(user_id)

    # store_info = za.get_store_list_by_userid(16515614909972, 1)
    # print(store_info)
    
    # za.open_store(16515614909972, 16092450125638, 1, r"C:\Users\My\Desktop\test")
    # za.close_store(16092450125638)
    # za.exit_ziniao()


    # 示例用法
    # res = find_grandparent_process_name()
    # print(re)
    test_func()
    pass

