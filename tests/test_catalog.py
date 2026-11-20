from app.analysis import analyze
from app.modules.catalog.service import build_catalog, resolve


def test_leading_zero_is_identity(dirty_report):  # TRAP-08
    catalog = dirty_report["catalog"]
    assert resolve(catalog, "0007") == "0007"
    assert resolve(catalog, "7") is None


def test_fullwidth_alias_normalizes(dirty_report):  # TRAP-06
    assert resolve(dirty_report["catalog"], " ｔｃ－０７ ") == "0007"


def test_ambiguous_alias_is_order_independent(dirty):  # TRAP-22
    for rows in (dirty["aliases"], dirty["aliases"][::-1]):
        catalog = build_catalog(dirty["parts"], rows)
        assert resolve(catalog, "共码") is None
        assert [e["candidates"] for e in catalog["issues"] if e["code"] == "ALIAS_CONFLICT"] == [["DRV-21", "DRV-22"]] * 2


def test_canonical_identifier_precedes_alias(clean):
    clean["aliases"].append({"alias": "0007", "serial": "0008"})
    catalog = analyze(clean)["catalog"]
    assert resolve(catalog, "0007") == "0007"
    assert catalog["issues"][0]["code"] == "ALIAS_CONFLICT"


def test_placeholder_does_not_create_part(dirty_report):  # TRAP-07
    catalog = dirty_report["catalog"]
    assert "未知" not in catalog["parts"]
    assert any(e["source"] == "parts" and e["row"] == 18 and e["code"] == "BAD_ROW" for e in catalog["issues"])


def test_conflicting_part_is_distinct_from_duplicate(dirty):
    dirty["parts"].append(dirty["parts"][0])
    catalog = analyze(dirty)["catalog"]
    assert catalog["disputed"] == ["CASE-9"]
    assert {e["row"]: e["code"] for e in catalog["issues"] if e["source"] == "parts"} == {
        17: "SERIAL_CONFLICT", 18: "BAD_ROW", 19: "DUPLICATE",
    }


def test_catalog_http(client):
    data = client.get("/api/catalog").json()
    assert len(data["parts"]) == 16 and data["aliases"]["旧驱-21"] == "DRV-21"
