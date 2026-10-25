"""Votação presidencial de 2º turno por município a partir dos arquivos do TSE."""
import zipfile

import pandas as pd

from predwinner.config import RAW_DIR

COLS = ["NR_TURNO", "CD_CARGO", "SG_UF", "CD_MUNICIPIO", "SG_PARTIDO", "QT_VOTOS_NOMINAIS"]


def read_president_runoff(year: int) -> pd.DataFrame:
    """Votos por (município, partido) no 2º turno presidencial, sem exterior nem voto em trânsito."""
    with zipfile.ZipFile(RAW_DIR / f"tse_{year}.zip") as z:
        with z.open(f"votacao_candidato_munzona_{year}_BR.csv") as f:
            df = pd.read_csv(f, sep=";", encoding="latin1", usecols=COLS)
    df = df[(df.NR_TURNO == 2) & (df.CD_CARGO == 1) & ~df.SG_UF.isin(["ZZ", "VT"])]
    return (
        df.groupby(["SG_UF", "CD_MUNICIPIO", "SG_PARTIDO"], as_index=False)
        .QT_VOTOS_NOMINAIS.sum()
        .rename(
            columns={
                "SG_UF": "uf",
                "CD_MUNICIPIO": "codigo_tse",
                "SG_PARTIDO": "partido",
                "QT_VOTOS_NOMINAIS": "votos",
            }
        )
    )
