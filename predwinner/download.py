"""Download dos dados brutos do TSE (votação) e do mapeamento TSE -> IBGE."""
from pathlib import Path

import requests

from predwinner.config import RAW_DIR, TSE_IBGE_MAP_URL, TSE_URL, YEARS


def fetch(url: str, dest: Path) -> Path:
    if dest.exists():
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
    tmp.rename(dest)
    return dest


def download_tse(years=YEARS) -> None:
    for year in years:
        print(f"TSE {year}...")
        fetch(TSE_URL.format(year=year), RAW_DIR / f"tse_{year}.zip")
    fetch(TSE_IBGE_MAP_URL, RAW_DIR / "municipios_tse_ibge.csv")


if __name__ == "__main__":
    download_tse()
