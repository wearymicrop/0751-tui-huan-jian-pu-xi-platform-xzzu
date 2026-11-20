from collections import Counter, defaultdict

STATES = ("mounted", "stock", "returned", "disputed")
CONFLICTS = {"SERIAL_CONFLICT", "REVISION_CONFLICT", "DOUBLE_MOUNT", "SELF_LOOP",
             "TEMPORAL_CYCLE", "DETACH_MISMATCH", "INVALID_TRANSITION", "NOT_REGISTERED"}


def reconcile(catalog, intake, sequence, graph):
    issues = catalog["issues"] + intake["issues"] + sequence["issues"] + graph["issues"]
    disputes = set(catalog["disputed"])
    reasons = defaultdict(set)
    for error in issues:
        if error.get("at", graph["as_of"]) > graph["as_of"]:
            continue
        for key in ("serial", "other_serial"):
            if serial := error.get(key):
                reasons[serial].add(error["code"])
                if error["code"] in CONFLICTS:
                    disputes.add(serial)
    rows = []
    future = []
    for serial, part in catalog["parts"].items():
        if part["registered"] > graph["as_of"]:
            future.append(serial)
            continue
        parent = graph["active"].get(serial, {}).get("parent")
        state = "disputed" if serial in disputes else (
            "mounted" if parent else graph["dispositions"].get(serial, "stock")
        )
        rows.append({**part, "state": state, "active_parent": parent,
                     "reason_codes": sorted(reasons[serial])})
    counts = Counter(row["state"] for row in rows)
    totals = {key: counts[key] for key in STATES}
    population = len(catalog["parts"]) - len(future)
    difference = population - sum(totals.values())
    return {"status": "MATCHED" if difference == 0 else "DIFFERENCE", "population": population,
            "as_of": graph["as_of"], "difference": difference, "totals": totals, "rows": rows, "future_serials": future}
