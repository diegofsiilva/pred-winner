# pred-winner

Modelos preditivos para o vencedor do 2º turno das eleições presidenciais brasileiras,
usando dados públicos do TSE e do IBGE.

## Como rodar

```bash
uv venv .venv && uv pip install -p .venv/bin/python -r requirements.txt
.venv/bin/python -m predwinner.download    # ~1,8 GB do TSE em data/raw/
.venv/bin/python -m predwinner.evaluate    # backtest -> results/backtest.csv
.venv/bin/python -m predwinner.importance  # importância -> results/importancia_2022.csv
.venv/bin/python -m pytest -q
```

Os indicadores do IBGE são baixados na primeira execução e ficam em cache em `data/raw/`.

## Dados

| Fonte | Conteúdo |
|---|---|
| TSE (`votacao_candidato_munzona`) | Votos do 2º turno presidencial por município, 2002–2022 (sem exterior e voto em trânsito) |
| IBGE SIDRA 5938 | PIB municipal e composição setorial (agro, indústria, adm. pública) |
| IBGE SIDRA 6579 | População estimada (2010 usa a estimativa de 2011) |
| [betafcc/Municipios-Brasileiros-TSE](https://github.com/betafcc/Municipios-Brasileiros-TSE) | Mapeamento de códigos TSE -> IBGE |

## Metodologia

- **Unidade**: município x eleição (2006–2022, ~5.570 municípios por ano).
- **Alvo**: o PT (presente em todos os 2º turnos do período) vence no município.
- **Features**: share do PT na eleição anterior (absoluto e relativo à média nacional),
  PIB per capita, crescimento do PIB per capita em 3 anos relativo ao país, população,
  composição setorial, capital, região, PT incumbente e interação crescimento x incumbência.
- **Modelos**: persistência (baseline), regressão logística, Random Forest,
  Gradient Boosting, fundamentals estilo Abramowitz (regressão linear do share com erro
  normal) e ensemble (média das probabilidades dos quatro últimos).
- **Validação**: janela crescente — cada eleição é prevista só com as anteriores.
- **Resultado nacional**: o fundamentals prevê o share nacional (média ponderada pelos
  votos válidos); nos demais, a média ponderada da probabilidade de vitória serve de índice.
