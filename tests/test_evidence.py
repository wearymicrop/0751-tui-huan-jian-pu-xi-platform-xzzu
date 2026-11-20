from concurrent.futures import ThreadPoolExecutor
from app.manifest import make_manifest
from app.modules.evidence.store import get, save


def test_serial_alias_retains_mount_and_detach_rows(client):
    response = client.get("/api/evidence/TC-07")
    evidence = response.json()
    assert evidence["part"]["serial"] == "0007"
    assert [(e["mount_row"], e["detach_row"]) for e in evidence["edges"]] == [(3, 1)]
    assert len(evidence["exposures"]) == 3


def test_archive_rerun_id_and_full_digest(client):
    run = client.post("/api/runs", json={"sample": "dirty"}).json()
    replay = client.post(f"/api/runs/{run['id']}/rerun").json()
    assert run["manifest"] == replay["manifest"] and run["id"] == replay["id"]
    assert run["reused"] is False and replay["reused"] is True
    assert len(client.get("/api/runs").json()["runs"]) == 1


def test_export_embeds_source_and_fixed_results(client):
    run = client.post("/api/runs", json={"sample": "dirty"}).json()
    reply = client.get(f"/api/runs/{run['id']}/export")
    assert "attachment" in reply.headers["Content-Disposition"]
    payload = reply.json()
    assert payload["manifest"] == make_manifest(payload["source"], payload["query"], payload["result"])
    assert payload["result"]["recall"]["count"] == 5
    assert "TEMPORAL_CYCLE" in reply.text


def test_unknown_run_has_business_error(client):
    reply = client.get("/api/runs/missing")
    assert (reply.status_code, reply.json()["code"]) == (404, "UNKNOWN_RUN")


def test_archive_requires_exactly_one_source(client, clean):
    for payload in ({}, {"sample": "clean", "source": clean}):
        reply = client.post("/api/runs", json=payload)
        assert (reply.status_code, reply.json()["code"]) == (422, "CHOOSE_SOURCE")


def test_custom_archived_source_survives_reopen(client, clean):
    run = client.post("/api/runs", json={"source": clean}).json()
    stored = get(run["id"])
    assert stored["source"] == clean
    assert client.get(f"/api/evidence/TC-07?run={run['id']}").json()["position"]["state"] == "returned"


def test_idempotent_sqlite_concurrent_insert(client):
    run = {"id": "same-digest", "query": {"batch": "B"}, "result": {}}
    with ThreadPoolExecutor(max_workers=4) as workers:
        reused = list(workers.map(save, [run] * 8))
    assert reused.count(False) == 1 and get("same-digest") == run
