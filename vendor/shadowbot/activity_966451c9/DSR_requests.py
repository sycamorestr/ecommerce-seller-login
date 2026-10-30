# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot_visual
import xbot, requests, execjs, json
from xbot import print, sleep, web, app, excel
from .import package
from .package import variables as glv
from xbot_extensions import activity_excel_v2

class DsrPersonnal:
    def __init__(self, cookies):
        self.cookies = cookies

    def empty_value(value):
        if value == -9999:
            value = '-'
        return value

    def get_cookie(self):
        cookies_dict = {}
        for pair in self.cookies.split(';'):
            key, value = pair.strip().split('=', 1)
            cookies_dict[key] = value
        return cookies_dict

    def get_params(self):
        params = {
            'exp_version': 'v10',
        }
        return params

    def to_percentage(self, value):
        return f"{value * 100:.4f}%"

    def get_response(self):
        _cookies = self.get_cookie()
        params = self.get_params()
        response = requests.get(
            'https://fxg.jinritemai.com/governance/shop/experiencescore/getOverviewV10',
            params=params,
            cookies=_cookies,
            timeout=5
        )
        return response

    def clean_data(self, data: dict):
        cleaned_data = {}
        for key, value in data.items():
            cleaned_value = {}
            for sub_key, sub_value in value.items():
                if sub_value == -9999 or sub_value == '-999900.00%':
                    cleaned_value[sub_key] = '-'
                else:
                    cleaned_value[sub_key] = sub_value
            cleaned_data[key] = cleaned_value
        return cleaned_data

    def analysis_data(self):
        response = self.get_response()
        datum = json.loads(response.text)['data']
        
        # 检查score_type，判断数据结构
        score_type = datum.get('score_type', 1)
        
        if score_type == 2:
            # 成长型店铺，使用grow_score_info
            score_info = datum.get('grow_score_info', {})
            data_dict = {
                '我的体验分': {
                    '分数值': score_info.get('grow_shop_score', '-'),
                    '较前一日': self._calculate_rise(score_info)
                }
            }
            return data_dict
        else:
            # 正式体验分店铺，使用formal_score_info
            formal_score_info = datum.get('formal_score_info', {})
            
            data_names = ['我的体验分', '商品体验分', '物流体验分', '服务体验']
            data_types = ['experience_score', 'goods_score', 'logistics_score', 'service_score']
            
            dp_dict = {}
            for data_name, data_type in zip(data_names, data_types):
                if data_type in formal_score_info:
                    current_data = formal_score_info[data_type]
                    data_dict = {}
                    
                    # 分数值（百分制）
                    data_dict['分数值'] = current_data.get('score', '-')
                    
                    # 较前一日变化
                    rise_value = current_data.get('rise_than_yesterday', '-')
                    if rise_value == -9999:
                        data_dict['较前一日'] = '-'
                    else:
                        data_dict['较前一日'] = rise_value
                    
                    dp_dict[data_name] = data_dict
            
            return self.clean_data(dp_dict)

    def _calculate_rise(self, score_info):
        """计算成长分的较前一日变化"""
        yesterday_info = score_info.get('grow_score_yesterday_info', {})
        today_score = score_info.get('grow_shop_score', 0)
        yesterday_score = yesterday_info.get('grow_score_yesterday', today_score)
        
        if yesterday_score == today_score:
            return 0
        else:
            return today_score - yesterday_score

    def run(self):
        dp_dict = self.analysis_data()
        return dp_dict


class DsrTotal(DsrPersonnal):
    def __init__(self, cookies):
        self.cookies = cookies

    def get_params(self):
        params = {
            'exp_version': 'v10',
        }
        return params

    def get_response(self):
        _cookies = self.get_cookie()
        params = self.get_params()
        response = requests.get(
            'https://fxg.jinritemai.com/governance/shop/experiencescore/getSubScoreMetricsV10',
            params=params,
            cookies=_cookies,
            timeout=8
        )
        return response

    def analysis_data(self):
        response = self.get_response()
        json_data = json.loads(response.text)
        data = json_data['data']
        shop_name = data['shop_name']
        
        # 检查score_type，判断数据结构
        score_type = data.get('score_type', 1)
        
        if score_type == 2:
            # 成长型店铺，使用grow_score_metric_info
            metric_info = data.get('grow_score_metric_info', {})
            metrics = metric_info.get('grow_score_metrics', [])
        else:
            # 正式体验分店铺，使用formal_score_metric_info
            metric_info = data.get('formal_score_metric_info', {})
            metrics = metric_info.get('metrics', [])
        
        dt_dict = {}
        
        for metric in metrics:
            # 跳过没有value的指标
            if 'value' not in metric:
                continue
            
            title = metric['title']
            temp_dict = {}
            
            # 传入分数值
            value_temp = metric['value']['value_figure']
            
            # 根据value_type判断是否需要百分比转换
            # value_type: 2=百分比, 3=时长, 4=评分, 6=时长, 7=数量, 9=数量, 10=数量
            if metric['value']['value_type'] == 2:
                # 百分比类型，转换为百分比格式
                temp_dict['value'] = self.to_percentage(value_temp)
            else:
                # 其他类型保持原值
                temp_dict['value'] = value_temp
            
            # 传入较前一日数据（成长型店铺可能没有这个字段）
            if 'compare_with_self' in metric:
                compare_with_self = metric.get('compare_with_self', 0)
                if compare_with_self == -9999:
                    temp_dict['rise_than_yesterday'] = '-'
                else:
                    # 根据value_type判断compare_with_self的格式
                    if metric['value']['value_type'] == 2:
                        # 百分比类型，compare_with_self是差值，直接显示
                        temp_dict['rise_than_yesterday'] = f"{compare_with_self * 100:.4f}%"
                    else:
                        temp_dict['rise_than_yesterday'] = compare_with_self
            else:
                temp_dict['rise_than_yesterday'] = '-'
            
            # 传入等级（成长型店铺可能没有level字段）
            if 'level' in metric:
                temp_dict['store_perferance'] = metric.get('level', '-')
            else:
                temp_dict['store_perferance'] = '-'
            
            # 传入超越同行比率（成长型店铺可能没有surpass_peers字段）
            if 'surpass_peers' in metric:
                surpass_peers = metric.get('surpass_peers', 0)
                if surpass_peers == -9999:
                    temp_dict['surpass_peers'] = '-'
                else:
                    temp_dict['surpass_peers'] = self.to_percentage(surpass_peers)
            else:
                temp_dict['surpass_peers'] = '-'
            
            # 传入行业优秀值（从value_period最新一天中提取industry_excellent_value）
            if 'value_period' in metric and len(metric['value_period']) > 0:
                latest_period = metric['value_period'][0]  # 最新日期在第一个
                industry_excellent_value = latest_period.get('industry_excellent_value')
                if industry_excellent_value is not None:
                    if metric['value']['value_type'] == 2:
                        temp_dict['industry_excellent_value'] = self.to_percentage(industry_excellent_value)
                    else:
                        temp_dict['industry_excellent_value'] = industry_excellent_value
                else:
                    temp_dict['industry_excellent_value'] = '-'
            else:
                temp_dict['industry_excellent_value'] = '-'
            
            dt_dict[title] = temp_dict
        
        translated_data = self.translate_keys(dt_dict)
        translated_data = self.clean_data(translated_data)
        return translated_data, shop_name

    def translate_keys(self, data):
        translation_dict = {
            'value': '分数值',
            'rise_than_yesterday': '较前一日',
            'surpass_peers': '超越同行比率',
            'store_perferance': '店铺表现',
            'industry_excellent_value': '行业优秀值'
        }
        translated_data = {}
        for key, value in data.items():
            translated_key = {}
            for sub_key, sub_value in value.items():
                if sub_key in translation_dict:
                    translated_key[translation_dict[sub_key]] = sub_value
                else:
                    translated_key[sub_key] = sub_value
            translated_data[key] = translated_key
        return translated_data

    def run(self):
        dt_dict, shop_name = self.analysis_data()
        return dt_dict, shop_name


def _main(cookies):
    dp = DsrPersonnal(cookies)
    dp_dict = dp.run()
    
    dt = DsrTotal(cookies)
    dt_dict, shop_name = dt.run()
    
    data_dict = {**dp_dict, **dt_dict}
    
    # 输出到表格
    app.databook.append_row([shop_name, '分值', '较前一日', '等级', '超越同行比率', '行业优秀值'])
    for index, items in data_dict.items():
        insert_list = [index] + list(items.values())
        app.databook.append_row(insert_list)
    
    return data_dict


def main(args):
    web_page = args.get('web_page')
    cookies = xbot_visual.web.browser.execute_javascript(
        browser=web_page, 
        argument=None, 
        code="function (element, input) {\r\nreturn document.cookie\r\n}"
    )
    data_dict = _main(cookies)
    args['data_dict'] = data_dict
    return data_dict