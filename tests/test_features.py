import pandas as pd
import pytest

from predwinner.features import add_lagged_vote


def test_add_lagged_vote_uses_previous_election():
    df = pd.DataFrame({
        "codigo_ibge": [1, 2, 1, 2],
        "ano": [2006, 2006, 2010, 2010],
        "share_pt": [0.6, 0.2, 0.7, 0.3],
        "votos_pt": [60, 20, 70, 30],
        "votos_validos": [100, 100, 100, 100],
    })
    out = add_lagged_vote(df).set_index("codigo_ibge")
    assert list(out.ano.unique()) == [2010]
    assert out.loc[1, "share_pt_ant"] == 0.6
    # Média nacional em 2006 = 0.4
    assert out.loc[1, "desvio_pt_ant"] == pytest.approx(0.2)
    assert out.loc[2, "desvio_pt_ant"] == pytest.approx(-0.2)
