from app.navigation import SECTIONS


def test_health_and_all_pages(client):
    assert client.get("/health").json() == {"status": "ok", "version": "1.0"}
    for section, title in SECTIONS.items():
        reply = client.get(f"/board/{section}")
        assert reply.status_code == 200 and f"<h1>{title}</h1>" in reply.text


def test_bad_sample_and_bad_source_are_client_errors(client):
    assert client.get("/api/intake?sample=nope").json()["code"] == "UNKNOWN_SAMPLE"
    assert client.post("/api/runs", json={"source": {}}).json()["code"] == "BAD_SOURCE"
