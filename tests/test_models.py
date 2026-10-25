import numpy as np
import pandas as pd
import pytest

from predwinner.features import FEATURES
from predwinner.models import MODELS


@pytest.fixture
def toy():
    rng = np.random.default_rng(0)
    n = 200
    df = pd.DataFrame(rng.random((n, len(FEATURES))), columns=FEATURES)
    df["pt_incumbente"] = rng.integers(0, 2, n)
    df["share_pt"] = (0.2 + 0.6 * df.share_pt_ant + rng.normal(0, 0.05, n)).clip(0, 1)
    df["pt_venceu"] = (df.share_pt > 0.5).astype(int)
    df["votos_validos"] = rng.integers(100, 1000, n)
    return df


@pytest.mark.parametrize("name", MODELS)
def test_models_return_probabilities(name, toy):
    proba = MODELS[name]().fit(toy).predict_proba(toy)
    assert proba.shape == (len(toy),)
    assert ((proba >= 0) & (proba <= 1)).all()
