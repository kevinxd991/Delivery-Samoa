import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =========================================================
# CONFIGURACION PAGINA
# =========================================================
st.set_page_config(
    page_title="Dashboard Delivery",
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
    padding: 15px;
    border-radius: 15px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# CARGA DE DATOS DESDE GOOGLE SHEETS
# =========================================================

sheet_id = "1LXPe-ZN-Hcc9_PgrkRNVAtvIZkyk3WCT0uSFBocfvM8"

url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

df = pd.read_csv(url)

# =========================================================
# LIMPIEZA DE DATOS
# =========================================================

df.columns = df.columns.str.strip()

# Ticket promedio
df["TICKET_PROMEDIO"] = (
    df["VENTA_TOTAL"] / df["CANTIDAD_DELIVERYS"]
)

# =========================================================
# TITULO
# =========================================================

st.title("📦 Dashboard Delivery")
st.markdown("### Análisis Histórico de Deliverys y Ventas")

st.divider()

# =========================================================
# SIDEBAR FILTROS
# =========================================================

st.sidebar.header("Filtros")

anios = sorted(df["AÑO"].unique())

anios_seleccionados = st.sidebar.multiselect(
    "Selecciona Año(s)",
    anios,
    default=anios
)

meses = sorted(df["MES"].unique())

meses_seleccionados = st.sidebar.multiselect(
    "Selecciona Mes(es)",
    meses,
    default=meses
)

tipo_grafica = st.sidebar.selectbox(
    "Tipo de gráfica",
    ["Línea", "Barra", "Área"]
)

# =========================================================
# FILTRADO
# =========================================================

df_filtrado = df[
    (df["AÑO"].isin(anios_seleccionados)) &
    (df["MES"].isin(meses_seleccionados))
]

# =========================================================
# KPIs
# =========================================================

total_deliverys = int(df_filtrado["CANTIDAD_DELIVERYS"].sum())

venta_total = df_filtrado["VENTA_TOTAL"].sum()

ticket_promedio = df_filtrado["TICKET_PROMEDIO"].mean()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "📦 Total Deliverys",
        f"{total_deliverys:,}"
    )

with col2:
    st.metric(
        "💰 Venta Total",
        f"S/ {venta_total:,.2f}"
    )

with col3:
    st.metric(
        "🧾 Ticket Promedio",
        f"S/ {ticket_promedio:,.2f}"
    )

st.divider()

# =========================================================
# GRAFICA VENTAS
# =========================================================

st.subheader("📈 Evolución de Ventas")

if tipo_grafica == "Línea":

    fig1 = px.line(
        df_filtrado,
        x="MES_NUM",
        y="VENTA_TOTAL",
        color="AÑO",
        markers=True,
        text="VENTA_TOTAL"
    )

elif tipo_grafica == "Barra":

    fig1 = px.bar(
        df_filtrado,
        x="MES",
        y="VENTA_TOTAL",
        color="AÑO",
        barmode="group",
        text_auto=True
    )

else:

    fig1 = px.area(
        df_filtrado,
        x="MES_NUM",
        y="VENTA_TOTAL",
        color="AÑO"
    )

fig1.update_layout(
    template="plotly_dark",
    height=500,
    xaxis_title="Mes",
    yaxis_title="Venta Total"
)

st.plotly_chart(fig1, use_container_width=True)

# =========================================================
# GRAFICA DELIVERYS
# =========================================================

st.subheader("📦 Cantidad de Deliverys")

fig2 = px.bar(
    df_filtrado,
    x="MES",
    y="CANTIDAD_DELIVERYS",
    color="AÑO",
    barmode="group",
    text_auto=True
)

fig2.update_layout(
    template="plotly_dark",
    height=500
)

st.plotly_chart(fig2, use_container_width=True)

# =========================================================
# TICKET PROMEDIO
# =========================================================

st.subheader("🧾 Ticket Promedio por Mes")

fig3 = px.line(
    df_filtrado,
    x="MES_NUM",
    y="TICKET_PROMEDIO",
    color="AÑO",
    markers=True,
    text=df_filtrado["TICKET_PROMEDIO"].round(2)
)

fig3.update_layout(
    template="plotly_dark",
    height=500,
    xaxis_title="Mes",
    yaxis_title="Ticket Promedio"
)

st.plotly_chart(fig3, use_container_width=True)

# =========================================================
# TABLA DETALLADA
# =========================================================

st.subheader("📋 Datos Detallados")

st.dataframe(
    df_filtrado.sort_values(
        by=["AÑO", "MES_NUM"]
    ),
    use_container_width=True
)

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")
st.caption("Dashboard desarrollado en Streamlit")