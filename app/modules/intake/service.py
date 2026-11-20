from app.identity import token
from app.modules.catalog.service import resolve
from app.reasons import issue
from app.timebox import moment


def check_returns(rows, catalog):
    entries, rejected, seen = [], [], {}
    for row, raw in enumerate(rows, 1):
        try:
            ticket = token(raw["ticket"])
            submitted = token(raw["serial"])
            action = raw["action"]
            if action not in ("return", "restock"):
                raise ValueError("退回或复入库")
            timestamp = moment(raw["at"])
        except (KeyError, TypeError, ValueError, OverflowError):
            rejected.append(issue("BAD_ROW", "returns", row, raw=raw))
            continue
        serial = resolve(catalog, submitted)
        if serial is None:
            rejected.append(issue("UNKNOWN_PART", "returns", row, serial=submitted, ticket=ticket))
            continue
        identity = (serial, action, timestamp)
        if ticket in seen:
            kept, original = seen[ticket]
            code = "DUPLICATE" if identity == original else "SERIAL_CONFLICT"
            rejected.append(issue(code, "returns", row, serial=serial, other_serial=original[0],
                                  ticket=ticket, at=timestamp, kept_row=kept))
            continue
        seen[ticket] = row, identity
        entries.append(dict(row=row, ticket=ticket, serial=serial, submitted=submitted, action=action, at=timestamp))
    entries.sort(key=lambda entry: (entry["at"], entry["row"]))
    return {"entries": entries, "issues": rejected,
            "counts": {"input": len(rows), "accepted": len(entries), "isolated": len(rejected)}}
