from app.analysis import with_recall


def test_recall_uses_historical_assemblies(dirty_report):
    result = with_recall(dirty_report, "CU-041")["recall"]
    assert result["targets"] == ["DRV-21", "DRV-22", "DRV-23", "UNIT-A", "UNIT-B"]
    assert len(result["paths"]) == 6


def test_intersection_does_not_invent_exposure(dirty_report):  # TRAP-23
    result = with_recall(dirty_report, "CU-041")["recall"]
    assert "UNIT-C" not in result["targets"]
    assert next(e for e in result["paths"] if e["origin"] == "0008")["path"] == ["0008", "DRV-22"]


def test_adjacent_handoff_hits_only_new_parent(client):
    data = client.get("/api/recall", params={"start": "2026-05-05T00:00:00Z", "end": "2026-05-06T00:00:00Z"}).json()
    assert data["targets"] == ["DRV-21", "UNIT-B"]
    assert next(r for r in data["paths"] if r["serial"] == "UNIT-B")["mount_rows"] == [3, 5]


def test_two_component_edges_are_clipped(dirty_report):
    result = with_recall(dirty_report, " cu-041 ")["recall"]
    west = next(e for e in result["paths"] if e["origin"] == "0007" and e["serial"] == "UNIT-B")
    assert (west["start"], west["end"], west["path"]) == ("2026-05-05T00:00:00.000000Z", "2026-05-08T00:00:00.000000Z", ["0007", "DRV-21", "UNIT-B"])


def test_empty_query_window_rejected(client):
    response = client.get("/api/recall", params={"start": "2026-05-05T00:00:00Z", "end": "2026-05-05T00:00:00Z"})
    assert (response.status_code, response.json()["code"]) == (422, "BAD_WINDOW")


def test_unknown_batch_rejected(client):
    response = client.get("/api/recall?batch=NOT-A-LOT")
    assert (response.status_code, response.json()["code"]) == (404, "UNKNOWN_BATCH")


def test_known_batch_without_installation(client):
    result = client.get("/api/recall?batch=CS-073&sample=clean").json()
    assert (result["count"], result["paths"]) == (0, [])
