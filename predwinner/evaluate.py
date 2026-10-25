"""Backtest de todos os modelos com validação temporal."""
import pandas as pd

from predwinner.config import ROOT
from predwinner.features import build_dataset
from predwinner.metrics import classification_report
from predwinner.models import MODELS
from predwinner.validation import expanding_splits


def backtest(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for year, train, test in expanding_splits(df):
        for name, make in MODELS.items():
            proba = make().fit(train).predict_proba(test)
            rows.append({"ano": year, "modelo": name, **classification_report(test.pt_venceu, proba)})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    results = backtest(build_dataset())
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    results.to_csv(out / "backtest.csv", index=False, float_format="%.4f")
    print(results.round(3).to_string(index=False))
