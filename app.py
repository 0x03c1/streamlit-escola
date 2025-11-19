import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Escola Sustentável do Futuro", layout="wide")

st.markdown("""
<style>
    .big-font {font-size:50px !important; font-weight:bold; text-align:center;}
    .metric-good {color:#00f000;}
    .metric-warning {color:#ffaa00;}
    .metric-bad {color:#ff0000;}
</style>
""", unsafe_allow_html=True)

st.title("Escola Sustentável do Futuro")
st.markdown("**Pensamento Computacional Interdisciplinar**")

with st.sidebar:
    st.image("https://www2.recife.pe.gov.br/sites/default/files/escola_futuro_700x400_0.png", use_container_width=True)
    st.header("Parâmetros Ajustáveis")

    salas = st.slider("Salas de aula convencionais", 12, 28, 12, 1)
    area_maker_horta = st.slider("Área Maker + Horta (m²)", 300, 1200, 400, 50)
    area_quadra = st.slider("Quadra esportiva (m²)", 600, 1000, 600, 50)
    eficiencia_painel = st.slider("Eficiência dos painéis solares (%)", 18.0, 26.0, 22.0, 0.5)
    preco_kwp = st.slider("Preço do kWp instalado (R$)", 3500, 5500, 4000, 100)
    orcamento_inicial = st.number_input("Orçamento inicial da prefeitura (R$ milhões)", 1.0, 10.0, 7.0, 0.1) * 1_000_000
    meses_obra = st.slider("Prazo da obra (meses)", 12, 24, 20, 1)

area_total_terreno = 8000  # m²

area_salas = salas * 45
area_fixa = area_quadra + 300 + 400  # quadra + biblioteca + admin
area_usada = area_salas + area_maker_horta + area_fixa
area_circulacao = area_total_terreno - area_usada * 1.35  # 35% de circulação/ampliação
viavel_pedagogia = area_circulacao >= 800
score_pedagogia = min(area_circulacao / 800, 1.0)

consumo_anual_kwh = 18 * area_usada  # 18 kWh/m².ano (escola eficiente)
irradiacao_media = 5.2  # kWh/m².dia (média Brasil)
perda_sistema = 0.85
potencia_kw = consumo_anual_kwh / (365 * irradiacao_media * (eficiencia_painel/100) * perda_sistema)
custo_solar = potencia_kw * preco_kwp
viavel_eletrica = potencia_kw <= 120  # limite realista de cobertura
score_eletrica = min(120 / potencia_kw, 1.0) if potencia_kw > 0 else 0

concreto_m3 = area_usada * 0.28
aco_kg = area_usada * 85
custo_civil = concreto_m3 * 480 + aco_kg * 6.8 + 1_200_000  # inclui fundação

custo_total = 4_450_000 + custo_civil + custo_solar + 200_000  # base + civil + solar + contingência
saldo_inicial = orcamento_inicial
custo_mensal = (custo_total - saldo_inicial) / meses_obra if meses_obra > 0 else 0
viavel_financeira = custo_total <= 8_000_000 and custo_mensal >= 0
score_financeiro = min(8_000_000 / custo_total, 1.0)

projeto_aprovado = viavel_pedagogia and viavel_eletrica and viavel_financeira and custo_total <= 8_000_000

col1, col2, col3, col4 = st.columns(4)


def gauge(score, title, invert=False):
    cor = "green" if (score >= 0.9 if not invert else score <= 0.4) else \
          "orange" if (score >= 0.6 if not invert else score <= 0.7) else "red"
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score*100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 18}},
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': cor},
               'steps': [{'range': [0, 60], 'color': "lightgray"},
                         {'range': [60, 90], 'color': "yellow"},
                         {'range': [90, 100], 'color': "lightgreen"}],
               'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 90}}))
    fig.update_layout(height=250, margin=dict(t=50, b=0, l=10, r=10))
    return fig


with col1:
    st.plotly_chart(gauge(score_pedagogia, "Pedagogia"), use_container_width=True)
with col2:
    st.plotly_chart(gauge(score_eletrica, "Energia Solar", invert=True), use_container_width=True)
with col3:
    st.plotly_chart(gauge(score_financeiro, "Orçamento", invert=True), use_container_width=True)
with col4:
    viab_geral = 1.0 if projeto_aprovado else 0.3
    fig = gauge(viab_geral, "Projeto Geral")
    fig.update_traces(gauge={'bar': {'color': "green" if projeto_aprovado else "red"}})
    st.plotly_chart(fig, use_container_width=True)

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["Pedagogia", "Elétrica", "Civil", "Administração"])

with tab1:
    st.subheader("Distribuição de Áreas")
    df_ped = pd.DataFrame({
        "Área": ["Salas de aula", "Maker + Horta",
                 "Quadra", "Biblioteca + Admin",
                 "Circulação/Ampliação", "Total Usado"],
        "m²": [area_salas, area_maker_horta, area_quadra, 700,
               max(area_circulacao, 0),
               area_usada + max(area_circulacao, 0)],
        "Status": ["OK", "OK", "OK", "OK",
                   "Excelente" if area_circulacao>=1200 else "Regular" if area_circulacao>=800 else "Insuficiente", 
              "Viável" if viavel_pedagogia else "Revisar"]
    })
    st.table(df_ped.style.format({"m²": "{:.0f}"}))

with tab2:
    st.write(f"**Consumo estimado:** {consumo_anual_kwh:,.0f} kWh/ano")
    st.write(f"**Potência necessária:** {potencia_kw:.1f} kWp")
    st.write(f"**Custo do sistema solar:** R$ {custo_solar:,.0f}")
    st.write(f"**Área aproximada de painéis:** {potencia_kw * 5.5:.0f} m²")
    if potencia_kw > 120:
        st.error("Potência muito alta — difícil cobrir todo o telhado")

with tab3:
    st.write(f"Concreto armado: {concreto_m3:,.0f} m³")
    st.write(f"Aço CA-50/60: {aco_kg:,.0f} kg")
    st.write(f"Custo estimado da estrutura: R$ {custo_civil:,.0f}")

with tab4:
    df_fluxo = pd.DataFrame({
        "Mês": range(1, meses_obra+1),
        "Desembolso mensal": [custo_mensal] * meses_obra,
        "Saldo acumulado": [max(saldo_inicial - custo_mensal * i, 0) for i in range(1, meses_obra+1)]
    })
    st.write(f"**Custo total do projeto:** R$ {custo_total:,.0f}")
    st.write(f"**Dentro do orçamento (R$ 8M)?** {'SIM' if custo_total <= 8_000_000 else 'NÃO'}")
    st.line_chart(df_fluxo.set_index("Mês")["Saldo acumulado"],
                  use_container_width=True)

st.divider()

if projeto_aprovado:
    st.balloons()
    st.success("PROJETO APROVADO PELA PREFEITURA! Todos os indicadores verdes!")
    st.markdown("<p class='big-font'>Escola Sustentável VIÁVEL!</p>", unsafe_allow_html=True)
else:
    st.info("Ajuste os parâmetros até todos os gauges ficarem verdes!")

st.caption("Desenvolvido em aula de Pensamento Computacional com Python")
