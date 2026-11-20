# 退换件谱系台

售后工程师可按批号重建部件装配历史，核实召回范围、序列件当前归属和原始记录行，并向仓库交付可重算的证据。

## 启动与演示

```sh
docker compose up --build
```

打开 `http://localhost:18445`。脏样例默认从 `CU-041` 反查，显示 5 件受影响部件、6 条带时间窗的证据。选择 `0007` 查看拆装原始行；选择干净样例，再到数量核对比较四类件数。用「归档本次」保存当前批号及查询窗，再到「追溯凭证」重跑和下载 JSON。上传自有 JSON 可参考 `sample_data/clean.json`，导入后在归档列表打开结果。

- 返件登记 `/api/intake` 采信票据，隔离重复和未知序列件。
- 部件字典 `/api/catalog` 归一编码，识别别名冲突与原始批号争议。
- 拆装序列 `/api/sequence` 按时间与序号裁决事件。
- 谱系校验 `/api/graph` 回放有效边并记录被拒的动作。
- 召回反查 `/api/recall` 返回指定批号的历史路径、交集及源行。
- 数量核对 `/api/balance` 分区核对在装、库存、退回和争议。
- 追溯凭证 `/api/evidence/{serial}` 逐件查证，`/api/runs` 保存与下载。

样例接口接受 `sample=clean` 或 `sample=dirty`。完整参数见服务的 `/docs`。

```sh
docker compose exec -T app pytest -q
```

`archive` 命名卷保存 SQLite。需要清空历史时，`docker compose down --volumes` 会删除这个卷及其中归档。

字段和时间边界见 [数据字典](docs/DATA-DICTIONARY.md)。模块、业务反例与测试索引见 [规则映射](docs/DEPTH.md)。
