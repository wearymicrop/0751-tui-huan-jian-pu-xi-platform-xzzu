LABELS = {
    "BAD_ROW": "字段缺失或格式错误", "UNKNOWN_PART": "序列件未登记",
    "DUPLICATE": "重复上报", "SERIAL_CONFLICT": "序列件档案不一致",
    "ALIAS_CONFLICT": "别名指向多个序列件", "UNKNOWN_BATCH": "批号未登记",
    "STALE_REVISION": "序号陈旧", "REVISION_CONFLICT": "同序号内容冲突",
    "SELF_LOOP": "部件不能装入自身", "TEMPORAL_CYCLE": "同一时段形成环",
    "DOUBLE_MOUNT": "同件仍在另一处", "DETACH_MISMATCH": "拆卸父件不匹配",
    "INVALID_TRANSITION": "返件状态与实物位置不一致", "NOT_REGISTERED": "事件早于登记时间",
}


def issue(code, source, row, **details):
    return {"code": code, "message": LABELS[code], "source": source, "row": row, **details}
