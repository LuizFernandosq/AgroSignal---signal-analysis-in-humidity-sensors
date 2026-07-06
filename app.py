

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Importação direta e limpa dos motores remanescentes do AgroSignal
import signal_processing as sp
from report import gerar_relatorio_pdf
from diagnostics import gerar_diagnostico


st.set_page_config(page_title="AgroSignal", page_icon="🌿", layout="wide")


V0, V1, V2 = "#4ade80", "#22c55e", "#86efac"
BG, BG2, BD = "#080f08", "#0d1a0d", "#1e3a1e"
TX, TX2 = "#a3c9a3", "#4a7a4a"
C_SINAL, C_FIL, C_ANOM = "#4ade80", "#ffffff", "#ef4444"


st.markdown(f"""
<style>
    .stApp {{ background-color: {BG}; color: {TX}; }}
    h1, h2, h3 {{ color: {V0} !important; font-family: 'JetBrains Mono', monospace; }}
    .stTabs [data-baseweb="tab"] {{ color: {TX2} !important; font-family: 'JetBrains Mono', monospace; }}
    .stTabs [aria-selected="true"] {{ color: {V0} !important; border-bottom-color: {V0} !important; }}
</style>
""", unsafe_allow_html=True)

st.title("🌿 AgroSignal — Plataforma de Processamento de Sinais Hídricos")
st.markdown("---")


st.sidebar.header("📁 Entrada do Sinal x[n]")
arquivo_csv = st.sidebar.file_uploader("Carregar arquivo CSV (Umidade)", type=["csv"])

st.sidebar.markdown("---")
st.sidebar.header("🌾 Configuração da Cultura Agrícola")


CULTURAS_PADRAO = {
    "🌽 Milho": {"min": 25, "max": 45},
    "🌱 Soja": {"min": 22, "max": 42},
    "🍅 Tomate": {"min": 30, "max": 50},
    "🌾 Arroz Irrigado": {"min": 45, "max": 65},
    "🥔 Batata": {"min": 28, "max": 48},
    "🛠️ Customizado (Ajuste Manual)": {"min": 25, "max": 45}
}


cultura_selecionada = st.sidebar.selectbox(
    "Selecione a Cultura Alvo:",
    options=list(CULTURAS_PADRAO.keys())
)

valores_padrao = CULTURAS_PADRAO[cultura_selecionada]


faixa_min = st.sidebar.slider(
    "Limiar Crítico Mínimo (%)", 
    min_value=10, 
    max_value=40, 
    value=valores_padrao["min"]
)

faixa_max = st.sidebar.slider(
    "Capacidade de Campo Máxima (%)", 
    min_value=41, 
    max_value=80, 
    value=valores_padrao["max"]
)

st.sidebar.markdown("---")
st.sidebar.header("🎛️ Parâmetros dos Filtros de Sinais")

# Slider para o Pilar 1: Ordem do filtro Butterworth
ordem_butter = st.sidebar.slider("Ordem do Filtro Butterworth (N)", min_value=1, max_value=5, value=2)
# Frequência de corte (fc)
fc = st.sidebar.slider("Frequência de Corte (fc em ciclos/hora)", min_value=0.01, max_value=0.49, value=0.05, step=0.01)
# Slider para o Pilar 4: Limiar do Z-score
limiar_z = st.sidebar.slider("Limiar de Anomalia (Z-score)", min_value=1.5, max_value=4.0, value=2.5, step=0.1)



if arquivo_csv is None:
    st.info("💡 Por favor, faça o upload de um arquivo CSV na barra lateral para iniciar o processamento de sinais.")
    
    st.markdown("### 📋 Formato de Arquivo Esperado pelo Algoritmo:")
    st.markdown("""
    O arquivo CSV deve conter uma amostragem horária estável ($f_s = 1$ amostra/hora) com as seguintes colunas de texto plano:
    - **timestamp**: Formato `AAAA-MM-DD HH:MM:SS`
    - **umidade**: Valores contínuos da amplitude medidos em percentagem (0% a 100%).
    """)
    
    
    exemplo_df = pd.DataFrame({
        "timestamp": pd.date_range(start="2026-01-01", periods=6, freq="h"),
        "umidade": [35.2, 34.8, 34.1, 55.0, 52.3, 49.8]
    })
    st.dataframe(exemplo_df)
    st.stop()


# Lendo os dados do CSV real carregado pelo usuário
try:
    df = pd.read_csv(arquivo_csv)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    
    # Extração do vetor de amostras do sinal de entrada
    t_datas = df["timestamp"]
    x_bruto = df["umidade"].to_numpy()
    n_total = len(x_bruto)
except Exception as e:
    st.error(f"❌ Erro ao processar o arquivo CSV: {e}. Verifique as colunas e formatos de texto.")
    st.stop()


# ══════════════════════════════════════════════
# PROCESSAMENTO MATEMÁTICO (OS 4 PILARES)
# ══════════════════════════════════════════════
fs = sp.calcular_fs(df)

# Pilar 1: Filtragem IIR Butterworth Passa-Baixas
y_filtrado = sp.filtro_butterworth(x_bruto, cutoff=fc, fs=fs, ordem=ordem_butter)

# Pilar 2: Operador Diferencial Discreto (Derivada Horária)
derivada = sp.calcular_derivada_discreta(y_filtrado, fs=fs)

# Pilar 3: Análise Espectral (FFT)
freqs, magnitudes, periodicidades = sp.analisar_espectro_fft(x_bruto, fs=fs)
p0 = periodicidades[0] # Ciclo periódico dominante principal

# Pilar 4: Normalização de Amplitude (Z-score)
indices_anomalias, zscores = sp.detetar_anomalias_zscore(x_bruto, limiar_zscore=limiar_z)
n_anomalias = len(indices_anomalias)

# Estatísticas gerais do sinal filtrado
stats = sp.calcular_estatisticas(y_filtrado)
diagnostico = gerar_diagnostico(stats, periodicidades, n_anomalias, n_total)


# ══════════════════════════════════════════════
# INTERFACE GRÁFICA — MODOS DE VISUALIZAÇÃO
# ══════════════════════════════════════════════
aba_fazendeiro, aba_academica = st.tabs(["👨‍🌾 Modo Fazendeiro", "🔬 Modo Acadêmico"])

# ──────────────────────────────────────────────
# ABA 1: MODO FAZENDEIRO
# ──────────────────────────────────────────────
with aba_fazendeiro:
    st.subheader(f"Dashboard Prático de Campo — Cultura Selecionada: {cultura_selecionada}")
    
    # Cartões informativos simplificados para tomada de decisão rápida
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Umidade Atual do Solo", f"{y_filtrado[-1]:.1f}%")
    with c2:
        taxa_queda = derivada[-1]
        st.metric("Taxa de Variação Recente", f"{taxa_queda:.2f}% / hora")
    with c3:
        status_sinal = "Crítico 🚨" if y_filtrado[-1] < faixa_min else "Ideal ✅"
        st.metric("Status Operacional", status_sinal)
    with c4:
        st.metric("Padrão de Ciclo Identificado", f"{p0['periodo_horas']:.1f}h")

    st.markdown("---")
    
    col_esquerda, col_direita = st.columns([2, 1])
    
    with col_esquerda:
        st.markdown("### 📈 Tendência Temporal da Umidade do Solo")
        fig_faz = go.Figure()
        fig_faz.add_trace(go.Scatter(x=t_datas, y=x_bruto, name="Leitura Bruta do Sensor", line=dict(color=TX2, width=1)))
        fig_faz.add_trace(go.Scatter(x=t_datas, y=y_filtrado, name="Curva Suavizada (Sem Ruído)", line=dict(color=V0, width=3)))
        
        # Linhas de referência de limites ideais da cultura escolhida
        fig_faz.add_hline(y=faixa_min, line_dash="dash", line_color="orange", annotation_text="Limiar Mínimo Recomendado")
        fig_faz.add_hline(y=faixa_max, line_dash="dash", line_color="cyan", annotation_text="Capacidade Máxima de Retenção")
        
        fig_faz.update_layout(template="plotly_dark", paper_bgcolor=BG, plot_bgcolor=BG2, height=400)
        st.plotly_chart(fig_faz, use_container_width=True)

    with col_direita:
        st.markdown("### ⚙️ Instruções e Recomendações Práticas")
        
        
        umidade_atual = y_filtrado[-1]
        if umidade_atual < faixa_min:
            st.warning("⚠️ **Ação Urgente: Irrigação Necessária Imediatamente!**")
            st.write(f"O sinal suavizado indica que os níveis de água estão abaixo da meta de {faixa_min}% estipulada para esta cultura.")
            if taxa_queda < 0:
                horas_restantes = max(0.0, (umidade_atual - (faixa_min*0.8)) / abs(taxa_queda))
                st.write(f"⏱️ **Autonomia Restante:** O solo entrará em estresse hídrico severo em aproximadamente {horas_restantes:.1f} horas.")
        else:
            st.success("✅ **Recomendação: Níveis Hídricos em Estado Ideal.**")
            st.write("Não há necessidade operacional de acionamento das bombas neste momento.")
            if taxa_queda < 0:
                horas_ate_limiar = (umidade_atual - faixa_min) / abs(taxa_queda)
                st.write(f"⏱️ **Próxima Rega:** Estimativa de queda até o limite mínimo em aproximadamente {horas_ate_limiar:.1f} horas.")

        # Alerta em tempo real do pilar 4 (Z-score)
        if any(np.abs(zscores[-5:]) > limiar_z):
            st.error("🚨 **Alerta de Anomalia Abrupta:** Variação escalar violenta detectada nas últimas leituras. Verifique possíveis quebras de cano ou falhas mecânicas!")


# ──────────────────────────────────────────────
# ABA 2: MODO ACADÊMICO
# ──────────────────────────────────────────────
with aba_academica:
    st.subheader("🔬 Análise Computacional de Sinais (Domínio do Tempo e Frequência)")
    
    # Painel integrado mostrando os Pilares 1, 2 e 4 de forma gráfica sequencial
    fig_acad = make_subplots(rows=3, cols=1, shared_xaxes=True,
                             subplot_titles=("Pilar 1: Filtro Digital IIR (Sinal Bruto x[n] vs. Filtrado y[n] via filtfilt)", 
                                             "Pilar 2: Operador Diferencial Discreto (Derivada dy/dt por diferenças finitas)", 
                                             "Pilar 4: Detecção de Anomalias Escalares de Amplitude (Z-score Normalizado)"))
    
    # Subplot do Pilar 1 (Filtro) + Marcadores do Pilar 4
    fig_acad.add_trace(go.Scatter(x=t_datas, y=x_bruto, name="x[n] Bruto", line=dict(color=TX2, width=1)), row=1, col=1)
    fig_acad.add_trace(go.Scatter(x=t_datas, y=y_filtrado, name="y[n] Filtrado", line=dict(color=V0, width=2)), row=1, col=1)
    if n_anomalias > 0:
        fig_acad.add_trace(go.Scatter(x=t_datas[indices_anomalias], y=x_bruto[indices_anomalias],
                                     mode="markers", name="Outliers Detectados", marker=dict(color=C_ANOM, size=6)), row=1, col=1)

    # Subplot do Pilar 2 (Derivada Discreta)
    fig_acad.add_trace(go.Scatter(x=t_datas, y=derivada, name="Taxa dy/dt", line=dict(color="#fb923c", width=1.5)), row=2, col=1)
    
    # Subplot do Pilar 4 (Z-score)
    fig_acad.add_trace(go.Scatter(x=t_datas, y=zscores, name="Z-score Adimensional", line=dict(color="#818cf8", width=1.5)), row=3, col=1)
    fig_acad.add_hline(y=limiar_z, line_dash="dot", line_color=C_ANOM, row=3, col=1)
    fig_acad.add_hline(y=-limiar_z, line_dash="dot", line_color=C_ANOM, row=3, col=1)
    
    fig_acad.update_layout(template="plotly_dark", paper_bgcolor=BG, plot_bgcolor=BG2, height=700, showlegend=True)
    st.plotly_chart(fig_acad, use_container_width=True)
    
    st.markdown("---")
    
    # Subplot do Pilar 3 (FFT)
    st.markdown("### Pilar 3: Mapeamento de Domínio Orto-Espectral via FFT")
    
    fig_fft = go.Figure()
    fig_fft.add_trace(go.Bar(x=freqs, y=magnitudes, name="Magnitude do Espectro |X(f)|", marker_color=V0, width=0.003))
    
    fig_fft.update_layout(
        template="plotly_dark", paper_bgcolor=BG, plot_bgcolor=BG2, height=350,
        xaxis_title="Frequência Discreta Normalizada (ciclos / hora)",
        yaxis_title="Magnitude do Espectro |X(f)|"
    )
    st.plotly_chart(fig_fft, use_container_width=True)
    
    # Detalhes textuais das componentes de frequência para defender no quadro
    st.markdown(f"**Componentes Harmônicas Identificadas no Espectro de Frequência:**")
    for i, p in enumerate(periodicidades[:3]):
        if p['periodo_horas'] > 0:
            st.markdown(f"- **Componente {i+1}:** Ciclo Periódico de **{p['periodo_horas']:.1f} horas** (Frequência: {p['frequencia']:.4f} c/h · Amplitude Relativa: {p['amplitude']:.2f}%)")

    # Botão de Exportação do PDF de Engenharia
    st.markdown("---")
    try:
        pdf_bytes = gerar_relatorio_pdf(df, y_filtrado, derivada, freqs, magnitudes, periodicidades, zscores, indices_anomalias, diagnostico, stats)
        st.download_button(label="📥 Exportar Relatório Técnico de Sinais (PDF)", data=pdf_bytes, file_name="relatorio_agrosignal.pdf", mime="application/pdf")
    except Exception as e:
        st.caption(f"Aguardando sincronização de variáveis para renderização do PDF: {e}")
