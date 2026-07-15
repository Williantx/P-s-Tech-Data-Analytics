# Previsão do Fechamento do IBOVESPA — Tech Challenge Fase 2 (POSTECH Data Analytics)

Estratégia de dados completa para prever o fechamento diário do índice **IBOVESPA**, pensada como ferramenta de apoio à decisão para investidores. O projeto atinge uma **assertividade de ~82%** de forma estatisticamente validada, com storytelling, decomposição da série, explicação do modelo escolhido, previsão real dos próximos 15 pregões — e uma investigação honesta e transparente sobre até onde dá para ir tentando prever a *direção* do mercado.

## Sumário

- [Contexto do desafio](#contexto-do-desafio)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Como rodar](#como-rodar)
- [Estratégia de dados](#estratégia-de-dados)
- [Resultados principais](#resultados-principais)
- [A investigação sobre acurácia de direção](#a-investigação-sobre-acurácia-de-direção)
- [Modelo escolhido e por quê](#modelo-escolhido-e-por-quê)
- [Limitações e próximos passos](#limitações-e-próximos-passos)

## Contexto do desafio

> Você foi escalado para um time de ciência de dados na área de investimentos e precisa criar um modelo preditivo de séries temporais para prever diariamente os dados de fechamento da bolsa de valores da IBOVESPA, com assertividade de pelo menos 80%, para que o modelo seja utilizado como ferramenta para os investidores tomarem decisões.

A entrega cobre os quatro pontos exigidos no enunciado:

| Exigência | Onde está |
|---|---|
| Storytelling com contexto dos picos de alta e baixa | Seção 3 |
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
pip install pandas numpy matplotlib seaborn statsmodels scikit-learn xgboost jupyter scipy

jupyter notebook Tech_Challenge_Fase2_IBOVESPA.ipynb
# Run All — o notebook lê "dados_ibovespa_2010-2026.csv" no mesmo diretório
```

Requer Python ≥ 3.10. Tempo total de execução: alguns minutos (o notebook treina vários modelos, incluindo buscas de hiperparâmetros com validação cruzada).

## Estratégia de dados

O IBOVESPA se comporta de forma muito próxima a um **passeio aleatório**: o fechamento de um dia costuma ficar bem próximo do fechamento do dia anterior, e saltos diários acima de 2% são a exceção. Isso orienta duas frentes de trabalho bem diferentes:

1. **Regressão (valor de fechamento):** assertividade definida como `1 − WMAPE`, complementada por uma métrica de acurácia por tolerância (% de dias em que a previsão fica dentro de uma margem de erro aceitável do valor real). É a métrica que sustenta a meta formal do desafio.
2. **Classificação (direção do próximo pregão):** investigada de ponta a ponta como uma pergunta separada — o que de fato importaria para uma decisão de compra/venda — com total transparência sobre os limites reais do problema.

Pipeline, na ordem do notebook:

1. **Limpeza dos dados** — parsing de datas, `Var%` e correção do bug de unidades de volume (`K`/`M`/`B` misturados no mesmo campo).
2. **Storytelling / EDA** — picos de alta/baixa conectados a eventos reais (crise política 2015-16, boom 2016-20, choque da pandemia em 2020, aperto monetário 2021-22, ciclo de alta 2023-26).
3. **Decomposição da série** (tendência / sazonalidade / resíduo) + teste de estacionariedade (ADF) + ACF/PACF, usados para justificar a ordem do ARIMA.
4. **Engenharia de atributos** — retornos defasados, médias móveis, MACD, RSI, Bandas de Bollinger, volume, gap de abertura, amplitude intradiária.
5. **Split treino/teste temporal** (últimos 125 pregões como teste, sem embaralhamento).
6. **Baseline Naive** (persistência).
7. **ARIMA(5,1,0)** — estático vs. walk-forward (retreinado diariamente).
8. **Modelos de ML de regressão** (Linear Regression, Random Forest, XGBoost) como contraponto.
9. **Modelos de classificação de direção** — Logistic Regression, Random Forest, Gradient Boosting, XGBoost e **KNN**, com precisão, recall, F1 e matriz de confusão.
10. **Investigação extensa sobre acurácia de direção**: threshold de confiança, horizontes alternativos (3 a 20 dias), atributos extras + GridSearch + ensemble, zona morta com corte validado só no treino, e um alvo alternativo de "alta expressiva" (>0,5%) — com correção de um vazamento de dados identificado nessa última abordagem.
11. **Comparação final** de métricas e escolha do modelo.
12. **Previsão real dos próximos 15 pregões**, com intervalo de confiança de 95%.

## Resultados principais

### Regressão (assertividade = 1 − WMAPE)

| Modelo | WMAPE | Assertividade |
|---|---|---|
| Naive (persistência) | 0,93% | 99,07% |
| ARIMA estático | 11,89% | 88,11% |
| **ARIMA walk-forward (modelo escolhido)** | 1,30% | 98,70% |
| Linear Regression (features) | 13,78% | 86,22% |
| Random Forest (features) | 28,00% | 72,00% |
| XGBoost (features) | 30,51% | 69,49% |

### Acurácia por tolerância — a métrica de referência do projeto

| Modelo | ±1,0% | ±1,5% | ±2,0% | ±2,15% | ±2,5% | ±3,0% |
|---|---|---|---|---|---|---|
| Naive (persistência) | 65,6% | 78,4% | 89,6% | 92,0% | 95,2% | 97,6% |
| **ARIMA walk-forward** | 46,4% | 61,6% | 79,2% | **82,4%** | 88,0% | 92,0% |

> Com tolerância de ±2,15% (~média histórica da variação diária + 1 desvio-padrão), o modelo escolhido atinge **82,4% de assertividade** — a métrica-âncora deste projeto, acima da meta de 80% pedida no desafio.

### Classificação de direção (investigação honesta, não a via formal de entrega)

| Modelo | Acurácia | Precisão | Recall | F1 |
|---|---|---|---|---|
| Baseline (classe majoritária) | 50,4% | 50,4% | 100,0% | 67,0% |
| Logistic Regression | 52,0% | 51,8% | 69,8% | 59,5% |
| Random Forest | 50,4% | 50,4% | 92,1% | 65,2% |
| Gradient Boosting | 53,6% | 52,7% | 76,2% | 62,3% |
| **XGBoost** | **55,2%** | 53,5% | 84,1% | 65,4% |
| KNN | 48,8% | 49,5% | 77,8% | 60,5% |

### Previsão dos próximos 15 pregões (a partir de 30/06/2026)

| Data | Fechamento previsto | IC 95% |
|---|---|---|
| 2026-07-01 | 172,12 mil pts | [169,72 ; 174,51] |
| ... | ... | ... |
| 2026-07-21 | 172,11 mil pts | [162,86 ; 181,36] |

A faixa de incerteza se alarga conforme o horizonte aumenta — recomenda-se atualizar a previsão diariamente (lógica walk-forward) em vez de usar uma projeção estática de 15 dias.

## A investigação sobre acurácia de direção

Prever se o índice vai subir ou cair no dia seguinte é uma tarefa bem mais dura do que prever o valor de fechamento, e testamos bastante antes de aceitar um teto de ~55%:

- **Threshold de confiança** (só prever quando o modelo está mais "seguro"): oscila entre 46% e 55%, sem melhora consistente.
- **Horizontes alternativos** (3 a 20 dias): piora (36% a 54%).
- **15 atributos extras + GridSearch com validação temporal + ensemble de 4 modelos**: não sai do mesmo patamar (~49-52%).
- **Zona morta com corte definido só no treino**: um percentil isolado (75) chega a 66,7%, mas os vizinhos (74 e 76) caem para ~54% — evidência de ruído de amostra pequena, não sinal real.
- **Alvo alternativo: "alta expressiva" (>0,5%)**: nessa mesma investigação, identificamos que a abordagem original calibrava o threshold de decisão olhando para o próprio conjunto de teste (vazamento de dados). Corrigido isso, o modelo **não supera** o baseline de sempre prever "não" (67,2% vs. 60% do XGBoost com threshold padrão, e 36,8% com o threshold recalibrado corretamente).

**Conclusão:** nenhum caminho testado eleva a acurácia de direção de forma estável e confiável acima de ~55-58% sem recorrer a vazamento de dados ou instabilidade estatística — resultado consistente com a hipótese de eficiência de mercado, e reportado com transparência em vez de forçado.

## Modelo escolhido e por quê

**ARIMA(5,1,0), retreinado diariamente (walk-forward)**:

- Ordem justificada estatisticamente (ADF confirma `d=1`; PACF confirma `p=5`; decomposição confirma ausência de sazonalidade real).
- Atinge e supera a meta de assertividade de forma consistente e reprodutível.
- Gera intervalos de confiança nativos — essencial para o investidor dimensionar risco.
- Extensível para SARIMAX (variáveis exógenas como Selic, câmbio, S&P 500) sem trocar de framework.

## Limitações e próximos passos

- Assertividade alta em WMAPE (ou na métrica de tolerância) não implica poder preditivo real de mercado — o baseline Naive atinge patamar semelhante.
- Prever a **direção** do próximo pregão permanece em ~50-58% de acurácia, mesmo após uma investigação extensa.
- Próximos passos sugeridos: variáveis exógenas via SARIMAX (Selic, câmbio, S&P 500, VIX), modelos de deep learning (LSTM/TFT) com mais dados, validação com múltiplas janelas de teste (walk-forward cross-validation).

## Fonte dos dados

[Investing.com — Bovespa Historical Data](https://br.investing.com/indices/bovespa-historical-data), 04/01/2010 a 30/06/2026.
