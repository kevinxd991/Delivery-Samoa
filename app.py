import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# CONFIGURACION PAGINA
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

.main {
    background-color: #0E1117;
}

h1, h2, h3, h4 {
    color: white;
}

[data-testid="metric-container"] {
    background-color: #1E1E1E;
    border: 1px solid #333;
    padding: 18px;
    border-radius: 15px;
}

.stAlert {
    border-radius: 12px;
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

# Ticket promedio
df["TICKET_PROMEDIO"] = (
    df["VENTA_TOTAL"] / df["CANTIDAD_DELIVERYS"]
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

st.sidebar.title("📊 Configuración")

modo = st.sidebar.radio(
    "Modo de visualización",
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

mejor_mes_data = (
    df.loc[df["VENTA_TOTAL"].idxmax()]
)

c1, c2, c3, c4, c5 = st.columns(5)

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
        f"{mejor_mes_data['MES']} {mejor_mes_data['AÑO']}"
    )

st.divider()

# =========================================================
# INSIGHTS
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
# MODO 1 - VISTA GENERAL
# =========================================================

if modo == "Vista General":

    st.subheader("💰 Ventas Totales por Mes y Año")

    fig1 = px.bar(
        df,
        x="MES",
        y="VENTA_TOTAL",
        color="AÑO",
        barmode="group",
        text_auto=".2s"
    )

    fig1.update_layout(
        template="plotly_dark",
        height=500,
        xaxis_title="Mes",
        yaxis_title="Venta Total",
        legend_title="Año"
    )

    st.plotly_chart(fig1, use_container_width=True)

    # =====================================================

    st.subheader("📦 Deliverys por Mes y Año")

    fig2 = px.bar(
        df,
        x="MES",
        y="CANTIDAD_DELIVERYS",
        color="AÑO",
        barmode="group",
        text_auto=True
    )

    fig2.update_layout(
        template="plotly_dark",
        height=500,
        xaxis_title="Mes",
        yaxis_title="Cantidad Deliverys",
        legend_title="Año"
    )

    st.plotly_chart(fig2, use_container_width=True)

# =========================================================
# MODO 2 - ANALISIS POR MES
# =========================================================

else:

    st.subheader("📈 Evolución Histórica por Mes")

    mes_seleccionado = st.selectbox(
        "Selecciona un mes",
        sorted(
            df["MES"].unique(),
            key=lambda x: orden_meses[x]
        )
    )

    df_mes = df[df["MES"] == mes_seleccionado]

    # =====================================================
    # KPI MES
    # =====================================================

    st.markdown(f"## 📌 Resumen de {mes_seleccionado}")

    top_anio = (
        df_mes.loc[df_mes["VENTA_TOTAL"].idxmax()]
    )

    colm1, colm2, colm3 = st.columns(3)

    with colm1:
        st.metric(
            "🏆 Mejor Año",
            f"{top_anio['AÑO']}"
        )

    with colm2:
        st.metric(
            "💰 Mayor Venta",
            f"S/ {top_anio['VENTA_TOTAL']:,.0f}"
        )

    with colm3:
        st.metric(
            "📦 Deliverys",
            f"{int(top_anio['CANTIDAD_DELIVERYS']):,}"
        )

    st.divider()

    # =====================================================
    # GRAFICO DELIVERYS
    # =====================================================

    st.subheader(f"📦 Evolución de Deliverys - {mes_seleccionado}")

    fig_mes_delivery = px.bar(
        df_mes,
        x="AÑO",
        y="CANTIDAD_DELIVERYS",
        text_auto=True
    )

    fig_mes_delivery.update_layout(
        template="plotly_dark",
        height=500,
        xaxis_title="Año",
        yaxis_title="Cantidad Deliverys"
    )

    st.plotly_chart(fig_mes_delivery, use_container_width=True)

    # =====================================================
    # GRAFICO VENTAS
    # =====================================================

    st.subheader(f"💰 Evolución de Ventas - {mes_seleccionado}")

    fig_mes_ventas = px.bar(
        df_mes,
        x="AÑO",
        y="VENTA_TOTAL",
        text_auto=".2s"
    )

    fig_mes_ventas.update_layout(
        template="plotly_dark",
        height=500,
        xaxis_title="Año",
        yaxis_title="Venta Total"
    )

    st.plotly_chart(fig_mes_ventas, use_container_width=True)

    # =====================================================
    # TICKET PROMEDIO
    # =====================================================

    st.subheader(f"🧾 Ticket Promedio - {mes_seleccionado}")

    fig_ticket = px.line(
        df_mes,
        x="AÑO",
        y="TICKET_PROMEDIO",
        markers=True,
        text=df_mes["TICKET_PROMEDIO"].round(2)
    )

    fig_ticket.update_layout(
        template="plotly_dark",
        height=500,
        xaxis_title="Año",
        yaxis_title="Ticket Promedio"
    )

    st.plotly_chart(fig_ticket, use_container_width=True)

    # =====================================================
    # CRECIMIENTO %
    # =====================================================

    st.subheader(f"📈 Crecimiento % - {mes_seleccionado}")

    df_mes = df_mes.sort_values(by="AÑO")

    df_mes["CRECIMIENTO_%"] = (
        df_mes["VENTA_TOTAL"].pct_change() * 100
    )

    fig_growth = px.bar(
        df_mes,
        x="AÑO",
        y="CRECIMIENTO_%",
        text_auto=".2f"
    )

    fig_growth.update_layout(
        template="plotly_dark",
        height=500,
        xaxis_title="Año",
        yaxis_title="Crecimiento %"
    )

    st.plotly_chart(fig_growth, use_container_width=True)

# =========================================================
# TABLA
# =========================================================

st.divider()

st.subheader("📋 Datos Detallados")

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
de ventas y deliverys a lo largo de los años. Se observa un crecimiento
acelerado durante el periodo de pandemia, impulsado por el aumento del
consumo mediante canales de entrega y restricciones de movilidad.
"""
)

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")
st.caption("Dashboard desarrollado en Streamlit")
