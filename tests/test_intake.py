from app.analysis import analyze


def test_clean_ticket_partition(clean):
    assert analyze(clean)["intake"]["counts"] == {"input": 6, "accepted": 6, "isolated": 0}


def test_dirty_ticket_partition(dirty_report):
    assert dirty_report["intake"]["counts"] == {"input": 9, "accepted": 7, "isolated": 2}


def test_alias_retry_deduplicates(dirty_report):
    error = dirty_report["intake"]["issues"][0]
    assert (error["code"], error["row"], error["kept_row"], error["serial"]) == ("DUPLICATE", 7, 1, "0007")


def test_unknown_ticket_retains_source_row(dirty_report):
    error = dirty_report["intake"]["issues"][1]
    assert (error["code"], error["row"], error["ticket"]) == ("UNKNOWN_PART", 8, "RT-099")


def test_conflicting_ticket_retains_first(clean):  # TRAP-14
    clean["returns"].append({**clean["returns"][0], "serial": "FUSE-3"})
    result = analyze(clean)["intake"]
    assert result["issues"][0]["other_serial"] == "0007"
    assert result["issues"][0]["code"] == "SERIAL_CONFLICT"
    assert [x["serial"] for x in result["entries"] if x["ticket"] == "RT-060"] == ["0007"]


def test_return_order_preserves_line_numbers(clean):  # TRAP-13
    clean["returns"].reverse()
    first = analyze(clean)["intake"]["entries"][0]
    assert (first["ticket"], first["row"]) == ("RT-061", 5)


def test_intake_http(client):
    response = client.get("/api/intake?sample=clean")
    assert response.status_code == 200 and response.json()["counts"]["accepted"] == 6
