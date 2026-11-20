# 规则与证据索引

## 功能模块

| 模块 | 动作与核心规则 | 入口 | 核心文件 | 测试 |
|---|---|---|---|---|
| M1 返件登记 | 按票号采信返件和复入库，归并重复上报 | `/api/intake` | `app/modules/intake/service.py` | `tests/test_intake.py` |
| M2 部件字典 | 对照独立档案与别名，保留前导零、分离歧义 | `/api/catalog` | `app/modules/catalog/service.py` | `tests/test_catalog.py` |
| M3 拆装序列 | 归一时间后排序，拒绝旧序号和同号冲突 | `/api/sequence` | `app/modules/sequence/service.py` | `tests/test_sequence.py` |
| M4 谱系校验 | 回放拆装与返件操作，校验瞬时图并保留历史边 | `/api/graph` | `app/modules/graph/service.py` `app/modules/graph/edges.py` | `tests/test_graph.py` |
| M5 召回反查 | 按批号从子件沿时间交集向上回查 | `/api/recall` | `app/modules/recall/service.py` `app/modules/recall/windows.py` | `tests/test_recall.py` |
| M6 数量核对 | 唯一件分配至四类并计算差额 | `/api/balance` | `app/modules/balance/service.py` | `tests/test_balance.py` |
| M7 追溯凭证 | 查单件证据、按内容归档并下载 | `/api/evidence/{serial}`、`/api/runs` | `app/modules/evidence/service.py` `app/modules/evidence/store.py` `app/modules/evidence/serial.py` | `tests/test_evidence.py` |

## 陷阱清单

| TRAP | 触发样例 | 朴素实现的问题 | 处理 | 位置 | 测试 |
|---|---|---|---|---|---|
| TRAP-06 | 脏样例全角 TC-07 | 同一别名分成两条 | 统一全半角与大小写 | `app/identity.py:4` | `tests/test_catalog.py::test_fullwidth_alias_normalizes` |
| TRAP-07 | 脏样例第 18 条档案 | 缺失哨兵进入库存 | 拒绝哨兵编码并记录行 | `app/identity.py:4` | `tests/test_catalog.py::test_placeholder_does_not_create_part` |
| TRAP-08 | 两套样例 0007 | 前导零丢失或误合并 | 编码保留为字符串 | `app/identity.py:4` | `tests/test_catalog.py::test_leading_zero_is_identity` |
| TRAP-11 | 对干净样例第 1 条换用 UTC 重传 | 同一时刻重复装入 | 先归一 UTC 再生成比较键 | `app/timebox.py:4` | `tests/test_sequence.py::test_equivalent_timezone_duplicate` |
| TRAP-13 | 干净样例票据倒序 | 晚到记录被丢弃 | 按生效时间排序并保留原行 | `app/modules/intake/service.py:31` | `tests/test_intake.py::test_return_order_preserves_line_numbers` |
| TRAP-14 | 干净样例票号 RT-060 增加异件申报 | 旧票被覆盖 | 保留首条和争议双方 | `app/modules/intake/service.py:23` | `tests/test_intake.py::test_conflicting_ticket_retains_first` |
| TRAP-19 | 脏样例 0009 仍在装且冲突 | 同时记在装与争议 | 以争议优先，另保留实物父件 | `app/modules/balance/service.py:25` | `tests/test_balance.py::test_dispute_outranks_actual_mount` |
| TRAP-20 | 脏样例事件第 18 条 | 同时段的互相装配形成递归环 | 沿当前父链验证并记录环路径 | `app/modules/graph/edges.py:12` | `tests/test_graph.py::test_cycle_returns_exact_path` |
| TRAP-21 | 干净样例错填拆出父件 | 子件从任意父件被拆掉 | 逐边核查匹配关系 | `app/modules/graph/edges.py:26` | `tests/test_graph.py::test_wrong_parent_detach_keeps_active_edge` |
| TRAP-22 | 脏样例「共码」 | 别名随输入顺序漂移 | 收集所有声明，隔离歧义 | `app/modules/catalog/service.py:33` | `tests/test_catalog.py::test_ambiguous_alias_is_order_independent` |
| TRAP-23 | 两套样例 0008、UNIT-C | 子件拆出后仍把父链计入 | 对每层父边取半开交集 | `app/modules/recall/windows.py:5` | `tests/test_recall.py::test_intersection_does_not_invent_exposure` |
| TRAP-25 | 脏样例事件第 19 条 | 同件重叠装在两处 | 维持已生效的父件并隔离重叠 | `app/modules/graph/edges.py:12` | `tests/test_graph.py::test_double_mount_keeps_original_parent` |
| TRAP-26 | 脏样例事件第 17 条 | 陈旧动作覆盖已生效状态 | 逐子件维护递增序号 | `app/modules/sequence/service.py:29` | `tests/test_sequence.py::test_stale_revision_is_quarantined` |
