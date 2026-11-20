from app.modules.graph.edges import detach, mount
from app.reasons import issue

ACTION_PRIORITY = {"detach": 0, "return": 1, "restock": 2, "mount": 3}


def replay(catalog, sequence, intake, as_of):
    active, history, dispositions, issues, accepted, future = {}, [], {}, [], [], []
    scheduled = sorted(sequence["events"] + intake["entries"],
                       key=lambda row: (row["at"], ACTION_PRIORITY[row["action"]], row["row"]))
    for entry in scheduled:
        action, child, stamp = entry["action"], entry["serial"], entry["at"]
        source = "events" if "parent" in entry else "returns"
        if stamp > as_of:
            future.append({**entry, "source": source})
            continue
        parts = catalog["parts"]
        parent = entry.get("parent", child)
        if max(parts[child]["registered"], parts[parent]["registered"]) > stamp:
            code, details = "NOT_REGISTERED", {}
        elif action == "detach":
            code, details = detach(active, history, entry)
        elif action == "mount" and (dispositions.get(child) == "returned" or dispositions.get(parent) == "returned"):
            code, details = "INVALID_TRANSITION", {"action": action}
        elif action == "mount":
            code, details = mount(active, entry)
        else:
            code, details = disposition(active, dispositions, child, action)
        if code:
            issues.append(issue(code, source, entry["row"], serial=child, **details))
        else:
            accepted.append({**entry, "source": source})
    return {"as_of": as_of, "edges": sorted(history + list(active.values()),
                                          key=lambda edge: (edge["start"], edge["child"], edge["parent"])),
            "active": active, "dispositions": dispositions, "issues": issues,
            "accepted": accepted, "future": future}


def disposition(active, dispositions, serial, action):
    returned = dispositions.get(serial) == "returned"
    has_children = any(edge["parent"] == serial for edge in active.values())
    if (action == "return" and (serial in active or has_children or returned)) or (action == "restock" and not returned):
        return "INVALID_TRANSITION", {"action": action}
    dispositions[serial] = "returned" if action == "return" else "stock"
    return None, {}
