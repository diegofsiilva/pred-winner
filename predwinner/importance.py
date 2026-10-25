"""Importância por permutação das features no teste de 2022."""
import pandas as pd
from sklearn.inspection import permutation_importance

from predwinner.config import ROOT
from predwinner.features import FEATURES, build_dataset
from predwinner.models import random_forest

if __name__ == "__main__":
    df = build_dataset()
    train, test = df[df.ano < 2022], df[df.ano == 2022]
    model = random_forest().fit(train)
    r = permutation_importance(
        model.estimator, test[FEATURES], test.pt_venceu, scoring="roc_auc", n_repeats=5, random_state=0
    )
    out = pd.DataFrame({"feature": FEATURES, "importancia_auc": r.importances_mean})
    out = out.sort_values("importancia_auc", ascending=False)
    out.to_csv(ROOT / "results" / "importancia_2022.csv", index=False, float_format="%.4f")
    print(out.to_string(index=False))
