# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
import arrow
import xbot_visual
from xbot_visual.web import get_cookies, set_cookie, remove_cookie
from xbot import print, sleep
from .import package
from .package import variables as glv
import datetime

import json
import re
import os
from dateutil import parser



print = [lambda *_, **__: None, print][__package__ == "xbot_robot" or hasattr(xbot, "__log")]




def extract_domain_from_url(url):
    pattern = r"(?:://)(?:www\.)?([a-zA-Z0-9-\.]+)(?=/)"
    match = re.search(pattern, url)
    if match:
        domain = match.group(1)
        return domain
    else:
        return None

  

def save_login_info(web_page, save_path, partition_key=None):

    login_info = {}

    url = web_page.get_url()
    cookies = get_cookies(url_type="auto", browser=web_page, web_type=None, url=None, name=None, domain=None, path=None, filter_secure=False, secure=False, filter_session=False, session=False)
    if partition_key:
        try:
            _cookies = get_cookies(url_type="auto", browser=web_page, web_type=None, url=None, name=None, domain=None, path=None, filter_secure=False, secure=False, filter_session=False, session=False, partition_key=partition_key)
            cookies.extend(_cookies)
        except TypeError as e:
            pass
 
    for cookie in cookies:
        cookie['expires'] = None
        if cookie['expirationDate']:
            date_string = cookie['expirationDate']
            dt = parser.parse(date_string)
            # dt = datetime.datetime.strptime(dt, "%Y/%m/%d %H:%M:%S")       
            cookie['expires'] = int(datetime.datetime.timestamp(dt))
        cookie['sessionCookie'] = not bool(cookie['expires'])
        cookie.pop('expirationDate')

    local_storage = web_page.execute_javascript('''
        function (ele, input) {
            let local_storage = {}
            for (let i = 0; i < localStorage.length; i++) {
                let key = localStorage.key(i);
                let value = localStorage.getItem(key);
                local_storage[key] = value
            }
            if (Object.keys(local_storage).length == 0) {
                return null
            }
            return local_storage
        }    
    ''')
    local_storage = local_storage if local_storage else {}
    login_info = {
        "url": url,
        "cookies": cookies,
        "local_storage": local_storage
    }
    # print(login_info)
    login_info = json.dumps(login_info, ensure_ascii=False, indent=4)
    if bool(save_path):
        with open(save_path, 'w', encoding="u8") as f:
            f.write(login_info)
    
    return login_info




def login(web_page, cookie_file_path, *, add_local_storage=False):
    

    with open(cookie_file_path, 'r', encoding="u8") as f:
        login_info = json.load(f)

        
    url = login_info.get("url", "")
    cookies = login_info.get('cookies', [])
    local_storage = login_info.get('local_storage', {})

    domain = web_page.execute_javascript('''() => {return window.origin;}''')
    if domain not in url:
        web_page.navigate(url)    
    
    logout(web_page)
    for cookie in cookies:        
        if cookie['name'] == "":
            continue
        try:
            set_cookie(url_type="auto", browser=web_page, web_type=None, url=None, **cookie)
        except Exception as e:
            print(e)

    if add_local_storage:
        print("添加本地存储")
        for k, v in local_storage.items():
            try:
                if isinstance(v, str):
                    v = f'`{v}`'
                web_page.execute_javascript('''
                function (ele, input) {
                    localStorage.removeItem(`%s`);
                    localStorage.setItem(`%s`, %s);
                }
                ''' % (k, k, v))                
            except Exception as e:
                print('add_local_storage', e)
    
    try:
        web_page.navigate(url, load_timeout=20)
    except:
        pass


def logout(web_page, del_local_storage=False):
    """
    通过删除Cookie和本地存储实现退出登录操作
    :param web_page: 网页对象
    :param del_local_storage: 是否删除本地存储 
    :return: 
    """
    cookies = get_cookies(url_type="auto", browser=web_page, web_type=None, url=None, name=None, domain=None, path=None, filter_secure=False, secure=False, filter_session=False, session=False)
    for cookie in cookies:
        if cookie['name'] == "":
            continue
        remove_cookie(url_type="auto", browser=web_page, web_type="cef", url=None, remove_type="appoint_cookie", name=cookie['name'])


    if del_local_storage:
        web_page.execute_javascript('''
            function (ele, input) {
                localStorage.clear();
            }    
        ''')

  



def main(args):
    
    pass
