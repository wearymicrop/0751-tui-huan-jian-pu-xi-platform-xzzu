from app.analysis import analyze


def test_cycle_returns_exact_path(dirty_report):  # TRAP-20
    problem = next(i for i in dirty_report["graph"]["issues"] if i["code"] == "TEMPORAL_CYCLE")
    assert problem["path"] == ["UNIT-B", "DRV-23", "UNIT-B"]
    assert "UNIT-B" not in dirty_report["graph"]["active"]


def test_alias_self_loop_resolves_before_validation(dirty_report):
    problem = next(i for i in dirty_report["graph"]["issues"] if i["code"] == "SELF_LOOP")
    assert problem["path"] == ["DRV-21", "DRV-21"]


def test_double_mount_keeps_original_parent(dirty_report):  # TRAP-25
    problem = next(i for i in dirty_report["graph"]["issues"] if i["code"] == "DOUBLE_MOUNT")
    assert (problem["serial"], problem["active_parent"], problem["row"]) == ("0009", "DRV-23", 19)
    assert dirty_report["graph"]["active"]["0009"]["parent"] == "DRV-23"


def test_reverse_edges_separated_in_time_do_not_form_cycle(clean):
    clean["events"].append({"child": "UNIT-A", "parent": "DRV-21", "action": "mount", "revision": 1, "at": "2026-05-06T00:00:00Z"})
    result = analyze(clean)["graph"]
    assert result["issues"] == []
    assert result["active"]["UNIT-A"]["parent"] == "DRV-21"


def test_wrong_parent_detach_keeps_active_edge(clean):  # TRAP-21
    clean["events"][4]["parent"] = "DRV-22"
    result = analyze(clean)["graph"]
    assert result["issues"][0]["code"] == "DETACH_MISMATCH"
    assert result["active"]["0007"]["parent"] == "DRV-21"


def test_future_mount_does_not_change_snapshot(clean):
    graph = analyze(clean)["graph"]
    assert graph["future"][0]["serial"] == "FUSE-3"
    assert "FUSE-3" not in graph["active"]


def test_mounted_part_cannot_be_returned(dirty_report):
    graph = dirty_report["graph"]
    issue = next(e for e in graph["issues"] if e["code"] == "INVALID_TRANSITION")
    assert issue["serial"] == "0009" and issue["source"] == "returns"
    assert "0009" not in graph["dispositions"]


def test_graph_http(client):
    graph = client.get("/api/graph?sample=clean").json()
    assert len(graph["edges"]) == 10
