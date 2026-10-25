"""Backtest de todos os modelos com validação temporal."""
import pandas as pd

from predwinner.config import ROOT
from predwinner.features import build_dataset
from predwinner.metrics import classification_report, national_share
from predwinner.models import MODELS
from predwinner.validation import expanding_splits


def backtest(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for year, train, test in expanding_splits(df):
        for name, make in MODELS.items():
            model = make().fit(train)
            proba = model.predict_proba(test)
            # Só o fundamentals prevê share; nos demais, a média ponderada da
            # probabilidade de vitória serve de índice nacional (> 0.5 = PT vence).
            nacional = model.predict_share(test) if hasattr(model, "predict_share") else proba
            rows.append({
                "ano": year,
                "modelo": name,
                **classification_report(test.pt_venceu, proba),
                "pt_nacional_prev": national_share(nacional, test.votos_validos),
                "pt_nacional_real": national_share(test.share_pt, test.votos_validos),
            })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    results = backtest(build_dataset())
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    results.to_csv(out / "backtest.csv", index=False, float_format="%.4f")
    print(results.round(3).to_string(index=False))
