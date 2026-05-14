import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# CONFIGURACION DE PAGINA
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

h1, h2, h3 {
    color: white;
}

[data-testid="metric-container"] {
    background-color: #1E1E1E;
    border: 1px solid #333;
    padding: 18px;
    border-radius: 15px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# CARGA DE DATOS
# =========================================================

sheet_id = "1LXPe-ZN-Hcc9_PgrkRNVAtvIZkyk3WCT0uSFBocfvM8"

url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

df = pd.read_csv(url)

# =========================================================
# LIMPIEZA Y PREPARACION
# =========================================================

df.columns = df.columns.str.strip()

# Orden correcto de meses
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

# Ordenar
df = df.sort_values(by=["AÑO", "MES_NUM"])

# Ticket promedio
df["TICKET_PROMEDIO"] = (
    df["VENTA_TOTAL"] / df["CANTIDAD_DELIVERYS"]
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

st.sidebar.header("Filtros")

anios = sorted(df["AÑO"].unique())

anios_seleccionados = st.sidebar.multiselect(
    "Selecciona Año(s)",
    anios,
    default=anios
)

meses = st.sidebar.multiselect(
    "Selecciona Mes(es)",
    sorted(df["MES"].unique(), key=lambda x: orden_meses[x]),
    default=sorted(df["MES"].unique(), key=lambda x: orden_meses[x])
)

# =========================================================
# FILTRADO
# =========================================================

df_filtrado = df[
    (df["AÑO"].isin(anios_seleccionados)) &
    (df["MES"].isin(meses))
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
# GRAFICO 1 - VENTAS
# =========================================================

st.subheader("💰 Comparativa de Ventas por Año")

fig1 = px.bar(
    df_filtrado,
    x="MES",
    y="VENTA_TOTAL",
    color="AÑO",
    barmode="group"
)

fig1.update_layout(
    template="plotly_dark",
    height=500,
    xaxis_title="Mes",
    yaxis_title="Venta Total",
    legend_title="Año"
)

st.plotly_chart(fig1, use_container_width=True)

# =========================================================
# GRAFICO 2 - DELIVERYS
# =========================================================

st.subheader("📦 Comparativa de Deliverys")

fig2 = px.bar(
    df_filtrado,
    x="MES",
    y="CANTIDAD_DELIVERYS",
    color="AÑO",
    barmode="group"
)

fig2.update_layout(
    template="plotly_dark",
    height=500,
    xaxis_title="Mes",
    yaxis_title="Cantidad de Deliverys",
    legend_title="Año"
)

st.plotly_chart(fig2, use_container_width=True)

# =========================================================
# GRAFICO 3 - TICKET PROMEDIO
# =========================================================

st.subheader("🧾 Evolución del Ticket Promedio")

fig3 = px.line(
    df_filtrado,
    x="MES",
    y="TICKET_PROMEDIO",
    color="AÑO",
    markers=True
)

fig3.update_layout(
    template="plotly_dark",
    height=500,
    xaxis_title="Mes",
    yaxis_title="Ticket Promedio",
    legend_title="Año"
)

st.plotly_chart(fig3, use_container_width=True)

# =========================================================
# CRECIMIENTO
# =========================================================

st.subheader("📈 Resumen Ejecutivo")

if len(anios_seleccionados) >= 2:

    anio_actual = max(anios_seleccionados)
    anio_pasado = sorted(anios_seleccionados)[-2]

    actual = df_filtrado[df_filtrado["AÑO"] == anio_actual]
    pasado = df_filtrado[df_filtrado["AÑO"] == anio_pasado]

    venta_actual = actual["VENTA_TOTAL"].sum()
    venta_pasada = pasado["VENTA_TOTAL"].sum()

    delivery_actual = actual["CANTIDAD_DELIVERYS"].sum()
    delivery_pasado = pasado["CANTIDAD_DELIVERYS"].sum()

    ticket_actual = actual["TICKET_PROMEDIO"].mean()
    ticket_pasado = pasado["TICKET_PROMEDIO"].mean()

    crecimiento_ventas = (
        (venta_actual - venta_pasada) / venta_pasada
    ) * 100

    crecimiento_deliverys = (
        (delivery_actual - delivery_pasado) / delivery_pasado
    ) * 100

    crecimiento_ticket = (
        (ticket_actual - ticket_pasado) / ticket_pasado
    ) * 100

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Crecimiento Ventas",
            f"{crecimiento_ventas:.2f}%"
        )

    with c2:
        st.metric(
            "Crecimiento Deliverys",
            f"{crecimiento_deliverys:.2f}%"
        )

    with c3:
        st.metric(
            "Crecimiento Ticket",
            f"{crecimiento_ticket:.2f}%"
        )

st.divider()

# =========================================================
# TABLA
# =========================================================

st.subheader("📋 Datos Detallados")

st.dataframe(
    df_filtrado,
    use_container_width=True
)

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")
st.caption("Dashboard desarrollado en Streamlit")
