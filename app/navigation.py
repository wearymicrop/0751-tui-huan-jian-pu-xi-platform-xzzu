SECTIONS = {
    "recall": "召回反查", "intake": "返件登记", "catalog": "部件字典", "sequence": "拆装序列",
    "graph": "谱系校验", "balance": "数量核对", "evidence": "追溯凭证",
}
TABLES = {
    "intake": ("采信返件单", "entries", (("ticket", "票号"), ("serial", "序列件"), ("action", "动作"), ("at", "时间"), ("row", "来源行"))),
    "catalog": ("规范序列件", "parts", (("serial", "序列件"), ("batch", "批号"), ("kind", "部件"), ("registered", "登记时间"))),
    "sequence": ("已排序事件", "events", (("serial", "子件"), ("parent", "父件"), ("action", "动作"), ("revision", "序号"), ("at", "生效时刻"), ("row", "来源行"))),
    "graph": ("有效装配边", "edges", (("child", "子件"), ("parent", "父件"), ("start", "装入"), ("end", "拆出"), ("mount_row", "装入行"), ("detach_row", "拆出行"))),
    "balance": ("序列件归属", "rows", (("serial", "序列件"), ("batch", "批号"), ("state", "状态"), ("active_parent", "有效父件"), ("reason_codes", "关联原因"))),
}
