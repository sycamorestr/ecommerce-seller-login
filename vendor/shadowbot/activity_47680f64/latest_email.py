# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv

import imaplib, email
from bs4 import BeautifulSoup

class MatchEmailCode:
    def __init__(self, email, password, select="INBOX"):
        """
        获取最新的邮件内容
        :param email: 邮箱地址
        :param password: 邮箱授权码
        :param select: 目标文件夹【收件，未读, 发件，垃圾箱】-> [INBOX, UNSEEN, Sent, Trash ]
        """
        # 添加缺失的命令
        imaplib.Commands['ID'] = ('AUTH')

        # 上传客户端身份信息
        args = ("name", "RPA", "contact", "", "version", "1.0.0", "vendor", "RPA")

        # 连接到 邮箱的 IMAP 服务器
        ssl = self.match_ssl(email)
        self.mail = imaplib.IMAP4_SSL(ssl)

        # 登录邮箱账号
        self.mail.login(email, password)

        # 163邮箱补充身份，否则会被拒绝
        typ, dat = self.mail._simple_command('ID', '("' + '" "'.join(args) + '")')
        self.mail._untagged_response(typ, dat, 'ID')

        # 选择收件箱邮箱
        self.mail.select(select)

    def match_ssl(self, email: str):
        map_dict = {
            "qq.com": "imap.qq.com",
            "163.com": "imap.163.com",
            "gmail.com": "imap.gmail.com"
        }
        for m, ssl in map_dict.items():
            if email.__contains__(m):
                return ssl

    def match_some_latest_email(self, email_count):
        """
        获取最新的几封邮件
        :param email_count: 需要获取的邮件数量
        :return:
        """
        result, data = self.mail.search(None, 'ALL')
        latest_email_id_list = data[0].split()[-email_count: ]

        message_list = []

        for email_id in latest_email_id_list:
            email_message = self._fetch_email_message(email_id)
            text = self.parser_body(email_message) or self.parser_html(email_message)
            time = self.parser_send_time(email_message)
            message_list.append({
                "text": text,
                "send_time": time
            })

        return message_list

    def _fetch_email_message(self, email_id):
        # 使用 fetch 命令获取邮件内容
        result, data = self.mail.fetch(email_id, '(RFC822)')

        # 解析邮件内容
        raw_email = data[0][1]

        if isinstance(raw_email, str):
            print(raw_email)

        return email.message_from_bytes(raw_email)

    def match_latest_email(self):
        """
        获取最新的一封邮件
        :return:
        """
        result, data = self.mail.search(None, 'ALL')
        latest_email_id = data[0].split()[-1]

        email_message = self._fetch_email_message(latest_email_id)

        text = self.parser_body(email_message) or self.parser_html(email_message)
        time = self.parser_send_time(email_message)
        return {
            "text": text,
            "send_time" : time
        }

    def parser_body(self, email_message):
        """
        解析邮件正文
        :param email_message: 邮件信息对象
        :return:
        """
        print("parser body!")

        body = b""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == 'text/plain':
                    body = part.get_payload(decode=True)
        else:
            body = email_message.get_payload(decode=True)

        if body is not None:
            body = body.decode('utf-8')

        if "<!DOCTYPE html>" in body:
            # 转发过来的邮件是整个html页面
            soup = BeautifulSoup(body, 'html.parser')
            # 获取 HTML 中的文本内容
            return soup.get_text().replace("\n", "").replace("\r", "")
        return body

    def parser_html(self, email_message):
        # 获取邮件 HTML 内容
        print("parser html!")

        html = None
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == 'text/html':
                    html = part.get_payload(decode=True)
        else:
            html = email_message.get_payload(decode=True)

        if html is not None:
            # 解析 HTML 内容
            soup = BeautifulSoup(html, 'html.parser')
            # 获取 HTML 中的文本内容
            return soup.get_text().replace("\n", "").replace("\r", "")

    def parser_send_time(self, email_message):
        # 获取邮件发送时间
        timestamp = email.utils.parsedate_to_datetime(email_message['Date'])
        # 将时间格式化为字符串
        return timestamp.strftime('%Y-%m-%d %H:%M:%S')

    def close(self):
        # 关闭邮箱连接
        self.mail.close()
        self.mail.logout()


def get_latest_email_for_163(email, password, select):
    M = MatchEmailCode(email, password, select)
    t = M.match_latest_email()
    M.close()
    return t


def main(args):
    email_ = args["email"]
    password = args["password"]
    select = args["select_from"]

    args["latest_email"] = get_latest_email_for_163(email_, password, select)

    print("获取到的邮件: ", args["latest_email"])
