from app.modules.balance.service import reconcile
from app.modules.catalog.service import build_catalog
from app.modules.graph.service import replay
from app.modules.intake.service import check_returns
from app.modules.recall.service import recall
from app.modules.sequence.service import order_events
from app.source import validate_source


def analyze(data):
    as_of = validate_source(data)
    catalog = build_catalog(data["parts"], data["aliases"])
    intake = check_returns(data["returns"], catalog)
    sequence = order_events(data["events"], catalog)
    graph = replay(catalog, sequence, intake, as_of)
    balance = reconcile(catalog, intake, sequence, graph)
    return dict(intake=intake, catalog=catalog, sequence=sequence, graph=graph, balance=balance)


def with_recall(result, batch, start=None, end=None):
    return {**result, "recall": recall(result["catalog"], result["graph"], batch, start, end)}
