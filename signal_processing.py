"""
signal_processing.py — AgroSignal
Motor purificado de processamento focado estritamente em 4 pilares de Sinais e Sistemas.

Pilares implementados:
  1. Filtro Digital IIR (Butterworth Passa-Baixas com Fase Zero via filtfilt)
  2. Operador Diferencial Discreto (Derivada Horária por diferenças finitas)
  3. Análise Espectral (FFT para mapeamento do domínio do tempo para frequência)
  4. Normalização de Amplitude (Z-score para detecção escalar de anomalias)
"""

import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt
from scipy.fft import fft, fftfreq


# ─────────────────────────────────────────────
# 1. TAXA DE AMOSTRAGEM FIXED
# ─────────────────────────────────────────────

def calcular_fs(df: pd.DataFrame) -> float:
    """
    Define a frequência de amostragem fs (amostras por hora).
    Como o sistema trabalha com amostragem horária estável na leitura do CSV,
    a taxa de amostragem do sinal discreto x[n] é de 1 amostra/hora.
    """
    return 1.0


# ─────────────────────────────────────────────
# PILAR 1: FILTRO DIGITAL IIR (BUTTERWORTH)
# ─────────────────────────────────────────────

def filtro_butterworth(sinal: np.ndarray, cutoff: float, fs: float, ordem: int = 2) -> np.ndarray:
    """
    Aplica um Filtro Digital Passa-Baixas do tipo IIR (Butterworth).
    
    Propriedades matemáticas defendidas na banca:
      - Resposta em frequência maximalmente plana na banda de passagem.
      - Atenuação contínua e acentuada de altas frequências (ruídos do sensor).
      - Uso da função 'filtfilt' (filtragem bidirecional) que elimina o deslocamento
        de fase, garantindo um atraso temporal estritamente igual a zero.
    """
    # Normalização da frequência de corte em relação à frequência de Nyquist (fs/2)
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    
    # Restrição de segurança para evitar instabilidade numérica do filtro
    if normal_cutoff >= 1.0:
        normal_cutoff = 0.99
    elif normal_cutoff <= 0.0:
        normal_cutoff = 0.01

    # Cálculo dos coeficientes do filtro IIR (b: numerador, a: denominador)
    b, a = butter(ordem, normal_cutoff, btype='low', analog=False)
    
    # Filtragem de fase zero (Forward-Backward filtering)
    sinal_filtrado = filtfilt(b, a, sinal)
    return sinal_filtrado


# ─────────────────────────────────────────────
# PILAR 2: OPERADOR DIFERENCIAL DISCRETO (DERIVADA)
# ─────────────────────────────────────────────

def calcular_derivada_discreta(sinal: np.ndarray, fs: float) -> np.ndarray:
    """
    Aplica o operador de diferenciação discreta sobre o sinal temporal.
    
    Propriedade matemática:
      - Utiliza o método de aproximação por diferenças finitas para estimar a 
        taxa de variação temporal instantânea (inclinação local dy/dt) do sinal.
        Como dt = 1/fs e fs = 1, a diferença finita é calculada diretamente amostra a amostra.
    """
    dt = 1.0 / fs
    derivada = np.zeros_like(sinal)
    
    # Diferença finita avançada para o primeiro ponto
    derivada[0] = (sinal[1] - sinal[0]) / dt
    
    # Diferença finita central para os pontos intermediários (menor erro numérico)
    for n in range(1, len(sinal) - 1):
        derivada[n] = (sinal[n+1] - sinal[n-1]) / (2 * dt)
        
    # Diferença finita atrasada para o último ponto
    derivada[-1] = (sinal[-1] - sinal[-2]) / dt
    
    return derivada


# ─────────────────────────────────────────────
# PILAR 3: ANÁLISE ESPECTRAL (FFT)
# ─────────────────────────────────────────────

def analisar_espectro_fft(sinal: np.ndarray, fs: float) -> tuple:
    """
    Aplica a Transformada Rápida de Fourier (FFT) para mapeamento de domínio.
    
    Propriedade matemática:
      - Projeta o sinal do domínio do tempo discreto para o domínio da frequência discreta.
      - Retorna apenas a metade positiva do espectro devido à simetria hermitiana 
        de sinais puramente reais no tempo.
    """
    n_amostras = len(sinal)
    
    # Remoção do nível DC (média) para evitar um pico gigante na frequência zero (0 Hz)
    sinal_centralizado = sinal - np.mean(sinal)
    
    # Execução do algoritmo da FFT e cálculo do vetor de frequências correspondentes
    fft_valores = fft(sinal_centralizado)
    frequencias_completas = fftfreq(n_amostras, d=(1.0 / fs))
    
    # Seleção apenas das frequências positivas (primeira metade do vetor)
    metade = n_amostras // 2
    freqs = frequencias_completas[:metade]
    
    # Cálculo da magnitude normalizada do espectro de amplitude
    magnitudes = (2.0 / n_amostras) * np.abs(fft_valores[:metade])
    
    # Extração das periodicidades dominantes encontradas no espectro
    periodicidades = []
    if len(magnitudes) > 1:
        # Ignora a frequência estritamente zero e encontra os picos mais altos
        indices_ordenados = np.argsort(magnitudes[1:])[::-1] + 1
        
        for idx in indices_ordenados[:3]: # Captura os 3 principais padrões cíclicos
            f_dom = freqs[idx]
            if f_dom > 1e-5:
                periodo_horas = 1.0 / f_dom
                periodicidades.append({
                    "frequencia": float(f_dom),
                    "periodo_horas": float(periodo_horas),
                    "periodo_dias": float(periodo_horas / 24.0),
                    "amplitude": float(magnitudes[idx])
                })
                
    # Caso nenhuma componente periódica clara seja detetada
    if not periodicidades:
        periodicidades.append({
            "frequencia": 0.0, "periodo_horas": 0.0, "periodo_dias": 0.0, "amplitude": 0.0
        })
        
    return freqs, magnitudes, periodicidades


# ─────────────────────────────────────────────
# PILAR 4: NORMALIZAÇÃO DE AMPLITUDE (Z-SCORE)
# ─────────────────────────────────────────────

def detetar_anomalias_zscore(sinal: np.ndarray, limiar_zscore: float = 2.5) -> tuple:
    """
    Aplica uma normalização linear de amplitude baseada em desvios padrão.
    
    Propriedade matemática:
      - Transforma o sinal em uma escala adimensional indexada por desvios padrão (Z).
      - Mapeia amostras cujas variações escalares absolutas excedem o limiar fixado, 
        sinalizando transições abruptas ou outliers de amplitude no histórico do sinal.
    """
    media = np.mean(sinal)
    desvio = np.std(sinal)

    # Proteção matemática contra divisão por zero em sinais perfeitamente constantes
    if desvio < 1e-10:
        return np.array([]), np.zeros(len(sinal))

    # Equação clássica de normalização linear do sinal
    zscores = (sinal - media) / desvio
    
    # Filtro de limiar geométrico para mapear os índices das anomalias
    indices_anomalias = np.where(np.abs(zscores) > limiar_zscore)[0]

    return indices_anomalias, zscores


# ─────────────────────────────────────────────
# FUNÇÃO AUXILIAR: ESTATÍSTICAS GERAIS
# ─────────────────────────────────────────────

def calcular_estatisticas(sinal: np.ndarray) -> dict:
    """
    Calcula métricas estatísticas descritivas básicas da amplitude do sinal.
    Na teoria de sinais, a média representa o valor DC (componente contínua) 
    e o desvio padrão correlaciona-se com a potência AC do sinal temporal.
    """
    return {
        "media": float(np.mean(sinal)),
        "mediana": float(np.median(sinal)),
        "desvio_padrao": float(np.std(sinal)),
        "minimo": float(np.min(sinal)),
        "maximo": float(np.max(sinal)),
        "amplitude_total": float(np.max(sinal) - np.min(sinal))
    }