from app.modules.balance.routes import router as balance
from app.modules.catalog.routes import router as catalog
from app.modules.evidence.routes import router as evidence
from app.modules.graph.routes import router as graph
from app.modules.intake.routes import router as intake
from app.modules.recall.routes import router as recall
from app.modules.sequence.routes import router as sequence

ROUTERS = (intake, catalog, sequence, graph, recall, balance, evidence)
