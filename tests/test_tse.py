import zipfile

import pytest

from predwinner import tse

ROWS = [
    # turno, cargo, uf, municipio, partido, votos
    (2, 1, "SP", 100, "PT", 30),
    (2, 1, "SP", 100, "PT", 30),  # outra zona do mesmo município
    (2, 1, "SP", 100, "PSDB", 40),
    (1, 1, "SP", 100, "PT", 999),  # 1º turno: ignorado
    (2, 3, "SP", 100, "PT", 999),  # outro cargo: ignorado
    (2, 1, "ZZ", 200, "PT", 999),  # exterior: ignorado
    (2, 1, "VT", 300, "PT", 999),  # voto em trânsito: ignorado
]


@pytest.fixture
def raw_dir(tmp_path, monkeypatch):
    header = ";".join(tse.COLS)
    lines = [header] + [";".join(map(str, r)) for r in ROWS]
    with zipfile.ZipFile(tmp_path / "tse_2006.zip", "w") as z:
        z.writestr("votacao_candidato_munzona_2006_BR.csv", "\n".join(lines).encode("latin1"))
    monkeypatch.setattr(tse, "RAW_DIR", tmp_path)


def test_runoff_results_filters_and_aggregates(raw_dir):
    out = tse.runoff_results(2006)
    assert len(out) == 1
    row = out.iloc[0]
    assert row.votos_validos == 100
    assert row.votos_pt == 60
    assert row.share_pt == 0.6
    assert row.pt_venceu == 1
