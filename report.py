"""
report.py — AgroSignal
Gera o relatório técnico em PDF perfeitamente sincronizado com os parâmetros do app.py.
"""

from fpdf import FPDF
from datetime import datetime
import numpy as np

def _s(text: str) -> str:
    """Sanitiza strings removendo acentos incompatíveis com o PDF padrão."""
    replacements = {
        "ã": "a", "õ": "o", "é": "e", "ç": "c", "á": "a", "à": "a",
        "ê": "e", "í": "i", "ó": "o", "ú": "u", "📊": "", "🌿": "",
        "🚨": "!", "⚠️": "/!", "✅": "OK", "🏜️": "", "🔄": "", "ℹ️": "", "⏱️": ""
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode('latin-1', 'replace').decode('latin-1')

class PDFReport(FPDF):
    def header(self):
        self.set_fill_color(8, 15, 8) # Dark background para o header
        self.rect(0, 0, 210, 25, "F")
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(74, 222, 128) # Verde AgroSignal
        self.cell(0, 10, _s("🌿 AgroSignal — Relatório Técnico de Processamento de Sinais"), 0, 1, "L")
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(163, 201, 163)
        self.cell(0, 5, _s(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"), 0, 1, "L")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Página {self.page_no()}", 0, 0, "C")

    def secao(self, titulo):
        self.ln(4)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(34, 197, 94)
        self.cell(0, 6, _s(titulo), 0, 1, "L")
        self.set_draw_color(30, 58, 30)
        self.line(self.get_x(), self.get_y(), self.get_x() + 190, self.get_y())
        self.ln(3)

    def item(self, txt, marcador="-"):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(40, 40, 40)
        self.cell(8, 5, marcador, 0, 0, "C")
        self.multi_cell(0, 5, _s(txt), new_x="LMARGIN", new_y="NEXT")

def gerar_relatorio_pdf(df, y_filtrado, derivada, freqs, magnitudes, periodicidades, zscores, indices_anomalias, diagnostico, stats):
    """
    Função principal chamada pelo app.py. 
    Assinatura e ordem de parâmetros 100% sincronizadas.
    """
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_auto_page_break(True, margin=15)
    
    # 1. Resumo dos Dados Reais
    pdf.secao("1. Estatísticas Descritivas do Sinal Discreto x[n]")
    pdf.item(f"Total de Amostras Processadas: {len(df)} pontos horários.")
    pdf.item(f"Valor Médio da Amplitude (Nível DC): {stats['media']:.2f}%")
    pdf.item(f"Variação Escalar (Desvio Padrão): {stats['desvio_padrao']:.2f}%")
    pdf.item(f"Amplitude Mínima Registrada: {stats['minimo']:.2f}%")
    pdf.item(f"Amplitude Máxima Registrada: {stats['maximo']:.2f}%")

    # 2. Pilar 1 e 2
    pdf.secao("2. Resultados de Filtragem Digital e Operação Diferencial")
    pdf.item("Filtro Digital Aplicado: IIR Butterworth Passa-Baixas com Fase Zero via filtfilt.")
    pdf.item(f"Taxa de Variação Temporal Máxima (Derivada Discreta): {np.max(derivada):.3f}%/h")
    pdf.item(f"Taxa de Variação Temporal Mínima (Derivada Discreta): {np.min(derivada):.3f}%/h")

    # 3. Pilar 3 (FFT)
    pdf.secao("3. Análise Espectral no Domínio da Frequência (FFT)")
    p0 = periodicidades[0] if len(periodicidades) > 0 else {"periodo_horas": 0, "frequencia": 0, "amplitude": 0}
    if p0["periodo_horas"] > 0:
        pdf.item(f"Componente Harmônica Dominante: Período de {p0['periodo_horas']:.1f} horas.")
        pdf.item(f"Frequência Discreta Correspondente: {p0['frequencia']:.4f} ciclos/hora.")
        pdf.item(f"Magnitude Relativa do Pico: {p0['amplitude']:.2f}%")
    else:
        pdf.item("Nenhum ciclo periódico dominante detectado acima do patamar de ruído.")

    # 4. Pilar 4 (Z-score)
    pdf.secao("4. Análise de Transições Abruptas (Z-score)")
    pdf.item(f"Total de Anomalias de Amplitude Detectadas: {len(indices_anomalias)} amostras fora do limiar geométrico.")
    
    # 5. Diagnóstico Final
    pdf.secao("5. Diagnóstico Automatizado do Sistema")
    pdf.item(f"Score de Estabilidade Hídrica: {diagnostico['score_saude']}/100 ({diagnostico['titulo']})")
    
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 5, "Observações Técnicas:", new_x="LMARGIN", new_y="NEXT")
    for obs in diagnostico["diagnosticos"]:
        pdf.item(obs, "-")

    pdf.ln(2)
    pdf.cell(0, 5, "Ações e Recomendações Sugeridas:", new_x="LMARGIN", new_y="NEXT")
    for rec in diagnostico["recomendacoes"]:
        pdf.item(rec, ">")

    # 6. Conceitos Teóricos para Defesa na Banca
    pdf.secao("6. Pilares Teóricos Aplicados no Sistema")
    conceitos = [
        ("Sinal Discreto x[n]", "Sequência de amplitudes hídricas amostradas a uma taxa fixa fs = 1 amostra/hora."),
        ("Filtro Butterworth IIR", "Atenua altas frequências (ruídos do sensor) preservando ganho unitário na banda de passagem."),
        ("Filtragem de Fase Zero", "Processamento de sinal bidirecional (direto e reverso) para eliminar atraso temporal."),
        ("Diferenciação Discreta", "Estimativa da inclinação instantânea baseada na aproximação estável por diferenças finitas."),
        ("Mapeamento FFT", "Algoritmo de Transformada Rápida de Fourier para projeção ortogonal do sinal para o domínio da frequência."),
        ("Normalização Z-score", "Métrica adimensional estatística que mapeia transições abruptas fora do desvio padrão.")
    ]
    for nome, desc in conceitos:
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(45, 5, _s(nome + ": "), 0, 0, "L")
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 5, _s(desc), new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())