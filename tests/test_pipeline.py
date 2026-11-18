import json
from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

from app import app as fastapi_app

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "config.json").read_text())
client = TestClient(fastapi_app)


def test_artifacts_created():
    assert (ROOT / "artifacts" / "model.joblib").exists()
    assert (ROOT / "artifacts" / "metrics.json").exists()


def test_metrics_content():
    m = json.loads((ROOT / "artifacts" / "metrics.json").read_text())
    for key in ["student_id", "accuracy", "training_rows", "model_version", "git_sha"]:
        assert key in m
    assert m["student_id"] == CONFIG["student_id"]
    assert 0.5 <= m["accuracy"] <= 1.0
    rows = len(pd.read_csv(ROOT / "dataset" / "train.csv"))
    assert m["training_rows"] == rows


def test_metrics_endpoint():
    r = client.get("/metrics")
    assert r.status_code == 200
    body = r.json()
    assert body["student_id"] == CONFIG["student_id"]
    assert "git_sha" in body and "model_version" in body


def test_predict_endpoint():
    record = {f: 0.1 for f in CONFIG["features"]}
    r = client.post("/predict", json={"records": [record]})
    assert r.status_code == 200
    body = r.json()
    assert len(body["predictions"]) == 1
    assert body["predictions"][0] in (0, 1)
