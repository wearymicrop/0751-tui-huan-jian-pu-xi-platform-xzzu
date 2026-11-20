from collections import defaultdict
from app.identity import token
from app.modules.catalog.service import resolve
from app.reasons import issue
from app.timebox import moment


def order_events(rows, catalog):
    candidates, issues = [], []
    for row, raw in enumerate(rows, 1):
        try:
            child_key, parent_key = token(raw["child"]), token(raw["parent"])
            action, revision = raw["action"], raw["revision"]
            if action not in ("mount", "detach") or type(revision) is not int or revision < 1:
                raise ValueError("动作或序号无效")
            at = moment(raw["at"])
        except (KeyError, TypeError, ValueError, OverflowError):
            issues.append(issue("BAD_ROW", "events", row, raw=raw))
            continue
        child, parent = resolve(catalog, child_key), resolve(catalog, parent_key)
        if child is None or parent is None:
            issues.append(issue("UNKNOWN_PART", "events", row, child=child_key, parent=parent_key))
            continue
        candidates.append(dict(row=row, serial=child, parent=parent, action=action, revision=revision, at=at))
    candidates.sort(key=lambda event: (event["at"], event["revision"], event["row"]))
    ordered = []
    seen = defaultdict(dict)
    latest = defaultdict(int)
    for event in candidates:
        row, child, rev = event["row"], event["serial"], event["revision"]
        marker = (event["parent"], event["at"], event["action"])
        if rev in seen[child]:
            kept, original = seen[child][rev]
            code = "DUPLICATE" if original == marker else (
                "STALE_REVISION" if rev < latest[child] else "REVISION_CONFLICT"
            )
            issues.append(issue(code, "events", row, serial=child, revision=rev, at=event["at"], kept_row=kept))
        elif rev < latest[child]:
            issues.append(issue("STALE_REVISION", "events", row, serial=child, revision=rev, at=event["at"], latest=latest[child]))
        else:
            seen[child][rev] = row, marker
            latest[child] = rev
            ordered.append(event)
    return {"events": ordered, "issues": issues,
            "counts": {"input": len(rows), "accepted": len(ordered), "isolated": len(issues)}}
