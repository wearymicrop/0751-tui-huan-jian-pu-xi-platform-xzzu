from collections import defaultdict
from app.identity import token
from app.reasons import issue
from app.timebox import moment


def build_catalog(part_rows, alias_rows):
    claims = defaultdict(list)
    issues = []
    for row, raw in enumerate(part_rows, 1):
        try:
            serial = token(raw["serial"])
            part = {"serial": serial, "batch": token(raw["batch"]), "kind": token(raw["kind"]),
                    "registered": moment(raw["registered"])}
        except (KeyError, TypeError, ValueError, OverflowError):
            issues.append(issue("BAD_ROW", "parts", row, raw=raw))
            continue
        claims[serial].append((row, part))
    parts = {}
    disputed = set()
    for serial, entries in sorted(claims.items()):
        first_row, record = entries[0]
        parts[serial] = {**record, "row": first_row}
        for row, other in entries[1:]:
            if other != record:
                disputed.add(serial)
            code = "DUPLICATE" if other == record else "SERIAL_CONFLICT"
            issues.append(issue(code, "parts", row, serial=serial, kept_row=first_row, raw=other))
    aliases = resolve_aliases(parts, alias_rows, issues)
    return {"parts": parts, "aliases": aliases, "issues": issues, "disputed": sorted(disputed)}


def resolve_aliases(parts, rows, issues):
    claims = defaultdict(list)
    for row, raw in enumerate(rows, 1):
        try:
            alias, serial = token(raw["alias"]), token(raw["serial"])
        except (KeyError, TypeError, ValueError):
            issues.append(issue("BAD_ROW", "aliases", row, raw=raw))
            continue
        if serial not in parts:
            issues.append(issue("UNKNOWN_PART", "aliases", row, serial=serial, alias=alias))
        else:
            claims[alias].append((row, serial))
    aliases = {}
    for alias, entries in sorted(claims.items()):
        owners = {serial for _, serial in entries}
        if alias in parts:
            owners.add(alias)
        if len(owners) > 1:
            issues.extend(issue("ALIAS_CONFLICT", "aliases", row, alias=alias, serial=serial,
                                candidates=sorted(owners)) for row, serial in entries)
        else:
            aliases[alias] = entries[0][1]
            issues.extend(issue("DUPLICATE", "aliases", row, alias=alias, serial=serial)
                          for row, serial in entries[1:])
    return aliases


def resolve(catalog, serial):
    serial = token(serial)
    return serial if serial in catalog["parts"] else catalog["aliases"].get(serial)
