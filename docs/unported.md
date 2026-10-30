# 未做成网页登录的块

## 没有登录地址

| 块 | 原因 |
| --- | --- |
| 滑块拖动 `process11`、`process3` | 调用方传入元素，没有登录页 |
| `activity_966451c9/process37.py` | 售后时间选择测试，不是「店铺切换(ID)(新）」 |
| `activity_7bca6d` 里的中国银行 | 该扩展没有中国银行登录流。网银登录在 `banks/boc/` |

隐藏子流程（`process22` 等）不是独立登录指令。其中已被登录模块调用的 `process48` / `process49` / `process2` / `process17` / `process36` 已经接到对应模块。
