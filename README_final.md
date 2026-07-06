# 🌿 AgroSignal
## Plataforma de Processamento de Sinais Aplicada ao Manejo Inteligente de Irrigação Agrícola

**Disciplina:** Sinais e Sistemas  
**Instituição:** CEFET-MG  
**Autor:** Luiz Fernando dos Santos Queiroz  
**Ano:** 2026

---

## Índice

1. [Visão Geral](#1-visão-geral)
2. [Instalação](#2-instalação)
3. [Como Executar](#3-como-executar)
4. [Estrutura de Arquivos](#4-estrutura-de-arquivos)
5. [Formato do CSV de Entrada](#5-formato-do-csv-de-entrada)
6. [Os 4 Pilares de Processamento de Sinais](#6-os-4-pilares-de-processamento-de-sinais)
7. [Pipeline de Processamento](#7-pipeline-de-processamento)
8. [Módulos do Sistema](#8-módulos-do-sistema)
9. [Interface — Modo Fazendeiro](#9-interface--modo-fazendeiro)
10. [Interface — Modo Acadêmico](#10-interface--modo-acadêmico)
11. [Parâmetros Configuráveis](#11-parâmetros-configuráveis)
12. [Culturas e Faixas de Umidade](#12-culturas-e-faixas-de-umidade)
13. [Relatório PDF](#13-relatório-pdf)
14. [Glossário](#14-glossário)
15. [Limitações e Trabalhos Futuros](#15-limitações-e-trabalhos-futuros)

---

## 1. Visão Geral

O **AgroSignal** é uma aplicação web interativa desenvolvida em Python com Streamlit que aplica quatro conceitos fundamentais da disciplina de **Sinais e Sistemas** ao problema real de monitoramento da umidade do solo em lavouras agrícolas.

O sistema recebe como entrada um arquivo CSV com leituras de umidade do solo geradas por sensores agrícolas. Esses dados são tratados como um **sinal discreto** `x[n]` e processados por um pipeline linear de quatro pilares matemáticos. A saída é uma recomendação concreta de irrigação para o agricultor — quando o solo precisa de água, quando não precisa, e quanto tempo resta antes de atingir o nível crítico.

### Por que Sinais e Sistemas na Agricultura?

As leituras temporais de sensores de umidade formam um sinal discreto gerado por um sistema dinâmico complexo. A umidade do solo é resultado da superposição de múltiplos fenômenos físicos simultâneos: evapotranspiração, irrigação, chuva e drenagem profunda. A teoria de Sinais e Sistemas oferece as ferramentas exatas para decompor, filtrar e interpretar esse sinal — extraindo informações que a simples observação dos dados brutos não permite.

### Os 4 Pilares

| Pilar | Ferramenta | Função no Sistema |
|---|---|---|
| 1 | Filtro IIR Butterworth Passa-Baixa | Suaviza o sinal, eliminando ruídos de alta frequência |
| 2 | Operador Diferencial Discreto | Estima a taxa de queda da umidade e o tempo até o nível crítico |
| 3 | Transformada Rápida de Fourier (FFT) | Identifica os ciclos periódicos de irrigação no histórico |
| 4 | Normalização Z-score | Detecta variações abruptas e outliers no sinal |

---

## 2. Instalação

### Requisito

Python 3.10 ou superior.

### Dependências

```bash
pip install streamlit pandas numpy scipy plotly fpdf2
```

| Biblioteca | Versão mínima | Uso no projeto |
|---|---|---|
| streamlit | 1.32 | Interface web interativa |
| pandas | 2.0 | Leitura e processamento do CSV |
| numpy | 1.24 | Operações matemáticas vetoriais |
| scipy | 1.11 | `butter`, `filtfilt` (Pilar 1) e `fft`, `fftfreq` (Pilar 3) |
| plotly | 5.18 | Gráficos interativos |
| fpdf2 | 2.7 | Geração do relatório PDF |

---

## 3. Como Executar

**Passo 1** — Coloque os 4 arquivos na mesma pasta:

```
agrosignal/
├── app.py
├── signal_processing.py
├── diagnostics.py
└── report.py
```

**Passo 2** — Abra o terminal dentro da pasta e execute:

```bash
py -m streamlit run app.py
```

Se `py` não funcionar, tente `python` ou `python3`:

```bash
python -m streamlit run app.py
```

**Passo 3** — O navegador abrirá automaticamente em `http://localhost:8501`.

**Passo 4** — Na sidebar esquerda, faça o upload de um arquivo CSV com os dados de umidade.

Para encerrar: `Ctrl + C` no terminal.

---

## 4. Estrutura de Arquivos

```
agrosignal/
│
├── app.py
│   Interface principal Streamlit. Lê o CSV, executa os 4 pilares
│   na ordem correta, exibe os dois modos de visualização
│   (Fazendeiro e Acadêmico) e integra todos os módulos.
│
├── signal_processing.py
│   Motor matemático do sistema. Implementa os 4 pilares:
│     calcular_fs()               → frequência de amostragem (fs = 1.0)
│     filtro_butterworth()        → Pilar 1
│     calcular_derivada_discreta()→ Pilar 2
│     analisar_espectro_fft()     → Pilar 3
│     detetar_anomalias_zscore()  → Pilar 4
│     calcular_estatisticas()     → métricas descritivas
│
├── diagnostics.py
│   Avalia os resultados dos 4 pilares e gera um diagnóstico
│   automático com score de saúde (0–100), observações técnicas
│   e recomendações de ação.
│
└── report.py
    Gera o relatório técnico em PDF consolidando todos os
    resultados para download.
```

---

## 5. Formato do CSV de Entrada

O arquivo deve conter exatamente duas colunas:

```csv
timestamp,umidade
2026-01-01 00:00:00,35.2
2026-01-01 01:00:00,34.8
2026-01-01 02:00:00,34.1
2026-01-01 03:00:00,55.0
2026-01-01 04:00:00,52.3
2026-01-01 05:00:00,49.8
```

### Regras

| Campo | Formato | Observação |
|---|---|---|
| `timestamp` | `AAAA-MM-DD HH:MM:SS` | Uma leitura por hora |
| `umidade` | Número decimal (0 a 100) | Percentual de saturação do solo |

O sistema assume `fs = 1 amostra/hora` fixo. O intervalo entre timestamps deve ser de 1 hora.

**Mínimo recomendado:** 48 linhas (2 dias) para que a FFT produza resultados informativos. Para identificar o ciclo diário de 24h com clareza, recomenda-se pelo menos 7 dias (168 amostras).

### Tela de boas-vindas

Quando nenhum arquivo está carregado, o sistema exibe a tela de instrução com o formato esperado e uma tabela de exemplo com 6 linhas demonstrativas.

---

## 6. Os 4 Pilares de Processamento de Sinais

---

### Pilar 1 — Filtro Digital IIR Butterworth Passa-Baixa com Fase Zero

**Função:** `filtro_butterworth(sinal, cutoff, fs, ordem)` em `signal_processing.py`

**O que resolve:** o sinal bruto `x[n]` do sensor contém ruídos transientes de alta frequência — interferências elétricas, vibrações, instabilidades de hardware. Esses ruídos precisam ser removidos antes que qualquer análise seja feita, pois caso contrário as decisões de irrigação poderiam ser baseadas em dados corrompidos.

**Como funciona:**

A magnitude da resposta em frequência do filtro Butterworth de ordem N é:

```
|H(e^jω)| = 1 / sqrt(1 + (ω/ωc)^(2N))
```

Frequências abaixo da frequência de corte `ωc` passam com ganho próximo de 1 — sem distorção. Frequências acima são progressivamente atenuadas. A curva de transição é maximalmente plana na banda de passagem, sem ondulações.

A equação de diferenças que implementa o filtro no domínio discreto é:

```
y[n] = Σ(b_i · x[n-i]) - Σ(a_j · y[n-j])
```

Os coeficientes `b_i` e `a_j` são calculados pela função `butter()` do SciPy a partir dos parâmetros N e ωc via transformação bilinear.

**Fase zero via `filtfilt`:**

A função `filtfilt` aplica o filtro duas vezes: uma vez para frente e uma vez para trás no tempo. Esse processamento bidirecional cancela o atraso de fase introduzido pelo filtro IIR, garantindo que o sinal filtrado `y[n]` não seja deslocado no tempo em relação a `x[n]`. Os eventos (irrigação, chuva) aparecem no instante cronológico correto.

**Implementação:**

```python
def filtro_butterworth(sinal, cutoff, fs, ordem=2):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq          # normaliza pela frequência de Nyquist
    b, a = butter(ordem, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, sinal)          # filtragem de fase zero
```

**Parâmetros configuráveis:**
- **Ordem N** (1 a 5): quanto maior, mais abrupta a transição entre banda passante e bloqueada
- **Frequência de corte fc** (0.01 a 0.49 ciclos/hora): define o limiar de separação

**Efeito visual:** no Modo Acadêmico, a linha `y[n]` (verde claro) aparece suavizada sobre `x[n]` (verde escuro), com os ruídos visualmente removidos.

---

### Pilar 2 — Operador Diferencial Discreto

**Função:** `calcular_derivada_discreta(sinal, fs)` em `signal_processing.py`

**O que resolve:** saber que o solo está com 35% de umidade é útil, mas saber que está caindo 0.8% por hora é ainda mais útil — porque permite calcular quanto tempo resta antes de atingir o nível crítico e antecipar a irrigação.

**Como funciona:**

A derivada contínua `dU/dt` é aproximada no domínio discreto pelo método das diferenças finitas. Três esquemas são usados para cobrir todos os pontos do vetor:

Primeiro ponto (diferença avançada):
```
ẋ[0] = (x[1] - x[0]) / Δt
```

Pontos intermediários (diferença central — menor erro numérico):
```
ẋ[n] = (x[n+1] - x[n-1]) / (2·Δt)
```

Último ponto (diferença atrasada):
```
ẋ[-1] = (x[-1] - x[-2]) / Δt
```

Como `fs = 1 amostra/hora`, `Δt = 1/fs = 1 hora`, simplificando os denominadores.

**Implementação:**

```python
def calcular_derivada_discreta(sinal, fs):
    dt = 1.0 / fs
    derivada = np.zeros_like(sinal)
    derivada[0] = (sinal[1] - sinal[0]) / dt
    for n in range(1, len(sinal) - 1):
        derivada[n] = (sinal[n+1] - sinal[n-1]) / (2 * dt)
    derivada[-1] = (sinal[-1] - sinal[-2]) / dt
    return derivada
```

**Uso prático no app:** o valor `derivada[-1]` indica a tendência atual do solo:

- Negativo → solo secando (evapotranspiração dominando)
- Positivo → solo acumulando umidade (irrigação ou chuva ativa)
- Próximo de zero → umidade estável

Com a taxa de queda, o sistema estima o tempo restante:

```python
horas_ate_limiar = (umidade_atual - faixa_min) / abs(taxa_queda)
```

**Efeito visual:** subplot central do Modo Acadêmico mostra `dy/dt` ao longo do tempo. Picos negativos correspondem a períodos de evaporação intensa; picos positivos correspondem a eventos de irrigação.

---

### Pilar 3 — Análise Espectral via FFT

**Função:** `analisar_espectro_fft(sinal, fs)` em `signal_processing.py`

**O que resolve:** o domínio do tempo mostra o que aconteceu com a umidade, mas não explica o padrão subjacente. A FFT converte o sinal para o domínio da frequência, revelando quais ciclos periódicos estão presentes — tipicamente o ciclo de irrigação diária em 24h e o ciclo de evapotranspiração.

**Como funciona:**

A Transformada Discreta de Fourier projeta `x[n]` sobre uma base de exponenciais complexas:

```
X(k) = Σ x[n] · e^(-j·2π·k·n/N),   n = 0, 1, ..., N-1
```

Desenvolvida pela Fórmula de Euler:

```
X(k) = Σ x[n] · [cos(2πkn/N) - j·sin(2πkn/N)]
```

A magnitude normalizada de cada componente:

```
A[k] = (2/N) · |X[k]|
```

A frequência correspondente ao bin k:

```
f[k] = k · fs / N   [ciclos/hora]
```

O período correspondente:

```
T[k] = 1 / f[k]   [horas]
```

**Detalhes da implementação:**

Antes da FFT, a média do sinal é subtraída (`sinal - np.mean(sinal)`) para eliminar a componente DC — o nível médio de umidade — que dominaria o espectro e ocultaria os padrões de irrigação.

Apenas a metade positiva do espectro é retornada (`freqs[:N//2]`), pois para sinais reais o espectro é simétrico (propriedade de simetria hermitiana).

O sistema captura automaticamente os 3 picos de maior amplitude, ignorando a frequência zero, e os retorna como lista de periodicidades com período em horas, frequência e amplitude.

**O que o espectro revela:**

| Padrão | Interpretação |
|---|---|
| Pico dominante em ~24h | Irrigação diária regular — ciclo solar saudável |
| Pico dominante em ~12h | Irrigação duas vezes ao dia |
| Pico dominante em ~8h | Irrigação três vezes ao dia |
| Espectro sem pico definido | Irrigação irregular ou apenas chuvas esporádicas |
| Energia espalhada em altas frequências | Desordem no regime hídrico, possíveis falhas |

**Efeito visual:** gráfico de barras no Modo Acadêmico exibe `|X(f)|` no eixo Y e frequência em ciclos/hora no eixo X. Abaixo, as 3 componentes dominantes são listadas com período, frequência e amplitude.

---

### Pilar 4 — Normalização de Amplitude via Z-score

**Função:** `detetar_anomalias_zscore(sinal, limiar_zscore)` em `signal_processing.py`

**O que resolve:** identificar amostras que se desviam abruptamente do comportamento histórico do sinal — variações que não correspondem à dinâmica física natural do solo, podendo indicar chuva intensa, calor extremo, falha de irrigação ou problema no sensor.

**Como funciona:**

O Z-score é uma transformação linear que reescala cada amostra em unidades de desvio padrão em relação à média histórica:

```
Z[n] = (x[n] - μ) / σ
```

Onde `μ` é a média aritmética e `σ` é o desvio padrão da série temporal completa. A transformação é puramente linear — preserva a forma do sinal, apenas normaliza sua amplitude para uma escala adimensional.

A classificação de cada amostra:

```
Detecção = Normal    se |Z[n]| ≤ λ
           Anomalia  se |Z[n]| > λ
```

Onde `λ` é o limiar configurável na sidebar (padrão: 2.5).

**Por que Z-score e não limiares fixos:**

O Z-score se adapta à volatilidade do sinal. Se o solo naturalmente varia muito (solo arenoso, clima semiárido), o desvio padrão aumenta e o sistema torna-se menos sensível a alarmes falsos. Se o solo é estável, o sistema fica mais alerta a qualquer variação fora do padrão.

**Implementação:**

```python
def detetar_anomalias_zscore(sinal, limiar_zscore=2.5):
    media  = np.mean(sinal)
    desvio = np.std(sinal)
    zscores = (sinal - media) / desvio
    indices_anomalias = np.where(np.abs(zscores) > limiar_zscore)[0]
    return indices_anomalias, zscores
```

**Efeito visual:** subplot inferior do Modo Acadêmico exibe Z-score ao longo do tempo com linhas de limiar `±λ` em vermelho tracejado. Os pontos que ultrapassam o limiar são marcados com `×` tanto no gráfico do sinal quanto no gráfico do Z-score.

---

## 7. Pipeline de Processamento

O sistema executa os 4 pilares em sequência, na ordem exata definida em `app.py`:

```
CSV → x[n]
         │
         ▼  filtro_butterworth(x[n], fc, fs, N)
      y[n] — sinal filtrado                         [Pilar 1]
         │
         ├──► calcular_derivada_discreta(y[n], fs)
         │    dy/dt — taxa de variação por hora      [Pilar 2]
         │
         ├──► analisar_espectro_fft(x[n], fs)
         │    freqs, magnitudes, periodicidades       [Pilar 3]
         │
         ├──► detetar_anomalias_zscore(x[n], λ)
         │    indices_anomalias, zscores              [Pilar 4]
         │
         ▼
    calcular_estatisticas(y[n])
    gerar_diagnostico(stats, periodicidades, n_anomalias, n_total)
         │
         ├──► Modo Fazendeiro (decisão prática)
         └──► Modo Acadêmico  (gráficos + PDF)
```

**Nota importante:** o filtro (Pilar 1) é aplicado sobre `x[n]` e produz `y[n]`. Os Pilares 2, 3 e 4 operam sobre sinais distintos:
- Pilar 2 opera sobre `y[n]` (sinal filtrado) — para que a taxa de variação não seja distorcida por ruído
- Pilar 3 opera sobre `x[n]` (sinal bruto) — para preservar a amplitude espectral original
- Pilar 4 opera sobre `x[n]` (sinal bruto) — para detectar outliers antes da filtragem

---

## 8. Módulos do Sistema

### 8.1 signal_processing.py

Motor matemático puro. Nenhuma lógica de interface — apenas processamento de sinais.

| Função | Entrada | Saída | Pilar |
|---|---|---|---|
| `calcular_fs(df)` | DataFrame | `float` — sempre 1.0 | — |
| `filtro_butterworth(sinal, cutoff, fs, ordem)` | array, float, float, int | array — y[n] | 1 |
| `calcular_derivada_discreta(sinal, fs)` | array, float | array — dy/dt | 2 |
| `analisar_espectro_fft(sinal, fs)` | array, float | (freqs, magnitudes, periodicidades) | 3 |
| `detetar_anomalias_zscore(sinal, limiar)` | array, float | (indices, zscores) | 4 |
| `calcular_estatisticas(sinal)` | array | dict com media, desvio, min, max, amplitude_total | — |

### 8.2 diagnostics.py

Função única `gerar_diagnostico(stats, periodicidades, n_anomalias, n_total)`.

Avalia três aspectos e aplica penalidades ao score de saúde:

**Nível DC — média do sinal filtrado:**
- Média < 25% → penalidade 40 pontos, alerta crítico
- Média < 35% → penalidade 15 pontos, atenção
- Média ≥ 35% → sem penalidade, nível estável

**Ciclicidade espectral — período dominante da FFT:**
- Período entre 20h e 26h → irrigação diária regular, sem penalidade
- Período entre 7h e 9h → múltiplas regas por dia, penalidade leve (5 pts)
- Fora desses intervalos → padrão inconsistente, penalidade 20 pontos

**Anomalias de amplitude — taxa de outliers pelo Z-score:**
- Taxa > 8% das amostras → penalidade 30 pontos, possível falha de hardware
- Anomalias pontuais → observação registrada, sem penalidade significativa

Score final: `max(0, 100 - penalidades)`
- Score ≥ 75 → `"ok"` — Sistema Hídrico Saudável
- Score 45–74 → `"atencao"` — Sistema Requer Atenção Operacional
- Score < 45 → `"critico"` — Intervenção Crítica Necessária

### 8.3 report.py

Função `gerar_relatorio_pdf(df, y_filtrado, derivada, freqs, magnitudes, periodicidades, zscores, indices_anomalias, diagnostico, stats)`.

Essa é a assinatura exata usada em `app.py`. A ordem dos parâmetros importa.

O PDF contém 6 seções:
1. Estatísticas descritivas do sinal discreto x[n]
2. Resultados de filtragem e derivada (Pilares 1 e 2)
3. Análise espectral — FFT (Pilar 3)
4. Anomalias de amplitude — Z-score (Pilar 4)
5. Diagnóstico automatizado com score e recomendações
6. Glossário dos pilares teóricos

### 8.4 app.py

Orquestrador da aplicação. Responsabilidades em ordem de execução:

1. Renderizar CSS e configuração visual
2. Montar sidebar (upload, cultura, parâmetros)
3. Se nenhum arquivo carregado → exibir tela de boas-vindas e parar
4. Ler e validar o CSV via `pd.read_csv()`
5. Executar os 4 pilares na sequência correta
6. Gerar estatísticas e diagnóstico
7. Renderizar Modo Fazendeiro ou Acadêmico conforme a aba ativa

---

## 9. Interface — Modo Fazendeiro

Aba `👨‍🌾 Modo Fazendeiro`. Projetada para tomada de decisão rápida sem necessidade de conhecimento técnico.

### Cartões de métricas (4 colunas)

| Cartão | Valor exibido | Origem |
|---|---|---|
| Umidade Atual do Solo | `y_filtrado[-1]` em % | Pilar 1 |
| Taxa de Variação Recente | `derivada[-1]` em %/hora | Pilar 2 |
| Status Operacional | "Ideal ✅" ou "Crítico 🚨" | Comparação y[-1] vs faixa_min |
| Padrão de Ciclo Identificado | `periodicidades[0]['periodo_horas']` em h | Pilar 3 |

### Gráfico de tendência temporal

Duas linhas sobrepostas com fundo escuro:
- Verde escuro (TX2): sinal bruto `x[n]` do sensor
- Verde claro (V0): sinal suavizado `y[n]` após o filtro

Duas linhas horizontais tracejadas de referência:
- Laranja: limiar crítico mínimo da cultura
- Ciano: capacidade de campo máxima

### Recomendações práticas (texto dinâmico)

**Caso umidade abaixo do limiar mínimo:**
```
⚠️ Ação Urgente: Irrigação Necessária Imediatamente!
O sinal suavizado indica que os níveis estão abaixo de X%.
⏱️ Autonomia Restante: estresse hídrico severo em ~Y horas.
```

**Caso umidade dentro da faixa ideal:**
```
✅ Recomendação: Níveis Hídricos em Estado Ideal.
Não há necessidade de acionamento das bombas agora.
⏱️ Próxima Rega: queda até o limite mínimo em ~Z horas.
```

**Alerta de anomalia em tempo real** — exibido se qualquer uma das últimas 5 amostras tiver `|Z| > λ`:
```
🚨 Alerta de Anomalia Abrupta: variação escalar violenta
detectada nas últimas leituras.
```

---

## 10. Interface — Modo Acadêmico

Aba `🔬 Modo Acadêmico`. Exibe os gráficos completos dos 4 pilares com título técnico em cada subplot.

### Gráfico integrado — 3 subplots com eixo X compartilhado

**Subplot superior — Pilares 1 e 4:**  
Título: *"Pilar 1: Filtro Digital IIR (Sinal Bruto x[n] vs. Filtrado y[n] via filtfilt)"*  
- Linha verde escuro: `x[n]` bruto
- Linha verde claro: `y[n]` filtrado
- Marcadores vermelhos: posições dos outliers detectados pelo Z-score

**Subplot central — Pilar 2:**  
Título: *"Pilar 2: Operador Diferencial Discreto (Derivada dy/dt por diferenças finitas)"*  
- Linha laranja: `dy/dt` ao longo do tempo
- Oscilações negativas → evapotranspiração; picos positivos → irrigação

**Subplot inferior — Pilar 4:**  
Título: *"Pilar 4: Detecção de Anomalias Escalares de Amplitude (Z-score Normalizado)"*  
- Linha roxa: Z-score ao longo do tempo
- Linhas tracejadas vermelhas: limiares `+λ` e `−λ`

### Gráfico de barras — Pilar 3

Título: *"Pilar 3: Mapeamento de Domínio Orto-Espectral via FFT"*  
- Eixo X: frequência discreta normalizada em ciclos/hora
- Eixo Y: magnitude do espectro `|X(f)|`
- Barras verdes com largura 0.003

Abaixo: listagem textual dos 3 ciclos harmônicos identificados com período em horas, frequência em c/h e amplitude relativa.

### Exportação PDF

Botão `📥 Exportar Relatório Técnico de Sinais (PDF)` que gera e baixa o documento via `report.py`.

---

## 11. Parâmetros Configuráveis

### Seção: Entrada do Sinal x[n]

Upload de arquivo CSV com colunas `timestamp` e `umidade`.

### Seção: Configuração da Cultura Agrícola

Seletor de cultura que inicializa automaticamente os sliders de limiar com valores recomendados.

### Seção: Parâmetros dos Filtros de Sinais

| Controle | Intervalo | Padrão | Pilar |
|---|---|---|---|
| Ordem do Filtro Butterworth (N) | 1 a 5 | 2 | 1 |
| Frequência de Corte fc (ciclos/hora) | 0.01 a 0.49 | 0.05 | 1 |
| Limiar de Anomalia Z-score (λ) | 1.5 a 4.0 | 2.5 | 4 |

**Guia do filtro — fc:**

| fc | Período de corte | Efeito no sinal |
|---|---|---|
| 0.02 | 50 horas | Muito restritivo — tendência geral preservada, eventos rápidos atenuados |
| 0.05 (padrão) | 20 horas | Equilíbrio — suaviza ruído, preserva ciclos de irrigação |
| 0.20 | 5 horas | Suave — ruído parcialmente presente |
| 0.49 | ~2 horas | Permissivo — quase sem filtragem |

**Guia do Z-score — λ:**

| λ | Sensibilidade | Uso recomendado |
|---|---|---|
| 1.5 | Alta | Diagnóstico preventivo — detecta desvios mínimos |
| 2.5 (padrão) | Moderada | Uso geral — detecta variações realmente abruptas |
| 3.0–4.0 | Baixa | Apenas eventos extremos — falhas severas de hardware |

---

## 12. Culturas e Faixas de Umidade

As culturas pré-configuradas definem os limiares padrão que o sistema usa para avaliar o estado do solo e gerar as recomendações do Modo Fazendeiro.

| Cultura | Limiar Crítico Mínimo | Capacidade de Campo Máxima |
|---|---|---|
| 🌽 Milho | 25% | 45% |
| 🌱 Soja | 22% | 42% |
| 🍅 Tomate | 30% | 50% |
| 🌾 Arroz Irrigado | 45% | 65% |
| 🥔 Batata | 28% | 48% |
| 🛠️ Customizado | ajuste manual | ajuste manual |

Ao selecionar uma cultura, os sliders são inicializados com esses valores. O usuário pode ajustá-los livremente para qualquer outro intervalo dentro dos limites permitidos (10–80%).

---

## 13. Relatório PDF

Gerado pelo botão no Modo Acadêmico. Estrutura completa do documento:

**Cabeçalho**  
Fundo verde escuro com título "AgroSignal — Relatório Técnico de Processamento de Sinais" e data/hora de geração.

**Seção 1 — Estatísticas Descritivas do Sinal Discreto x[n]**  
Total de amostras, média (nível DC), desvio padrão, mínimo e máximo.

**Seção 2 — Resultados de Filtragem Digital e Operação Diferencial**  
Tipo de filtro aplicado, taxa de variação máxima e mínima da derivada.

**Seção 3 — Análise Espectral no Domínio da Frequência (FFT)**  
Período e frequência da componente dominante, magnitude do pico principal.

**Seção 4 — Análise de Transições Abruptas (Z-score)**  
Total de anomalias detectadas acima do limiar.

**Seção 5 — Diagnóstico Automatizado do Sistema**  
Score de estabilidade (0–100), título do status, observações técnicas e recomendações.

**Seção 6 — Pilares Teóricos Aplicados no Sistema**  
Glossário técnico com definição de cada pilar: Sinal Discreto x[n], Filtro Butterworth IIR, Filtragem de Fase Zero, Diferenciação Discreta, Mapeamento FFT e Normalização Z-score.

---

## 14. Glossário

**Sinal Discreto x[n]**  
Sequência de amplitudes de umidade coletadas em instantes de tempo fixos (a cada hora). Representa a entrada do sistema de processamento.

**Frequência de Amostragem (fs)**  
Número de amostras por hora. Fixo em `fs = 1.0` neste sistema, correspondente ao intervalo de 1 hora entre leituras do sensor.

**Filtro IIR (Infinite Impulse Response)**  
Filtro digital com realimentação. Sua resposta a um impulso pode ser teoricamente infinita. Requer menos coeficientes que um FIR equivalente, mas precisa de cuidado para garantir estabilidade.

**Butterworth Passa-Baixa**  
Tipo de filtro com resposta em frequência maximalmente plana na banda de passagem — sem ondulações. Frequências abaixo de `fc` passam com ganho ≈ 1; frequências acima são progressivamente atenuadas.

**`filtfilt` — Fase Zero**  
Filtragem bidirecional: o sinal é filtrado para frente e depois para trás no tempo. Os atrasos de fase de cada passagem se cancelam, resultando em atraso temporal zero no sinal filtrado.

**Frequência de Corte (fc)**  
Frequência a partir da qual o filtro Butterworth começa a atenuar. Configurada em ciclos/hora. Equivale ao período `T = 1/fc` horas.

**Diferenças Finitas**  
Método numérico para aproximar derivadas contínuas em sinais discretos. Usa a diferença entre amostras consecutivas para estimar a inclinação instantânea do sinal.

**FFT (Fast Fourier Transform)**  
Algoritmo eficiente para calcular a Transformada Discreta de Fourier. Projeta o sinal do domínio do tempo para o domínio da frequência, revelando seus componentes harmônicos.

**Componente DC**  
Componente de frequência zero — corresponde à média da série temporal. Removida antes da FFT para evitar que domine o espectro e oculte os padrões periódicos.

**Espectro de Magnitude `|X(f)|`**  
Gráfico da amplitude de cada componente de frequência. Picos indicam padrões que se repetem no sinal com aquele período.

**Simetria Hermitiana**  
Propriedade do espectro de sinais reais no tempo: os coeficientes para frequências negativas são o conjugado complexo dos coeficientes positivos. Por isso apenas a metade positiva do espectro é suficiente.

**Z-score**  
Transformação linear `Z[n] = (x[n] - μ) / σ` que expressa cada amostra em desvios padrão em relação à média histórica. Adimensional — independe da escala do sinal original.

**Outlier**  
Amostra com `|Z[n]| > λ` — variação escalar que se destaca significativamente do comportamento médio do sinal. Pode indicar eventos reais (chuva, falha de irrigação) ou falhas de hardware.

**Score de Saúde**  
Indicador calculado por `diagnostics.py` com base nas saídas dos 4 pilares. Parte de 100 e desconta penalidades conforme a criticidade dos problemas detectados.

---

## 15. Limitações e Trabalhos Futuros

### Limitações atuais

**Frequência de amostragem fixa em 1 amostra/hora**  
O sistema assume `fs = 1.0` de forma fixa na função `calcular_fs()`, independentemente do intervalo real do CSV. Arquivos com intervalos diferentes (15 min, 30 min) serão lidos corretamente pelo pandas, mas os parâmetros de `fc` e os períodos da FFT serão interpretados em escala horária incorreta.

**FFT com poucos dados**  
Com menos de 48 amostras, a resolução espectral é insuficiente para distinguir ciclos próximos. Para identificar claramente o ciclo de 24h, recomenda-se pelo menos 7 dias (168 amostras).

**Sensor único**  
O sistema processa um único canal de umidade por vez. Fazendas com múltiplos sensores em diferentes pontos do terreno precisam fazer uploads separados para cada sensor.

**Dados simulados**  
Os testes foram realizados com dados de CSV gerados artificialmente para simular o comportamento de sensores reais. O sistema não foi validado com dados de sensores físicos em campo.

**Sem integração com hardware**  
O AgroSignal é uma ferramenta de análise e apoio à decisão. Não possui saída para acionamento automático de sistemas de irrigação — a decisão de ligar ou desligar a bomba ainda é manual.

### Trabalhos futuros

- Integração de modelos de previsão meteorológica ao pipeline para antecipar eventos de chuva e ajustar as recomendações
- Desenvolvimento de algoritmos adaptativos que ajustem automaticamente a ordem do filtro e os limiares com base no estágio fenológico da cultura
- Conexão direta com sensores físicos de umidade via protocolo MQTT ou API REST, eliminando a necessidade de upload manual de CSV
- Suporte a múltiplos sensores simultâneos com análise espacial da umidade por talhão
- Alertas automáticos via WhatsApp ou SMS quando o solo atingir o limiar crítico