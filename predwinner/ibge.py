"""Indicadores municipais do IBGE via API de agregados (SIDRA)."""
import pandas as pd
import requests

from predwinner.config import RAW_DIR

API = "https://servicodados.ibge.gov.br/api/v3/agregados/{table}/periodos/{period}/variaveis/{var}"

PIB_TABLE = 5938
PIB_VARS = {
    37: "pib",  # mil reais, preços correntes
    516: "share_agro",
    520: "share_industria",
    528: "share_adm_publica",
}
POP_TABLE, POP_VAR = 6579, 9324
# A estimativa de população não é publicada em ano de Censo; usa-se o ano seguinte.
POP_FALLBACK = {2010: 2011}


def fetch_variable(table: int, var: int, periods: list[int]) -> pd.DataFrame:
    # Um período por requisição: a API recusa consultas com muitos valores.
    rows = []
    for period in periods:
        url = API.format(table=table, period=period, var=var)
        r = requests.get(url, params={"localidades": "N6[all]"}, timeout=120)
        r.raise_for_status()
        rows += [
            (int(s["localidade"]["id"]), int(year), value)
            for s in r.json()[0]["resultados"][0]["series"]
            for year, value in s["serie"].items()
        ]
    df = pd.DataFrame(rows, columns=["codigo_ibge", "ano", "valor"])
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    return df


def load_indicators(periods: list[int]) -> pd.DataFrame:
    """Tabela larga (codigo_ibge, ano) com PIB, composição setorial e população."""
    path = RAW_DIR / "ibge_indicadores.csv"
    if path.exists():
        return pd.read_csv(path)
    frames = []
    for var, name in PIB_VARS.items():
        frames.append(fetch_variable(PIB_TABLE, var, periods).assign(variavel=name))
    pop_periods = [POP_FALLBACK.get(p, p) for p in periods]
    pop = fetch_variable(POP_TABLE, POP_VAR, pop_periods)
    pop["ano"] = pop.ano.replace({v: k for k, v in POP_FALLBACK.items() if k in periods})
    frames.append(pop.assign(variavel="populacao"))
    df = (
        pd.concat(frames)
        .pivot_table(index=["codigo_ibge", "ano"], columns="variavel", values="valor")
        .reset_index()
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return df
