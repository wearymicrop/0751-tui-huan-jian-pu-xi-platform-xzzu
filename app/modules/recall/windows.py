from collections import defaultdict
from app.timebox import intersection


def trace(parts, lot, edges, start, end, disputed):
    by_child = defaultdict(list)
    for edge in edges:
        by_child[edge["child"]].append(edge)
    evidence = []
    seeds = [key for key, value in parts.items() if value["batch"] == lot and key not in disputed]
    for origin in seeds:
        queue = [(origin, max(start, parts[origin]["registered"]), end, [origin], [])]
        while queue:
            serial, left, right, path, links = queue.pop()
            if left >= right:
                continue
            for edge in by_child[serial]:
                overlap = intersection(left, right, edge["start"], edge["end"])
                if not overlap:
                    continue
                parent = edge["parent"]
                route = [*path, parent]
                provenance = [*links, edge["mount_row"]]
                evidence.append(dict(origin=origin, serial=parent, start=overlap[0], end=overlap[1],
                                     path=route, mount_rows=provenance))
                queue.append((parent, *overlap, route, provenance))
    return sorted(evidence, key=lambda item: (item["serial"], item["start"], item["path"], item["mount_rows"]))
