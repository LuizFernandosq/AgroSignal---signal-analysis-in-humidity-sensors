"""
diagnostics.py — AgroSignal
Gera diagnósticos e recomendações automáticas a partir dos resultados purificados dos 4 pilares.
"""

import numpy as np

def gerar_diagnostico(stats: dict, periodicidades: list, n_anomalias: int, n_total: int) -> dict:
    """
    Analisa os outputs matemáticos (médias, harmónicas e anomalias de Z-score)
    e extrai um diagnóstico focado em engenharia de sinais.
    """
    diagnosticos = []
    recomendacoes = []
    penalidade = 0

    media = stats["media"]
    taxa_anomalias = n_anomalias / max(n_total, 1)
    p0 = periodicidades[0] if len(periodicidades) > 0 else {"periodo_horas": 0}

    # ── 1. Análise do Nível DC (Média de Amplitude) ──────────────────
    if media < 25:
        diagnosticos.append(f"🏜️ Componente DC (Média) Crítica ({media:.1f}%) — Solo em stress severo.")
        recomendacoes.append("Iniciar irrigação de emergência para elevar o nível contínuo do sinal.")
        penalidade += 40
    elif media < 35:
        diagnosticos.append(f"⚠️ Nível médio baixo ({media:.1f}%) — Solo próximo do limite inferior.")
        recomendacoes.append("Agendar um ciclo hídrico preventivo.")
        penalidade += 15
    else:
        diagnosticos.append(f"✅ Nível contínuo estável ({media:.1f}%) — Amplitude média ideal.")

    # ── 2. Análise Espectral (FFT) ──────────────────────────────────
    per = p0.get("periodo_horas", 0)
    if 20 <= per <= 26:
        diagnosticos.append(f"🔄 Ciclicidade Dominante Estável: Detetado período harmónico de {per:.1f}h (Rega Diária).")
        recomendacoes.append("Manter o padrão de automação diária observado na análise espectral.")
    elif 7 <= per <= 9:
        diagnosticos.append(f"🔄 Frequência de Alta Periodicidade: Detetado ciclo de {per:.1f}h (Múltiplas regas por dia).")
        penalidade += 5
    else:
        diagnosticos.append("⚠️ Ausência de Espectro Harmónico Dominante: Comportamento cíclico inconsistente ou caótico.")
        recomendacoes.append("Revisar os temporizadores do sistema para restabelecer um padrão estável de rega.")
        penalidade += 20

    # ── 3. Análise de Transições e Outliers (Z-score) ───────────────
    if taxa_anomalias > 0.08:
        diagnosticos.append(f"🚨 Elevada taxa de transições abruptas ({taxa_anomalias*100:.1f}% das amostras) — Possível falha de hardware.")
        recomendacoes.append("Inspecionar o sensor de humidade física com urgência devido a ruído espúrio ou mau contacto.")
        penalidade += 30
    elif n_anomalias > 0:
        diagnosticos.append(f"ℹ️ Outliers detetados pelo Z-score ({n_anomalias} amostras) — Eventos transientes isolados (ex: picos de chuva).")
        recomendacoes.append("Monitorizar o comportamento das variações de amplitude nas próximas horas.")

    # ── 4. Cálculo do Score de Saúde ─────────────────────────────────
    score = max(0, 100 - penalidade)

    if score >= 75:
        status = "ok"
        titulo = "Sistema Hídrico Saudável"
    elif score >= 45:
        status = "atencao"
        titulo = "Sistema Requer Atenção Operacional"
    else:
        status = "critico"
        titulo = "Intervenção Crítica Necessária"

    if not recomendacoes:
        recomendacoes.append("Continuar com o monitoramento regular do sinal temporal.")

    return {
        "status": status,
        "titulo": titulo,
        "diagnosticos": diagnosticos,
        "recomendacoes": recomendacoes,
        "score_saude": score
    }