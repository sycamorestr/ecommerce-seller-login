# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
import xbot_visual
from xbot import print, sleep
from . import package
from .package import variables as glv
from .tax_invoice_api import TaxInvoiceAPI
import os, requests
 
def main(args):
    # 获取参数
    app_id: str = args.get('app_id')
    secret: str = args.get('secret') 
    tax_account: str = args.get('tax_account')
    tax_password: str = args.get('tax_password')
    nsrsbh: str = args.get('nsrrbh')
    qr_code_type: str = args.get('qr_code_type')
    is_qr_code: bool = args.get('is_qr_code', False)
    global api

    # 初始化api
    api = init_api(app_id, secret)

    # 登录
    login_status = api.tax_login(nsrsbh=nsrsbh, username=tax_account, password=tax_password)
    # print(login_status)

    # 判断登录状态
    if not login_status.get('status'):
        raise Exception(login_status.get('msg'))
    elif '验证码' in login_status.get('msg'):
        input_sms_code()

    print(f'{nsrsbh} 登录成功！')
    # 二维码验证
    if is_qr_code:
        check_qr_code_status(qr_code_type)
        print(f'{nsrsbh} 扫脸认证已完成 有效期24小时！')

    args['invoice_instance'] = api


def init_api(app_id: str, secret: str) -> TaxInvoiceAPI:
    # 初始化对象
    api = TaxInvoiceAPI()
    if not api.set_token(app_id, secret):
        raise Exception('初始化失败，请检查')
    return api


def input_sms_code():
    while True:
        # 弹出输入框，获取短信验证码
        sms_input = xbot_visual.dialog.show_input_dialog(title="请输入短信验证码", label="短信验证码", type="input",
                                                         value=None, storage_key="f23d107d-5507-4581-9854-562486348e49")
        if sms_input.pressed_button == '取消':
            raise Exception('验证码输入被人工中断')
        # 使用短信验证码登录
        login_status = api.tax_login(sms_code=sms_input.value)
        if login_status.get('status'): return


def check_qr_code_status(code_type: str) -> None:
    # 下载二维码
    pic_pid, qr_code_path = download_qr_code(code_type)
    _c = 0

    while _c < 60:
        sleep(5)
        # 查询二维码状态
        query_result = api.query_secondary_auth_status()
        if query_result.get('msg') == '扫码':
            # 关闭二维码图片
            xbot_visual.system.terminal_process(terminal_way="id", process_id=pic_pid, process_name=None)
            # 删除二维码图片
            xbot_visual.file.remove(paths=qr_code_path)
            return
        elif query_result.get('msg') == '扫码超时':
            # 关闭二维码图片
            xbot_visual.system.terminal_process(terminal_way="id", process_id=pic_pid, process_name=None)
            # 重新下载二维码
            pic_pid, qr_code_path = download_qr_code()
        _c += 1
    raise Exception('扫码超时')


def download_qr_code(code_type) -> (str, str):
    # 二维码路径
    code_path = os.path.join(os.path.dirname(__file__), 'qr_code.png')
    # 获取验证码
    qr_code_get_status = api.get_qr_code(code_type=code_type)
    if not qr_code_get_status.get('status'):
        raise Exception('二维码请求失败')
    for _retry_time in range(3):
        try:
            # 下载二维码图片
            response = requests.get(qr_code_get_status.get('msg'))
            response.raise_for_status()
            with open(code_path, 'wb') as f:
                f.write(response.content)
            # 打开二维码图片
            process_info = xbot_visual.system.run_or_open(application_path=code_path, command_line_arguments=None,
                                                          working_folder=None,
                                                          after_application_launch="wait_to_mainwindow",
                                                          is_waitexit_not_more_than=False, timeout_for_exit="10",
                                                          is_waithwnd_not_more_than=True, timeout_for_hwnd="10",
                                                          start_as_admin=False, window_style="maximized")
            return process_info.pid, code_path

        except Exception as err:
            if _retry_time == 3:
                raise Exception('下载二维码失败：{}'.format(str(err)))
            sleep(2)
            continue