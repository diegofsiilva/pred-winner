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

## Resultados (backtest)

Acurácia por município:

| Modelo | 2010 | 2014 | 2018 | 2022 |
|---|---|---|---|---|
| persistência | **0,852** | 0,854 | 0,850 | **0,924** |
| logística | 0,796 | **0,880** | **0,905** | 0,857 |
| random forest | 0,807 | 0,841 | 0,881 | 0,884 |
| gradient boosting | 0,808 | 0,807 | 0,891 | 0,871 |
| fundamentals | 0,776 | 0,840 | 0,876 | 0,867 |
| ensemble | 0,811 | 0,849 | 0,893 | 0,871 |

Log loss (menor é melhor): os modelos ficam entre 0,22 e 0,47; a persistência, por dar
probabilidades 0/1, fica entre 1,0 e 2,1.

Share nacional do PT previsto vs. real (vencedor correto em negrito):

| Modelo | 2010 (real 0,561) | 2014 (0,517) | 2018 (0,449) | 2022 (0,509) |
|---|---|---|---|---|
| persistência | **0,689** | **0,578** | 0,513 | 0,323 |
| logística | **0,576** | 0,479 | **0,410** | 0,280 |
| random forest | **0,608** | **0,555** | **0,461** | 0,297 |
| gradient boosting | **0,601** | **0,549** | **0,451** | 0,291 |
| fundamentals | **0,610** | **0,552** | 0,501 | 0,382 |
| ensemble | **0,632** | **0,551** | **0,452** | 0,284 |

## Limitações

- **Nenhum modelo acerta 2022.** As features estruturais não capturam o clima nacional
  de cada eleição; os modelos aprendem com 2018 que "PT fora do governo" implica derrota.
  Prever o vencedor nacional exigiria pesquisas de intenção de voto ou aprovação do governo.
- Só 4 eleições de treino: efeitos nacionais (incumbência, economia do país) são quase
  indistinguíveis de um efeito fixo por ano.
- Os modelos **ordenam** bem os municípios (AUC 0,87–0,98, acima da persistência), mas
  em acurácia a persistência é difícil de bater.
- O PIB municipal só existe a preços correntes; por isso o crescimento é relativo ao país.
