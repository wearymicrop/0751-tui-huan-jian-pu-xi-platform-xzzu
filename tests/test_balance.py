from app.analysis import analyze


def test_dirty_four_states_partition(dirty_report):
    balance = dirty_report["balance"]
    assert balance["totals"] == {"mounted": 3, "stock": 7, "returned": 2, "disputed": 4}
    assert len({r["serial"] for r in balance["rows"]}) == sum(balance["totals"].values()) == balance["population"] == 16


def test_clean_partition(clean):
    balance = analyze(clean)["balance"]
    assert balance["totals"] == {"mounted": 5, "stock": 9, "returned": 2, "disputed": 0}
    assert balance["difference"] == 0


def test_dispute_outranks_actual_mount(dirty_report):  # TRAP-19
    row = next(r for r in dirty_report["balance"]["rows"] if r["serial"] == "0009")
    assert (row["state"], row["active_parent"]) == ("disputed", "DRV-23")
    assert row["reason_codes"] == ["DOUBLE_MOUNT", "INVALID_TRANSITION"]


def test_return_then_restock_changes_ownership(clean):
    balance = analyze(clean)["balance"]
    states = {r["serial"]: r["state"] for r in balance["rows"]}
    assert (states["0007"], states["0008"], states["CLIP-1"]) == ("returned", "stock", "stock")


def test_unregistered_future_serial_excluded(clean):
    clean["parts"].append({"serial": "FUTURE", "batch": "ZZ-01", "kind": "电器", "registered": "2026-05-21T08:00:00+08:00"})
    balance = analyze(clean)["balance"]
    assert balance["future_serials"] == ["FUTURE"] and balance["population"] == 16


def test_stale_record_does_not_turn_return_into_dispute(dirty_report):
    row = next(r for r in dirty_report["balance"]["rows"] if r["serial"] == "0007")
    assert row["state"] == "returned" and row["active_parent"] is None and "STALE_REVISION" in row["reason_codes"]


def test_balance_http(client):
    report = client.get("/api/balance").json()
    assert report["status"] == "MATCHED" and report["difference"] == 0
