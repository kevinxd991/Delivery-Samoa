import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =========================================================
# CONFIGURACION PAGINA
# =========================================================

st.set_page_config(
    page_title="Dashboard Ejecutivo Delivery",
    page_icon="📦",
    layout="wide"
)

# =========================================================
# ESTILOS PREMIUM
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

.stAlert {
    border-radius: 15px;
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
st.markdown("### Análisis histórico de ventas y deliverys")

st.divider()

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("📊 Configuración")

modo = st.sidebar.radio(
    "Modo de Visualización",
    [
        "Vista General",
        "Análisis por Mes"
    ]
)

# =========================================================
# KPIs
# =========================================================

st.subheader("📌 KPIs Principales")

total_deliverys = int(df["CANTIDAD_DELIVERYS"].sum())

venta_total = df["VENTA_TOTAL"].sum()

ticket_promedio = df["TICKET_PROMEDIO"].mean()

mejor_anio = (
    df.groupby("AÑO")["VENTA_TOTAL"]
    .sum()
    .idxmax()
)

mejor_mes = (
    df.loc[df["VENTA_TOTAL"].idxmax()]
)

crecimiento_total = (
    (df.iloc[-1]["VENTA_TOTAL"] - df.iloc[0]["VENTA_TOTAL"])
    / df.iloc[0]["VENTA_TOTAL"]
) * 100

c1, c2, c3, c4, c5, c6 = st.columns(6)

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

with c4:
    st.metric(
        "🏆 Mejor Año",
        f"{mejor_anio}"
    )

with c5:
    st.metric(
        "🔥 Mejor Mes",
        f"{mejor_mes['MES']} {mejor_mes['AÑO']}"
    )

with c6:
    st.metric(
        "📈 Crecimiento",
        f"{crecimiento_total:.2f}%"
    )

st.divider()

# =========================================================
# HALLAZGOS
# =========================================================

st.subheader("📌 Hallazgos Clave")

st.info(
    """
Durante el periodo COVID-19 (2020-2021) se observa un incremento
significativo en la demanda de deliverys y ventas debido a las
restricciones de movilidad y el crecimiento del consumo mediante delivery.
"""
)

# =========================================================
# TOP 3 AÑOS
# =========================================================

st.subheader("🏆 Top 3 Mejores Años")

top_anios = (
    df.groupby("AÑO")["VENTA_TOTAL"]
    .sum()
    .sort_values(ascending=False)
    .head(3)
)

ranking = list(top_anios.items())

medallas = ["🥇", "🥈", "🥉"]

col1, col2, col3 = st.columns(3)

for i, col in enumerate([col1, col2, col3]):
    with col:
        st.metric(
            f"{medallas[i]} Año {ranking[i][0]}",
            f"S/ {ranking[i][1]:,.0f}"
        )

st.divider()

# =========================================================
# COMPARACION COVID
# =========================================================

st.subheader("🦠 Comparación Pre-COVID / COVID / Post-COVID")

pre_covid = df[df["AÑO"].isin([2018, 2019])]
covid = df[df["AÑO"].isin([2020, 2021])]
post_covid = df[df["AÑO"] >= 2022]

comparacion = pd.DataFrame({
    "Periodo": [
        "Pre COVID",
        "COVID",
        "Post COVID"
    ],
    "Venta Promedio": [
        pre_covid["VENTA_TOTAL"].mean(),
        covid["VENTA_TOTAL"].mean(),
        post_covid["VENTA_TOTAL"].mean()
    ],
    "Deliverys Promedio": [
        pre_covid["CANTIDAD_DELIVERYS"].mean(),
        covid["CANTIDAD_DELIVERYS"].mean(),
        post_covid["CANTIDAD_DELIVERYS"].mean()
    ]
})

st.dataframe(
    comparacion,
    use_container_width=True
)

st.divider()

# =========================================================
# HEATMAP
# =========================================================

st.subheader("🔥 Heatmap de Ventas")

heatmap_data = df.pivot_table(
    values="VENTA_TOTAL",
    index="AÑO",
    columns="MES",
    aggfunc="sum"
)

fig_heatmap = px.imshow(
    heatmap_data,
    text_auto=True,
    aspect="auto",
    color_continuous_scale="Blues"
)

fig_heatmap.update_layout(
    template="plotly_dark",
    height=500
)

st.plotly_chart(
    fig_heatmap,
    use_container_width=True
)

st.divider()

# =========================================================
# VISTA GENERAL
# =========================================================

if modo == "Vista General":

    st.subheader("📈 Evolución General del Negocio")

    # =====================================================
    # DELIVERYS
    # =====================================================

    fig_general_delivery = px.line(
        df,
        x="AÑO",
        y="CANTIDAD_DELIVERYS",
        color="MES",
        markers=True
    )

    fig_general_delivery.update_layout(
        template="plotly_dark",
        height=550,
        title="Evolución Histórica de Deliverys",
        xaxis_title="Año",
        yaxis_title="Cantidad de Deliverys",
        legend_title="Mes"
    )

    fig_general_delivery.add_vline(
        x=2020,
        line_width=2,
        line_dash="dash",
        line_color="red"
    )

    fig_general_delivery.add_annotation(
        x=2020,
        y=df["CANTIDAD_DELIVERYS"].max(),
        text="COVID",
        showarrow=True
    )

    st.plotly_chart(
        fig_general_delivery,
        use_container_width=True
    )

    # =====================================================
    # VENTAS
    # =====================================================

    fig_general_ventas = px.line(
        df,
        x="AÑO",
        y="VENTA_TOTAL",
        color="MES",
        markers=True
    )

    fig_general_ventas.update_layout(
        template="plotly_dark",
        height=550,
        title="Evolución Histórica de Ventas",
        xaxis_title="Año",
        yaxis_title="Venta Total",
        legend_title="Mes"
    )

    fig_general_ventas.add_vline(
        x=2020,
        line_width=2,
        line_dash="dash",
        line_color="red"
    )

    fig_general_ventas.add_annotation(
        x=2020,
        y=df["VENTA_TOTAL"].max(),
        text="COVID",
        showarrow=True
    )

    st.plotly_chart(
        fig_general_ventas,
        use_container_width=True
    )

# =========================================================
# ANALISIS POR MES
# =========================================================

else:

    st.subheader("📊 Análisis Histórico por Mes")

    mes_seleccionado = st.selectbox(
        "Selecciona un mes",
        sorted(
            df["MES"].unique(),
            key=lambda x: orden_meses[x]
        )
    )

    df_mes = df[df["MES"] == mes_seleccionado]

    # =====================================================
    # KPIS DEL MES
    # =====================================================

    st.markdown(f"## 📌 Resumen Ejecutivo - {mes_seleccionado}")

    top_anio = (
        df_mes.loc[df_mes["VENTA_TOTAL"].idxmax()]
    )

    crecimiento_total_mes = (
        (
            df_mes.iloc[-1]["VENTA_TOTAL"]
            - df_mes.iloc[0]["VENTA_TOTAL"]
        )
        / df_mes.iloc[0]["VENTA_TOTAL"]
    ) * 100

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric(
            "🏆 Mejor Año",
            f"{top_anio['AÑO']}"
        )

    with k2:
        st.metric(
            "💰 Mayor Venta",
            f"S/ {top_anio['VENTA_TOTAL']:,.0f}"
        )

    with k3:
        st.metric(
            "📦 Mayor Delivery",
            f"{int(top_anio['CANTIDAD_DELIVERYS']):,}"
        )

    with k4:
        st.metric(
            "📈 Crecimiento Histórico",
            f"{crecimiento_total_mes:.2f}%"
        )

    st.divider()

    # =====================================================
    # GRAFICO DELIVERYS
    # =====================================================

    st.subheader(
        f"📦 Evolución Histórica de Deliverys - {mes_seleccionado}"
    )

    fig_delivery = px.line(
        df_mes,
        x="AÑO",
        y="CANTIDAD_DELIVERYS",
        markers=True,
        text="CANTIDAD_DELIVERYS"
    )

    fig_delivery.update_traces(
        textposition="top center"
    )

    fig_delivery.update_layout(
        template="plotly_dark",
        height=550,
        xaxis_title="Año",
        yaxis_title="Cantidad Deliverys"
    )

    fig_delivery.add_vline(
        x=2020,
        line_width=2,
        line_dash="dash",
        line_color="red"
    )

    fig_delivery.add_annotation(
        x=2020,
        y=df_mes["CANTIDAD_DELIVERYS"].max(),
        text="COVID",
        showarrow=True
    )

    st.plotly_chart(
        fig_delivery,
        use_container_width=True
    )

    # =====================================================
    # INSIGHT DELIVERYS
    # =====================================================

    delivery_inicio = df_mes.iloc[0]["CANTIDAD_DELIVERYS"]
    delivery_final = df_mes.iloc[-1]["CANTIDAD_DELIVERYS"]

    if delivery_final > delivery_inicio:

        st.success(
            f"""
            📌 El mes de {mes_seleccionado} presenta una tendencia
            creciente en la cantidad de deliverys respecto a los
            primeros años analizados.
            """
        )

    else:

        st.warning(
            f"""
            📌 El mes de {mes_seleccionado} presenta una desaceleración
            en la cantidad de deliverys.
            """
        )

    st.divider()

    # =====================================================
    # GRAFICO VENTAS
    # =====================================================

    st.subheader(
        f"💰 Evolución Histórica de Ventas - {mes_seleccionado}"
    )

    fig_ventas = px.bar(
        df_mes,
        x="AÑO",
        y="VENTA_TOTAL",
        text_auto=".2s"
    )

    fig_ventas.update_layout(
        template="plotly_dark",
        height=550,
        xaxis_title="Año",
        yaxis_title="Venta Total"
    )

    fig_ventas.add_vline(
        x=2020,
        line_width=2,
        line_dash="dash",
        line_color="red"
    )

    fig_ventas.add_annotation(
        x=2020,
        y=df_mes["VENTA_TOTAL"].max(),
        text="COVID",
        showarrow=True
    )

    st.plotly_chart(
        fig_ventas,
        use_container_width=True
    )

    st.divider()

    # =====================================================
    # TICKET PROMEDIO
    # =====================================================

    st.subheader(
        f"🧾 Evolución Ticket Promedio - {mes_seleccionado}"
    )

    fig_ticket = px.line(
        df_mes,
        x="AÑO",
        y="TICKET_PROMEDIO",
        markers=True,
        text=df_mes["TICKET_PROMEDIO"].round(2)
    )

    fig_ticket.update_traces(
        textposition="top center"
    )

    fig_ticket.update_layout(
        template="plotly_dark",
        height=550,
        xaxis_title="Año",
        yaxis_title="Ticket Promedio"
    )

    st.plotly_chart(
        fig_ticket,
        use_container_width=True
    )

    st.divider()

    # =====================================================
    # CRECIMIENTO %
    # =====================================================

    st.subheader(
        f"📈 Crecimiento % Histórico - {mes_seleccionado}"
    )

    fig_growth = px.bar(
        df_mes,
        x="AÑO",
        y="CRECIMIENTO_%",
        text_auto=".2f"
    )

    fig_growth.update_layout(
        template="plotly_dark",
        height=550,
        xaxis_title="Año",
        yaxis_title="Crecimiento %"
    )

    st.plotly_chart(
        fig_growth,
        use_container_width=True
    )

    # =====================================================
    # SEMAFORO
    # =====================================================

    ultimo_crecimiento = (
        df_mes["CRECIMIENTO_%"].iloc[-1]
    )

    st.subheader("🚦 Indicador de Desempeño")

    if ultimo_crecimiento > 10:

        st.success(
            f"""
            🟢 El mes de {mes_seleccionado}
            presenta un crecimiento sólido respecto
            al año anterior.
            """
        )

    elif ultimo_crecimiento > 0:

        st.warning(
            f"""
            🟡 El mes de {mes_seleccionado}
            presenta crecimiento moderado.
            """
        )

    else:

        st.error(
            f"""
            🔴 El mes de {mes_seleccionado}
            presenta una caída respecto
            al año anterior.
            """
        )

# =========================================================
# TABLA
# =========================================================

st.divider()

st.subheader("📋 Tabla Detallada")

st.dataframe(
    df,
    use_container_width=True
)

# =========================================================
# CONCLUSION
# =========================================================

st.subheader("📌 Conclusión Ejecutiva")

st.success(
    """
El análisis histórico evidencia variaciones importantes en el comportamiento
comercial de la operación delivery. Durante el periodo COVID-19 se registró
el mayor crecimiento histórico debido al incremento del consumo mediante
canales digitales y restricciones de movilidad.

Posteriormente, el negocio presenta una estabilización progresiva,
manteniendo niveles sólidos de ventas y ticket promedio.
"""
)

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")
st.caption("Dashboard desarrollado en Streamlit")



