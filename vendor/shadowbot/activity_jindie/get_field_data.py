import json
import xbot
from xbot import print
from .import package
from .package import variables as glv
from xbot.web import WebBrowser
from .utils import gen_selector


def get_field_value_from_container(container_xpath: str, web_page: WebBrowser):
    '''从字段容器中提取值，支持 checkbox/input/textarea/span。'''
    js_code = '''
        function () {
            function isVisible(el) {
                if (!el) return false;
                var style = window.getComputedStyle(el);
                if (!style) return true;
                if (style.display === 'none' || style.visibility === 'hidden') return false;
                if (el.offsetParent === null && style.position !== 'fixed') return false;
                return true;
            }

            function firstNonEmpty(list) {
                for (var i = 0; i < list.length; i++) {
                    var v = list[i];
                    if (v !== null && v !== undefined && String(v).trim() !== '') return String(v).trim();
                }
                return '';
            }

            var result = document.evaluate(
                %s,
                document,
                null,
                XPathResult.FIRST_ORDERED_NODE_TYPE,
                null
            );
            var container = result.singleNodeValue;
            if (!container) return { ok: false, msg: 'container not found' };

            var checkbox = container.querySelector('input[type="checkbox"]');
            if (checkbox) return { ok: true, type: 'checkbox', value: !!checkbox.checked };

            var inputs = Array.from(container.querySelectorAll('input:not([type="hidden"]), textarea')).filter(isVisible);
            var inputVals = inputs.map(function (el) { return el.value; });
            var inputVal = firstNonEmpty(inputVals);
            if (inputVal !== '') return { ok: true, type: 'input', value: inputVal };

            var texts = Array.from(container.querySelectorAll('span.k-input, span.k-textbox, span, div.k-input'))
                .filter(isVisible)
                .map(function (el) { return (el.textContent || '').trim(); })
                .filter(function (t) { return t !== ''; });
            if (texts.length) return { ok: true, type: 'text', value: texts[0] };

            return { ok: false, msg: 'value not found' };
        }
    ''' % json.dumps(container_xpath)
    return web_page.execute_javascript(js_code, execution_world='MAIN')


def get_field_data(web_page: WebBrowser, group_name: str, key: str):
    '''获取指定分组字段值（返回 str 或 bool）。'''
    container_xpath = (
        f'//div[@class="k-content k-state-active"]//span[.="{group_name}"]/../../..'
        f'//span[.="{key}"]/../following-sibling::div[1]'
    )
    container_selector = gen_selector(container_xpath, f'{group_name}-{key}-字段容器')
    if not web_page.is_element_displayed(container_selector):
        raise Exception(f'未找到字段容器：{group_name}-{key}，定位：{container_xpath}')

    value_result = get_field_value_from_container(container_xpath, web_page)
    if not value_result or not value_result.get('ok'):
        raise Exception(f'字段取值失败：{group_name}-{key}，结果：{value_result}')

    return value_result.get('value')


def test_func():
    if 'xbot_extensions' not in __file__:
        web_page = xbot.web.get_active('chrome')
        value = get_field_data(web_page, '交货安排', '最早交货日期')
        print('字段值:', value)
        exit()


def main(args):
    test_func()
    web_page = args.get('web_page')
    group_name = args.get('group_name')
    key = args.get('key')
    args['out_field_value'] = get_field_data(web_page, group_name, key)
