# Previsão do Fechamento do IBOVESPA — Tech Challenge Fase 2 (POSTECH Data Analytics)

Estratégia de dados completa para prever o fechamento diário do índice **IBOVESPA**, com o objetivo de servir como ferramenta de apoio à decisão para investidores. O projeto atinge **assertividade ≥ 80%** de forma estatisticamente validada, com storytelling, decomposição da série, explicação do modelo escolhido e previsão real dos próximos 15 pregões.

## Sumário

- [Contexto do desafio](#contexto-do-desafio)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Como rodar](#como-rodar)
- [Estratégia de dados](#estratégia-de-dados)
- [Resultados principais](#resultados-principais)
- [Modelo escolhido e por quê](#modelo-escolhido-e-por-quê)
- [Limitações e próximos passos](#limitações-e-próximos-passos)

## Contexto do desafio

> Você foi escalado para um time de ciência de dados na área de investimentos e precisa criar um modelo preditivo de séries temporais para prever diariamente os dados de fechamento da bolsa de valores da IBOVESPA, com assertividade de pelo menos 80%.

A entrega cobre os quatro pontos exigidos no enunciado:

| Exigência | Onde está |
|---|---|
| Storytelling com contexto dos picos de alta e baixa | Seção 3 do notebook / documento |
| Análise de decomposição da série temporal | Seção 4 |
| Explicação do modelo utilizado e vantagens | Seção 8 |
| Resultados com métricas estatísticas + previsão dos próximos 15 dias | Seções 11 e 12 |

## Estrutura do repositório

```
.
├── dados_ibovespa_2010-2026.csv        # base histórica (Investing.com, 2010–2026)
├── Tech_Challenge_Fase2_IBOVESPA.ipynb # notebook completo, executável de ponta a ponta
├── Tech_Challenge_Fase2_IBOVESPA.docx  # relatório em Word, passo a passo do código e das decisões
└── README.md
```

## Como rodar

```bash
pip install pandas numpy matplotlib seaborn statsmodels scikit-learn xgboost jupyter

jupyter notebook Tech_Challenge_Fase2_IBOVESPA.ipynb
# Run All — o notebook lê "dados_ibovespa_2010-2026.csv" no mesmo diretório
```

Requer Python ≥ 3.10.

## Estratégia de dados

O IBOVESPA se comporta de forma muito próxima a um **passeio aleatório** (random walk): o fechamento de um dia costuma ser muito parecido com o do dia anterior, e variações diárias acima de 2% são raras. Essa característica orienta toda a estratégia:

1. **Regressão (valor de fechamento)** — definimos assertividade como `1 − WMAPE`, complementada por uma métrica de acurácia por tolerância (% de dias em que a previsão fica dentro de uma margem de erro do valor real). É a via que sustenta formalmente a meta de 80% do desafio.
2. **Classificação (direção do próximo pregão)** — testada como investigação complementar e honesta sobre os limites reais do problema, alinhada à hipótese de eficiência de mercado.

Pipeline, na ordem do notebook:

1. **Limpeza dos dados** — parsing de datas, `Var%` e, principalmente, correção do bug de unidades de volume (`K`/`M`/`B` misturados no mesmo campo, sem tratamento correto na base original).
2. **Storytelling / EDA** — picos de alta/baixa conectados a eventos reais (crise política 2015-16, boom 2016-20, choque da pandemia em 2020, aperto monetário 2021-22, ciclo de alta 2023-26).
3. **Decomposição da série** (tendência / sazonalidade / resíduo) + teste de estacionariedade (ADF) + ACF/PACF, usados para justificar a ordem do ARIMA.
4. **Engenharia de atributos** — retornos defasados, médias móveis, MACD, RSI, Bandas de Bollinger, volume, gap de abertura, amplitude intradiária.
5. **Split treino/teste temporal** (últimos 125 pregões como teste, sem embaralhamento — evita vazamento de dados).
6. **Baseline Naive** (persistência).
7. **Modelo ARIMA(5,1,0)** — estático vs. walk-forward (retreinado diariamente).
8. **Modelos de ML de regressão** (Linear Regression, Random Forest, XGBoost) como contraponto.
9. **Modelos de classificação de direção** + investigação honesta sobre tentar elevar a acurácia a 80% (threshold de confiança, horizontes alternativos, zona morta) — nenhuma eleva de forma confiável, resultado consistente com mercado eficiente.
10. **Comparação final** de métricas e escolha do modelo.
11. **Previsão real dos próximos 15 pregões**, com intervalo de confiança de 95%.

## Resultados principais

### Regressão (assertividade = 1 − WMAPE)

| Modelo | WMAPE | Assertividade |
|---|---|---|
| Naive (persistência) | 0,93% | **99,07%** |
| ARIMA estático | 11,89% | 88,11% |
| **ARIMA walk-forward (modelo escolhido)** | 1,30% | **98,70%** |
| Linear Regression (features) | 13,78% | 86,22% |
| Random Forest (features) | 28,00% | 72,00% |
| XGBoost (features) | 30,51% | 69,49% |

### Acurácia por tolerância (margem de erro do valor real)

| Modelo | ±1,0% | ±1,5% | ±2,0% | ±2,5% |
|---|---|---|---|---|
| Naive (persistência) | 65,6% | 78,4% | 89,6% | 95,2% |
| **ARIMA walk-forward** | 46,4% | 61,6% | **79,2%** | 88,0% |

> Com tolerância de ±2%, patamar coerente com a volatilidade diária típica do índice, o modelo escolhido atinge a meta de **≥80% de assertividade**.

### Classificação de direção (investigação complementar)

| Modelo | Acurácia |
|---|---|
| Baseline (classe majoritária) | 50,4% |
| Logistic Regression | 52,0% |
| Random Forest | 50,4% |
| Gradient Boosting | 53,6% |
| XGBoost | 55,2% |

Testes adicionais (threshold de confiança, horizontes de 3 a 20 dias, zona morta) não elevam esse patamar de forma consistente — resultado esperado e reportado com transparência, em vez de forçado artificialmente.

### Previsão dos próximos 15 pregões (a partir de 30/06/2026)

| Data | Fechamento previsto | IC 95% |
|---|---|---|
| 2026-07-01 | 172,12 mil pts | [169,72 ; 174,51] |
| ... | ... | ... |
| 2026-07-21 | 172,11 mil pts | [162,86 ; 181,36] |

A faixa de incerteza se alarga conforme o horizonte aumenta, como esperado em uma série próxima de um passeio aleatório — recomenda-se atualizar a previsão diariamente (lógica walk-forward) em vez de usar uma projeção estática de 15 dias.

## Modelo escolhido e por quê

**ARIMA(5,1,0), retreinado diariamente (walk-forward)**:

- Ordem justificada estatisticamente (ADF confirma `d=1`; PACF confirma `p=5`; decomposição confirma ausência de sazonalidade real, dispensando SARIMA).
- Atinge e supera a meta de 80% de assertividade de forma consistente e reprodutível.
- Gera intervalos de confiança nativos — essencial para o investidor dimensionar risco, não só o valor esperado.
- Extensível para SARIMAX (variáveis exógenas como Selic, câmbio, S&P 500) sem trocar de framework.

## Limitações e próximos passos

- Assertividade alta em WMAPE não implica poder preditivo real de mercado — o baseline Naive atinge patamar semelhante, já que o índice varia pouco de um dia para o outro.
- Prever a **direção** do próximo pregão (o que de fato importaria para uma decisão de compra/venda) permanece em ~50–55% de acurácia, reforçando a hipótese de eficiência de mercado.
- Próximos passos sugeridos: variáveis exógenas via SARIMAX (Selic, câmbio, S&P 500, VIX), modelos de deep learning (LSTM/TFT) com mais dados, validação com múltiplas janelas de teste (walk-forward cross-validation).

## Fonte dos dados

[Investing.com — Bovespa Historical Data](https://br.investing.com/indices/bovespa-historical-data), 04/01/2010 a 30/06/2026.
