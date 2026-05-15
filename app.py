import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =========================================================
# CONFIGURACION
# =========================================================

st.set_page_config(
    page_title="Dashboard Ejecutivo Delivery",
    page_icon="📦",
    layout="wide"
)

# =========================================================
# ESTILOS
# =========================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
}

.main {
    background-color: #0E1117;
}

h1, h2, h3, h4 {
    color: white;
}

[data-testid="metric-container"] {
    background: linear-gradient(145deg, #1b1f2a, #11151c);
    border: 1px solid #2d3748;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}

.block-container {
    padding-top: 2rem;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# GOOGLE SHEETS
# =========================================================

sheet_id = "1LXPe-ZN-Hcc9_PgrkRNVAtvIZkyk3WCT0uSFBocfvM8"

url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

df = pd.read_csv(url)

# =========================================================
# LIMPIEZA
# =========================================================

df.columns = df.columns.str.strip()

orden_meses = {
    "Enero": 1,
    "Febrero": 2,
    "Marzo": 3,
    "Abril": 4,
    "Mayo": 5,
    "Junio": 6,
    "Julio": 7,
    "Agosto": 8,
    "Septiembre": 9,
    "Octubre": 10,
    "Noviembre": 11,
    "Diciembre": 12
}

df["MES_NUM"] = df["MES"].map(orden_meses)

df = df.sort_values(by=["AÑO", "MES_NUM"])

# =========================================================
# CALCULOS
# =========================================================

df["TICKET_PROMEDIO"] = (
    df["VENTA_TOTAL"] / df["CANTIDAD_DELIVERYS"]
)

df["CRECIMIENTO_%"] = (
    df.groupby("MES")["VENTA_TOTAL"]
    .pct_change() * 100
)

# =========================================================
# TITULO
# =========================================================

st.title("📦 Dashboard Ejecutivo Delivery")
st.markdown("### Análisis Histórico de Deliverys y Ventas")

st.divider()

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("📊 Panel de Navegación")

seccion = st.sidebar.radio(
    "Selecciona una sección",
    [
        "Resumen Ejecutivo",
        "KPIs",
        "Análisis por Mes",
        "Comparación Año vs Año",
        "Rankings",
        "Insights Automáticos",
        "Forecast"
    ]
)

# =========================================================
# RESUMEN EJECUTIVO
# =========================================================

if seccion == "Resumen Ejecutivo":

    st.subheader("📌 Resumen Ejecutivo")

    st.info("""
    Durante el periodo COVID-19 (2020-2021) se registró
    un incremento importante en la demanda de deliverys
    debido al crecimiento del consumo mediante canales digitales.
    """)

    total_deliverys = int(df["CANTIDAD_DELIVERYS"].sum())
    venta_total = df["VENTA_TOTAL"].sum()
    ticket_promedio = df["TICKET_PROMEDIO"].mean()

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "📦 Deliverys",
            f"{total_deliverys:,}"
        )

    with c2:
        st.metric(
            "💰 Venta Total",
            f"S/ {venta_total:,.0f}"
        )

    with c3:
        st.metric(
            "🧾 Ticket Promedio",
            f"S/ {ticket_promedio:,.2f}"
        )

    st.divider()

    st.success("""
    El negocio presenta crecimiento histórico impulsado
    principalmente durante el periodo de pandemia,
    manteniendo posteriormente estabilidad comercial.
    """)

# =========================================================
# KPIs
# =========================================================

elif seccion == "KPIs":

    st.subheader("📊 KPIs Estratégicos")

    mejor_anio = (
        df.groupby("AÑO")["VENTA_TOTAL"]
        .sum()
        .idxmax()
    )

    mejor_mes = (
        df.loc[df["VENTA_TOTAL"].idxmax()]
    )

    crecimiento_total = (
        (
            df.iloc[-1]["VENTA_TOTAL"]
            - df.iloc[0]["VENTA_TOTAL"]
        )
        / df.iloc[0]["VENTA_TOTAL"]
    ) * 100

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric(
            "🏆 Mejor Año",
            f"{mejor_anio}"
        )

    with k2:
        st.metric(
            "🔥 Mejor Mes",
            f"{mejor_mes['MES']} {mejor_mes['AÑO']}"
        )

    with k3:
        st.metric(
            "📈 Crecimiento",
            f"{crecimiento_total:.2f}%"
        )

    with k4:
        st.metric(
            "🧾 Ticket Máximo",
            f"S/ {df['TICKET_PROMEDIO'].max():,.2f}"
        )

    st.divider()

    st.subheader("🚦 Indicador de Crecimiento")

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=crecimiento_total,
        title={'text': "Crecimiento Histórico %"},
        gauge={
            'axis': {'range': [-100, 100]},
            'bar': {'color': "green"}
        }
    ))

    fig_gauge.update_layout(
        template="plotly_dark",
        height=450
    )

    st.plotly_chart(
        fig_gauge,
        use_container_width=True
    )

# =========================================================
# ANALISIS POR MES
# =========================================================

elif seccion == "Análisis por Mes":

    st.subheader("📈 Análisis Histórico por Mes")

    mes = st.selectbox(
        "Selecciona un mes",
        sorted(
            df["MES"].unique(),
            key=lambda x: orden_meses[x]
        )
    )

    metrica = st.radio(
        "Selecciona métrica",
        [
            "CANTIDAD_DELIVERYS",
            "VENTA_TOTAL",
            "TICKET_PROMEDIO"
        ]
    )

    df_mes = df[df["MES"] == mes]

    nombres = {
        "CANTIDAD_DELIVERYS": "Deliverys",
        "VENTA_TOTAL": "Ventas",
        "TICKET_PROMEDIO": "Ticket Promedio"
    }

    st.subheader(
        f"📊 Evolución de {nombres[metrica]} - {mes}"
    )

    if metrica == "VENTA_TOTAL":

        fig = px.bar(
            df_mes,
            x="AÑO",
            y=metrica,
            text_auto=".2s"
        )

    else:

        fig = px.line(
            df_mes,
            x="AÑO",
            y=metrica,
            markers=True,
            text=df_mes[metrica].round(2)
        )

        fig.update_traces(
            textposition="top center"
        )

    fig.update_layout(
        template="plotly_dark",
        height=600,
        xaxis_title="Año",
        yaxis_title=nombres[metrica]
    )

    fig.add_vline(
        x=2020,
        line_width=2,
        line_dash="dash",
        line_color="red"
    )

    fig.add_annotation(
        x=2020,
        y=df_mes[metrica].max(),
        text="COVID",
        showarrow=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.divider()

    crecimiento = (
        df_mes["CRECIMIENTO_%"].iloc[-1]
    )

    if crecimiento > 10:

        st.success(
            f"""
            🟢 El mes de {mes}
            presenta crecimiento sólido respecto
            al año anterior.
            """
        )

    elif crecimiento > 0:

        st.warning(
            f"""
            🟡 El mes de {mes}
            presenta crecimiento moderado.
            """
        )

    else:

        st.error(
            f"""
            🔴 El mes de {mes}
            presenta desaceleración respecto
            al año anterior.
            """
        )

# =========================================================
# COMPARACION AÑO VS AÑO
# =========================================================

elif seccion == "Comparación Año vs Año":

    st.subheader("⚖️ Comparación Año vs Año")

    anios = sorted(df["AÑO"].unique())

    anio1 = st.selectbox(
        "Selecciona Año 1",
        anios,
        index=len(anios)-2
    )

    anio2 = st.selectbox(
        "Selecciona Año 2",
        anios,
        index=len(anios)-1
    )

    comparacion = df[
        df["AÑO"].isin([anio1, anio2])
    ]

    fig_compare = px.bar(
        comparacion,
        x="MES",
        y="VENTA_TOTAL",
        color="AÑO",
        barmode="group",
        text_auto=".2s"
    )

    fig_compare.update_layout(
        template="plotly_dark",
        height=600,
        xaxis_title="Mes",
        yaxis_title="Venta Total"
    )

    st.plotly_chart(
        fig_compare,
        use_container_width=True
    )

# =========================================================
# RANKINGS
# =========================================================

elif seccion == "Rankings":

    st.subheader("🏆 Rankings Ejecutivos")

    ranking_tipo = st.selectbox(
        "Selecciona Ranking",
        [
            "Top Ventas",
            "Top Deliverys",
            "Top Ticket Promedio"
        ]
    )

    if ranking_tipo == "Top Ventas":

        ranking = (
            df.sort_values(
                by="VENTA_TOTAL",
                ascending=False
            )
            [["AÑO", "MES", "VENTA_TOTAL"]]
            .head(10)
        )

    elif ranking_tipo == "Top Deliverys":

        ranking = (
            df.sort_values(
                by="CANTIDAD_DELIVERYS",
                ascending=False
            )
            [["AÑO", "MES", "CANTIDAD_DELIVERYS"]]
            .head(10)
        )

    else:

        ranking = (
            df.sort_values(
                by="TICKET_PROMEDIO",
                ascending=False
            )
            [["AÑO", "MES", "TICKET_PROMEDIO"]]
            .head(10)
        )

    st.dataframe(
        ranking,
        use_container_width=True
    )

# =========================================================
# INSIGHTS
# =========================================================

elif seccion == "Insights Automáticos":

    st.subheader("🤖 Insights Automáticos")

    mejor_anio = (
        df.groupby("AÑO")["VENTA_TOTAL"]
        .sum()
        .idxmax()
    )

    mejor_mes = (
        df.loc[df["VENTA_TOTAL"].idxmax()]
    )

    st.success(
        f"""
        📌 El mejor año histórico fue {mejor_anio}
        en términos de ventas totales.
        """
    )

    st.info(
        f"""
        📌 El mejor mes histórico fue
        {mejor_mes['MES']} {mejor_mes['AÑO']}.
        """
    )

    crecimiento_total = (
        (
            df.iloc[-1]["VENTA_TOTAL"]
            - df.iloc[0]["VENTA_TOTAL"]
        )
        / df.iloc[0]["VENTA_TOTAL"]
    ) * 100

    if crecimiento_total > 0:

        st.success(
            f"""
            📈 El negocio presenta crecimiento histórico
            acumulado de {crecimiento_total:.2f}%.
            """
        )

    else:

        st.error(
            """
            📉 El negocio presenta desaceleración
            histórica.
            """
        )

# =========================================================
# FORECAST
# =========================================================

elif seccion == "Forecast":

    st.subheader("🔮 Forecast Simple")

    forecast = (
        df.groupby("AÑO")["VENTA_TOTAL"]
        .sum()
        .reset_index()
    )

    forecast["PROYECCION"] = (
        forecast["VENTA_TOTAL"]
        .rolling(2)
        .mean()
    )

    fig_forecast = px.line(
        forecast,
        x="AÑO",
        y=["VENTA_TOTAL", "PROYECCION"],
        markers=True
    )

    fig_forecast.update_layout(
        template="plotly_dark",
        height=600,
        xaxis_title="Año",
        yaxis_title="Venta Total"
    )

    st.plotly_chart(
        fig_forecast,
        use_container_width=True
    )

# =========================================================
# TABLA
# =========================================================

st.divider()

with st.expander("📋 Ver Tabla Completa"):

    st.dataframe(
        df,
        use_container_width=True
    )

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")
st.caption("Dashboard desarrollado en Streamlit")



