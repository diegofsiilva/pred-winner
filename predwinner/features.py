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


def economic_features(election_years: list[int]) -> pd.DataFrame:
    """Indicadores do ano anterior à eleição e crescimento do PIB per capita em 3 anos.

    O crescimento é medido relativo ao do país, o que remove a inflação
    (o PIB municipal só existe a preços correntes).
    """
    periods = sorted({y - 1 for y in election_years} | {y - 4 for y in election_years})
    ind = load_indicators(periods)
    ind["pib_pc"] = ind.pib / ind.populacao
    national = ind.groupby("ano").pib.sum() / ind.groupby("ano").populacao.sum()

    cur = ind.assign(ano=ind.ano + 1)
    base = ind[["codigo_ibge", "ano", "pib_pc"]].assign(ano=ind.ano + 4)
    df = cur.merge(base, on=["codigo_ibge", "ano"], suffixes=("", "_base"))
    nat_growth = np.log(df.ano.map(lambda a: national[a - 1] / national[a - 4]))
    df["crescimento_rel"] = np.log(df.pib_pc / df.pib_pc_base) - nat_growth
    df["log_pib_pc"] = np.log(df.pib_pc)
    df["log_pop"] = np.log(df.populacao)
    # Valor adicionado negativo em alguns municípios gera participações fora de [0, 100].
    shares = ["share_agro", "share_industria", "share_adm_publica"]
    df[shares] = df[shares].clip(0, 100)
    df["crescimento_rel"] = df.crescimento_rel.clip(-1, 1)
    cols = ["codigo_ibge", "ano", "log_pib_pc", "log_pop", "crescimento_rel",
            "share_agro", "share_industria", "share_adm_publica"]
    return df[df.ano.isin(election_years)][cols]


FEATURES = [
    "share_pt_ant", "desvio_pt_ant", "log_pib_pc", "log_pop", "crescimento_rel",
    "share_agro", "share_industria", "share_adm_publica", "capital", "pt_incumbente",
    "crescimento_x_incumbente",
] + [f"regiao_{r}" for r in REGIONS.values()]


def build_dataset() -> pd.DataFrame:
    path = PROCESSED_DIR / "dataset.csv"
    if path.exists():
        return pd.read_csv(path)
    df = add_lagged_vote(results_all_years())
    df = df.merge(economic_features(sorted(df.ano.unique())), on=["codigo_ibge", "ano"])
    df["pt_incumbente"] = (df.ano.map(INCUMBENT_PARTY) == "PT").astype(int)
    df["crescimento_x_incumbente"] = df.crescimento_rel * df.pt_incumbente
    for r in REGIONS.values():
        df[f"regiao_{r}"] = (df.regiao == r).astype(int)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return df
