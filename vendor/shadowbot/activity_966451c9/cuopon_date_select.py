# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, web
from .import package
from .package import variables as glv
from xbot_extensions.web_action.select_date import select_date



def start_select_ymd(web_page, date):
    year, month, day = [item for item in date.split('-')]
    code = f"""
        function (context, args) {{
            var target_year = {year};
            target_year = parseInt(target_year);
            var target_month = {month};
            target_month = parseInt(target_month);
            var targetDate = {day};
            targetDate = parseInt(targetDate);

            const prevelem = document.querySelectorAll(".arco-panel-date")[0];
            const afterelem = document.querySelectorAll(".arco-panel-date")[1];

            function switchYear() {{
                page_year = prevelem.querySelectorAll('.arco-picker-header-label')[0].textContent.trim();
                page_year = parseInt(page_year.replace(/[^0-9]/g, "")); 
                if (page_year === target_year) {{
                    console.log("已到达目标年份：", target_year);
                    switchMonth(); // 切换到月份逻辑
                    return;
                }}

                if (page_year > target_year) {{
                    const prevYearButton = prevelem.querySelectorAll('.arco-picker-header-icon')[0];
                    prevYearButton.style.border = "2px solid blue"
                    prevYearButton.click();
                    console.log("点击上一年按钮，当前年份：", page_year);
                }} else if (page_year < target_year) {{
                    const nextYearButton = afterelem.querySelectorAll('.arco-picker-header-icon')[3];
                    nextYearButton.style.border = "2px solid blue"
                    nextYearButton.click();
                    console.log("点击下一年按钮，当前年份：", page_year);
                }}
                setTimeout(switchYear, 100);
            }}

            function switchMonth() {{
                page_month = prevelem.querySelectorAll('.arco-picker-header-label')[1].textContent.trim();
                page_month = parseInt(page_month.replace(/[^0-9]/g, "")); 

                if (page_month === target_month) {{
                    console.log("已到达目标月份：", page_month);
                    clickTargetDate(); // 切换到日期点击逻辑
                    return;
                }}

                if (page_month > target_month) {{
                    const prevMonthButton = prevelem.querySelectorAll('.arco-picker-header-icon')[1];
                    prevMonthButton.style.border = "2px solid green";
                    prevMonthButton.click();
                    console.log("点击上一月按钮，当前月份：", page_month);
                }} else if (page_month < target_month) {{
                    const nextMonthButton = afterelem.querySelectorAll('.arco-picker-header-icon')[2];
                    nextMonthButton.style.border = "2px solid green";
                    nextMonthButton.click();
                    console.log("点击下一月按钮，当前月份：", page_month);
                }}
                setTimeout(switchMonth, 100);
            }}

            function clickTargetDate() {{
                const xpath = '(//*[@class="arco-panel-date"])[1]//*[contains(@class, "arco-picker-cell ") and not(contains(@class, "arco-picker-cell-disabled"))]';
                const enabledCells = document.evaluate(
                xpath,
                prevelem,
                null,
                XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,
                null
                );

                const results = [];
                for (let i = 0; i < enabledCells.snapshotLength; i++) {{
                results.push(enabledCells.snapshotItem(i));
                }};
                for (const elem of results) {{
                if (elem.textContent.trim() == targetDate) {{
                    elem.click();
                    console.log("已点击目标日期：", targetDate);
                    break; // 
                }}
                }}
            }}

            switchYear(); // 启动切换年份逻辑
        }}
    """
    web_page.execute_javascript(code, '', )
    
def end_select_ymd(web_page, date):
    year, month, day = [item for item in date.split('-')]
    code = f"""
        function (context, args) {{
            var target_year = {year};
            target_year = parseInt(target_year);
            var target_month = {month};
            target_month = parseInt(target_month);
            var targetDate = {day};
            targetDate = parseInt(targetDate);

            const prevelem = document.querySelectorAll(".arco-panel-date")[0];
            const afterelem = document.querySelectorAll(".arco-panel-date")[1];

            function switchYear() {{
                page_year = afterelem.querySelectorAll('.arco-picker-header-label')[0].textContent.trim();
                page_year = parseInt(page_year.replace(/[^0-9]/g, "")); 
                
                if (page_year === target_year) {{
                    console.log("已到达目标年份：", target_year);
                    switchMonth(); // 切换到月份逻辑
                    return;
                }}

                if (page_year > target_year) {{
                    const prevYearButton = prevelem.querySelectorAll('.arco-picker-header-icon')[0];
                    prevYearButton.click();
                    console.log("点击上一年按钮，当前年份：", page_year);
                }} else if (page_year < target_year) {{
                    const nextYearButton = afterelem.querySelectorAll('.arco-picker-header-icon')[3];
                    nextYearButton.click();
                    console.log("点击下一年按钮，当前年份：", page_year);
                }}
                setTimeout(switchYear, 100);
            }}

            function switchMonth() {{
                page_month = afterelem.querySelectorAll('.arco-picker-header-label')[1].textContent.trim();
                page_month = parseInt(page_month.replace(/[^0-9]/g, "")); 

                if (page_month === target_month) {{
                    console.log("已到达目标月份：", page_month);
                    clickTargetDate(); // 切换到日期点击逻辑
                    return;
                }}

                if (page_month > target_month) {{
                    const prevMonthButton = prevelem.querySelectorAll('.arco-picker-header-icon')[1];
                    prevMonthButton.click();
                    console.log("点击上一月按钮，当前月份：", page_month);
                }} else if (page_month < target_month) {{
                    const nextMonthButton = afterelem.querySelectorAll('.arco-picker-header-icon')[2];
                    nextMonthButton.click();
                    console.log("点击下一月按钮，当前月份：", page_month);
                }}
                setTimeout(switchMonth, 100);
            }}

            function clickTargetDate() {{
                const xpath = '(//*[@class="arco-panel-date"])[2]//*[contains(@class, "arco-picker-cell ") and not(contains(@class, "arco-picker-cell-disabled"))]';
                const enabledCells = document.evaluate(
                xpath,
                prevelem,
                null,
                XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,
                null
                );

                const results = [];
                for (let i = 0; i < enabledCells.snapshotLength; i++) {{
                results.push(enabledCells.snapshotItem(i));
                }};
                for (const elem of results) {{
                if (elem.textContent.trim() == targetDate) {{
                    elem.click();
                    console.log("已点击目标日期：", targetDate);
                    break; // 
                }}
                }}
            }}

            switchYear(); // 启动切换年份逻辑
        }}
    """
    web_page.execute_javascript(code, '', )

def handle_hms(web_page, hms, index):

    h, m, s = [item for item in hms.split(':')]
    code = f"""
        function (context, args) {{
            var prevelem = document.querySelectorAll(".arco-timepicker")[{index}];
            var ulElems = prevelem.querySelectorAll("ul");
            function select_hms(h, m, s) {{
                for (let index = 0; index < ulElems.length; index++) {{
                    let ul = ulElems[index];
                    let lis = ul.querySelectorAll("li");
                    for (let i = 0; i < lis.length; i++) {{
                        let li = lis[i];
                        if (index === 0) {{  // 小时
                            if (li.textContent.trim() === h) {{
                                setTimeout(() => {{
                                    li.click();
                                }}, index * 500);
                                break;
                            }}
                        }} else if (index === 1) {{  // 分钟
                            if (li.textContent.trim() === m) {{
                                setTimeout(() => {{
                                    li.click();
                                    console.log("已选择分钟：", m);
                                }}, index * 500);
                                break;
                            }}
                        }} else if (index === 2) {{  // 秒
                            if (li.textContent.trim() === s) {{
                                setTimeout(() => {{
                                    li.click();
                                    console.log("已选择秒：", s);
                                }}, index * 500);
                                break;
                            }}
                        }}
                    }}
                }}
            }}
            // 示例调用
            select_hms('{h}', '{m}', '{s}');
        }}
    """
    web_page.execute_javascript(code, '')


def excute(web_page, start_time, end_time):
    code = """
    function (context, args) {
        const spans = document.querySelectorAll("span");
        const targetSpan = Array.from(spans).find((span) => {
            if(span && span.textContent.trim() === "选择时间"){
                span.click()
            };
        });
    }
    """
    code_two = """
    function (context, args) {
        const spans = document.querySelectorAll("span");
        const targetSpan = Array.from(spans).find((span) => {
            if(span && span.textContent.trim() === "确定"){
                span.click()
            };
        });
    }
    """
    date_split_list = start_time.split(' ')
    start_ymd = date_split_list[0]
    start_hms = date_split_list[1]
    start_select_ymd(web_page, start_ymd)
    sleep(4)
    date_split_list = end_time.split(' ')
    end_ymd = date_split_list[0]
    end_hms = date_split_list[1]
    start_select_ymd(web_page, end_ymd)
    sleep(2)
    web_page.execute_javascript(code, '')
    handle_hms(web_page, start_hms, 0)
    handle_hms(web_page, end_hms, 1)
    sleep(2)
    web_page.execute_javascript(code_two, '')
    

def main(args):

    web_page = args.get("web_page")
    date_iframe = args.get("date_iframe")
    start_time = args.get("start_time", "2025-07-31 01:01:01")
    end_time = args.get("end_time", "2025-08-31 17:23:00")
    # web_page = web.get_active(mode='chrome')

    excute(web_page, start_time, end_time)
    sleep(3)