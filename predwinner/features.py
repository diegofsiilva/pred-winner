"""Montagem do dataset (município x eleição) com alvo e features."""
import numpy as np
import pandas as pd

from predwinner.config import INCUMBENT_PARTY, PROCESSED_DIR, YEARS
from predwinner.ibge import load_indicators
from predwinner.tse import runoff_results, tse_to_ibge

REGIONS = {1: "Norte", 2: "Nordeste", 3: "Sudeste", 4: "Sul", 5: "Centro-Oeste"}


def results_all_years() -> pd.DataFrame:
    df = pd.concat([runoff_results(y) for y in YEARS])
    df = df.merge(tse_to_ibge(), on="codigo_tse", how="inner")
    df["regiao"] = (df.codigo_ibge // 1_000_000).map(REGIONS)
    return df


def add_lagged_vote(df: pd.DataFrame) -> pd.DataFrame:
    """Share do PT na eleição anterior, absoluto e relativo à média nacional."""
    national = df.groupby("ano").votos_pt.sum() / df.groupby("ano").votos_validos.sum()
    prev = df[["codigo_ibge", "ano", "share_pt"]].copy()
    prev["desvio_pt_ant"] = prev.share_pt - prev.ano.map(national)
    prev["ano"] += 4
    prev = prev.rename(columns={"share_pt": "share_pt_ant"})
    return df.merge(prev, on=["codigo_ibge", "ano"], how="inner")
