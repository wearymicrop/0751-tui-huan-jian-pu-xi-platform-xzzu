def cycle_path(active, child, parent):
    path = [child, parent]
    cursor = parent
    while cursor in active:
        cursor = active[cursor]["parent"]
        path.append(cursor)
        if cursor == child:
            return path
    return None


def mount(active, event):
    child, parent = event["serial"], event["parent"]
    if child == parent:
        return "SELF_LOOP", {"path": [child, child]}
    if child in active:
        return "DOUBLE_MOUNT", {"active_parent": active[child]["parent"]}
    path = cycle_path(active, child, parent)
    if path:
        return "TEMPORAL_CYCLE", {"path": path}
    active[child] = dict(child=child, parent=parent, start=event["at"], end=None,
                         mount_row=event["row"], detach_row=None)
    return None, {}


def detach(active, history, event):
    child = event["serial"]
    edge = active.get(child)
    if edge is None or edge["parent"] != event["parent"]:
        return "DETACH_MISMATCH", {"active_parent": edge["parent"] if edge else None}
    active.pop(child)
    if edge["start"] < event["at"]:
        history.append({**edge, "end": event["at"], "detach_row": event["row"]})
    return None, {}
