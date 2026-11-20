from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = {"clean": "干净样例", "dirty": "脏样例"}
RULE_VERSION = "1.0"


def database_path():
    return Path(os.environ.get("LINEAGE_DB", "lineage.sqlite3"))
