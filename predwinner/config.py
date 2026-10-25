from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

# Eleições com 2º turno presidencial em que o PT esteve presente.
YEARS = [2002, 2006, 2010, 2014, 2018, 2022]

# Partido do presidente em exercício no momento de cada eleição.
INCUMBENT_PARTY = {
    2002: "PSDB",
    2006: "PT",
    2010: "PT",
    2014: "PT",
    2018: "MDB",
    2022: "PL",
}

TSE_URL = (
    "https://cdn.tse.jus.br/estatistica/sead/odsele/"
    "votacao_candidato_munzona/votacao_candidato_munzona_{year}.zip"
)
TSE_IBGE_MAP_URL = (
    "https://raw.githubusercontent.com/betafcc/Municipios-Brasileiros-TSE/"
    "master/municipios_brasileiros_tse.csv"
)
