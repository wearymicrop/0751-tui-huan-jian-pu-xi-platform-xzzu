from app.analysis import analyze


def test_inbound_event_order(dirty_report):
    rows = dirty_report["sequence"]["events"]
    assert (rows[0]["row"], rows[0]["serial"]) == (2, "DRV-21")
    assert [row["at"] for row in rows] == sorted(row["at"] for row in rows)


def test_stale_revision_is_quarantined(dirty_report):  # TRAP-26
    info = next(e for e in dirty_report["sequence"]["issues"] if e["code"] == "STALE_REVISION")
    assert (info["serial"], info["revision"], info["row"]) == ("0007", 1, 17)
    assert 17 not in [x["row"] for x in dirty_report["sequence"]["events"]]


def test_equivalent_timezone_duplicate(clean):  # TRAP-11
    clean["events"].append({**clean["events"][0], "at": "2026-05-02T00:00:00Z"})
    issues = analyze(clean)["sequence"]["issues"]
    assert [(i["code"], i["kept_row"]) for i in issues] == [("DUPLICATE", 1)]


def test_wrong_revision_type_has_source(dirty_report):
    result = dirty_report["sequence"]
    assert result["counts"] == {"input": 22, "accepted": 19, "isolated": 3}
    assert any(e["code"] == "BAD_ROW" and e["row"] == 22 for e in result["issues"])


def test_ambiguous_alias_produces_no_candidate(dirty_report):
    error = next(e for e in dirty_report["sequence"]["issues"] if e["code"] == "UNKNOWN_PART")
    assert (error["parent"], error["child"]) == ("共码", "TC-08")


def test_same_timestamp_inverted_source_order(clean):
    clean["events"][2], clean["events"][3] = clean["events"][3], clean["events"][2]
    result = analyze(clean)
    assert not result["sequence"]["issues"] and not result["graph"]["issues"]
    assert result["graph"]["active"]["DRV-21"]["parent"] == "UNIT-B"


def test_sequence_http(client):
    assert client.get("/api/sequence?sample=clean").json()["counts"]["accepted"] == 16
