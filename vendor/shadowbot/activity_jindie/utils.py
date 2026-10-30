import json
import uuid
import xbot
from xbot import print
from xbot.selector import Selector
from xbot.web import WebBrowser


def gen_selector(xpath, name: str) -> Selector:
    """生成 xbot Selector。"""
    if isinstance(xpath, str):
        xpath = [xpath]
    uid = str(uuid.uuid4())
    data = {
        'id': uid,
        'name': name,
        'type': 'simple',
        'xpath': {'enable': 'true', 'segments': xpath},
    }
    return Selector(data)


def get_tag_style(xpath: str, web_page: WebBrowser):
    """获取元素基础属性（tag/type/class/data_role）。"""
    js_code = '''
        function () {
            var result = document.evaluate(
                %s,
                document,
                null,
                XPathResult.FIRST_ORDERED_NODE_TYPE,
                null
            );
            var el = result.singleNodeValue;
            if (!el) return null;
            return {
                tag: el.tagName.toLowerCase(),
                type: el.type || null,
                class: el.className || null,
                data_role: el.getAttribute('data-role') || null
            };
        }
    ''' % json.dumps(xpath)
    return web_page.execute_javascript(js_code, execution_world='MAIN')


def set_datetime_data(xpath: str, value: str, web_page: WebBrowser):
    """给日期输入框直接赋值并触发事件。"""
    js_code = '''
        function () {
            var result = document.evaluate(
                %s,
                document,
                null,
                XPathResult.FIRST_ORDERED_NODE_TYPE,
                null
            );
            var el = result.singleNodeValue;
            if (!el) return false;
            el.value = %s;
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
            return true;
        }
    ''' % (json.dumps(xpath), json.dumps(value))
    return web_page.execute_javascript(js_code, execution_world='MAIN')


def set_checkbox_data(xpath: str, checked: bool, web_page: WebBrowser):
    """处理 K3Cloud 表格复选框勾选/取消。"""
    js_code = '''
        function () {
            function byXpath(xp) {
                return document.evaluate(
                    xp,
                    document,
                    null,
                    XPathResult.FIRST_ORDERED_NODE_TYPE,
                    null
                ).singleNodeValue;
            }

            function clickLikeUser(el) {
                if (!el) return;
                ["mouseenter", "mouseover", "mousemove", "mousedown", "mouseup"].forEach(function (t) {
                    el.dispatchEvent(new MouseEvent(t, { view: window, bubbles: true, cancelable: true }));
                });
                if (typeof el.click === "function") el.click();
                else el.dispatchEvent(new MouseEvent("click", { view: window, bubbles: true, cancelable: true }));
            }

            function fireValueEvents(el) {
                if (!el) return;
                el.dispatchEvent(new Event("input", { bubbles: true }));
                el.dispatchEvent(new Event("change", { bubbles: true }));
                el.dispatchEvent(new Event("blur", { bubbles: true }));
            }

            function locateCheckboxParts(node) {
                var input = null;
                var wrapper = null;
                var td = null;

                if (node.matches && node.matches('input[type="checkbox"]')) {
                    input = node;
                    td = input.closest('td');
                    wrapper = input.closest('div[data-role="checkbox"], span.k-checkbox-wrapper, label');
                } else if (node.matches && node.matches('td')) {
                    td = node;
                    input = td.querySelector('input[type="checkbox"]');
                    wrapper = td.querySelector('div[data-role="checkbox"], span.k-checkbox-wrapper, label');
                } else {
                    td = node.closest ? node.closest('td') : null;
                    wrapper = node.closest ? node.closest('div[data-role="checkbox"], span.k-checkbox-wrapper, label') : null;
                    input = node.querySelector ? node.querySelector('input[type="checkbox"]') : null;
                    if (!input && wrapper) input = wrapper.querySelector('input[type="checkbox"]');
                    if (!input && td) input = td.querySelector('input[type="checkbox"]');
                }
                return { input: input, wrapper: wrapper, td: td };
            }

            var node = byXpath(%s);
            if (!node) return { ok: false, msg: 'element not found', xpath: %s };

            var parts = locateCheckboxParts(node);
            var input = parts.input;
            var wrapper = parts.wrapper;
            var td = parts.td;
            if (!input || !td) return { ok: false, msg: 'checkbox input or td not found' };

            var targetChecked = %s;
            var beforeInput = !!input.checked;

            var field = null;
            var gridUpdated = false;
            var modelValue = null;
            var gridEl = td.closest('.k-grid');
            if (gridEl && window.jQuery && window.jQuery.fn && window.jQuery.fn.data) {
                var $ = window.jQuery;
                var grid = $(gridEl).data('kendoGrid');
                var row = td.closest('tr');
                if (grid && row) {
                    var cellIndex = td.cellIndex;
                    var th = grid.thead && grid.thead.find ? grid.thead.find('th').eq(cellIndex) : null;
                    if (th && th.length) field = th.attr('data-field') || null;
                    if (!field) {
                        var fallbackTh = document.querySelector('.k-content.k-state-active th[data-index="' + cellIndex + '"][data-field]');
                        if (!fallbackTh && gridEl) fallbackTh = gridEl.querySelector('th[data-index="' + cellIndex + '"][data-field]');
                        if (fallbackTh) field = fallbackTh.getAttribute('data-field');
                    }
                    var dataItem = grid.dataItem(row);
                    if (dataItem && field) {
                        dataItem.set(field, targetChecked);
                        modelValue = dataItem.get(field);
                        gridUpdated = (typeof modelValue === 'boolean' && modelValue === targetChecked);
                        if (grid.refresh) grid.refresh();
                    }
                }
            }

            if (!gridUpdated && !!input.checked !== targetChecked) {
                var label = wrapper ? wrapper.querySelector('label.k-checkbox-label') : null;
                clickLikeUser(td);
                clickLikeUser(label || wrapper || input);
            }

            if (!!input.checked !== targetChecked) {
                ["keydown", "keypress", "keyup"].forEach(function (t) {
                    input.dispatchEvent(new KeyboardEvent(t, {
                        key: ' ',
                        code: 'Space',
                        keyCode: 32,
                        which: 32,
                        bubbles: true,
                        cancelable: true
                    }));
                });
            }

            if (!!input.checked !== targetChecked) {
                input.checked = targetChecked;
            }

            fireValueEvents(input);
            fireValueEvents(td);

            var afterInput = !!input.checked;
            return {
                ok: afterInput === targetChecked,
                msg: afterInput === targetChecked ? 'finished' : 'failed to reach target state',
                checked: afterInput,
                target: targetChecked,
                changed: beforeInput !== afterInput,
                field: field,
                gridUpdated: gridUpdated,
                modelValue: modelValue
            };
        }
    ''' % (json.dumps(xpath), json.dumps(xpath), json.dumps(checked))

    return web_page.execute_javascript(js_code, execution_world='MAIN')


def get_input_value(xpath: str, web_page: WebBrowser):
    """获取输入类节点值，支持 input/textarea/span。"""
    js_code = '''
        function () {
            var result = document.evaluate(
                %s,
                document,
                null,
                XPathResult.FIRST_ORDERED_NODE_TYPE,
                null
            );
            var el = result.singleNodeValue;
            if (!el) return null;

            var tag = el.tagName.toLowerCase();
            if (tag === 'input' || tag === 'textarea') {
                return el.value || '';
            }
            if (tag === 'span' || tag === 'div') {
                return (el.textContent || '').trim();
            }
            return null;
        }
    ''' % json.dumps(xpath)

    return web_page.execute_javascript(js_code, execution_world='MAIN')


def test_get_input_value():
    if 'xbot_extensions' not in __file__:
        web_page = xbot.web.get_active('chrome')
        xpath = '//div[@class="k-content k-state-active"]//span[.="基本信息"]/../../..//span[.="单据类型"]/../following-sibling::div[1]//*[@class="k-input" or @class="k-textbox"]'
        value = get_input_value(xpath, web_page)
        print('获取到的输入框值为:', value)
        exit()


def main(args):
    test_get_input_value()
