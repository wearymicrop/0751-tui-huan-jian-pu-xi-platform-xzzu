from app.analysis import analyze
from app.source import load_sample


def from_sample(sample: str = "dirty"):
    return analyze(load_sample(sample))
