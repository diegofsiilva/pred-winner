"""Divisões temporais: treina com eleições anteriores e testa na seguinte."""
import pandas as pd


def expanding_splits(df: pd.DataFrame, min_train_years: int = 1):
    """Gera (ano_teste, treino, teste) com janela crescente de eleições passadas."""
    years = sorted(df.ano.unique())
    for i in range(min_train_years, len(years)):
        yield years[i], df[df.ano < years[i]], df[df.ano == years[i]]
