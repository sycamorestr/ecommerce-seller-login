# 金蝶云星空 RPA 扩展指令需求文档

## 1. 文档目的
本文档用于定义 `xbot_extensions.activity_jindie` 项目的功能需求、接口规范与验收标准，指导后续开发、测试与发布。

## 2. 项目目标
在金蝶云星空网页端提供一组可复用 RPA 指令，覆盖以下高频业务动作：
- 登录系统
- 标签页管理
- 分组展开/收起
- 单字段填写与批量填写
- 表格单元格填写
- 字段值读取

## 3. 适用范围
- 适用平台：金蝶云星空 Web 页面
- 运行环境：XBot 扩展活动（Code Flow）
- 主要输入对象：`web_page: xbot._web.browser.WebBrowser`

## 4. 指令清单与接口需求

| 指令名 | 功能说明 | 输入参数 | 输出参数 |
|---|---|---|---|
| `login` | 登录金蝶云星空 | `web_page, account, password, platform, login_now` | `out_web_page` |
| `get_all_tab` | 获取当前打开标签页列表 | `web_page` | `out_all_tab_list` |
| `close_tab` | 关闭指定标签页（支持单个/多个） | `web_page, tab_name` | 无 |
| `get_group_list` | 获取页面可见分组列表 | `web_page` | `out_group_list` |
| `show_group` | 展开指定分组或全部分组 | `web_page, group_name, show_all` | 无 |
| `hide_group` | 收起指定分组或全部分组 | `web_page, group_name, hide_all` | 无 |
| `input_data` | 按分组+字段名填写单字段 | `web_page, group_name, key, value` | 无 |
| `batch_input_data` | 按列表批量填写字段 | `web_page, data_list` | 无 |
| `input_table` | 按表格序号、列名、行号填写单元格 | `web_page, sheet_index, col_name, row_num, data` | 无 |
| `get_field_data` | 按分组+字段名读取字段值 | `web_page, group_name, key` | `out_field_value` |

## 5. 详细功能需求

### FR-01 登录
- 支持账号密码登录。
- 支持平台选择。
- 支持验证码识别（存在验证码时触发）。
- 支持“是否顶号登录”选择。
- 登录成功后返回可继续操作的 `web_page`。

### FR-02 标签页管理
- 能读取当前所有标签页标题。
- 能按标签页标题关闭目标页。
- 关闭多个标签页时按顺序执行。

### FR-03 分组控制
- 支持按分组名展开/收起。
- 支持 `show_all/hide_all` 一键处理全部可见分组。
- 对不存在分组应安全跳过或给出可读异常。

### FR-04 字段填写
- 支持文本框填写。
- 支持下拉字段选择。
- 支持日期字段填写（格式 `YYYY/MM/DD`）。
- 输入完成后触发必要提交动作（如 Enter 或 change 事件）。

### FR-05 批量填写
- 输入结构为列表，每项至少包含：`group_name, key, value`。
- 对缺少关键键值的项进行跳过并记录日志。
- 其余项复用单字段填写逻辑。

### FR-06 表格填写
- 支持按表头名定位列。
- 支持填写文本、日期、复选框单元格。
- 复选框支持布尔语义映射：`是/否/true/false/1/0`。
- 对复选框优先按 `data-field` 定位，避免冻结列/虚拟表导致错位。

### FR-07 字段读取
- 支持读取文本、日期、下拉显示值、复选框布尔值。
- 优先从字段容器内读取可见有效值。
- 找不到目标时返回清晰异常。

## 6. 通用约束与异常要求
- 所有指令必须可在 `main(args)` 中直接调用。
- 与流程编排兼容：保持参数 `name` 稳定，不随文案变更。
- 异常信息必须包含业务上下文（分组名、字段名、定位表达式）。
- 不允许静默失败。

## 7. 数据结构约定

### 7.1 `data_list`（批量填写）
```json
[
  { "group_name": "基本信息", "key": "供应商", "value": "E00001" },
  { "group_name": "交货安排", "key": "最早交货日期", "value": "2026/01/01" }
]
