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
# CARGA DATOS GOOGLE SHEETS
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
# SIDEBAR
# =========================================================

st.sidebar.title("📊 Filtros")

anios = sorted(df["AÑO"].unique())

anios_seleccionados = st.sidebar.multiselect(
    "Selecciona Año(s)",
    anios,
    default=anios
)

meses = sorted(
    df["MES"].unique(),
    key=lambda x: orden_meses[x]
)

meses_seleccionados = st.sidebar.multiselect(
    "Selecciona Mes(es)",
    meses,
    default=meses
)

# =========================================================
# FILTRO
# =========================================================

df_filtrado = df[
    (df["AÑO"].isin(anios_seleccionados)) &
    (df["MES"].isin(meses_seleccionados))
]

# =========================================================
# TITULO
# =========================================================

st.title("📦 Dashboard Ejecutivo Delivery")
st.markdown("### Análisis Histórico de Deliverys y Ventas")

st.divider()

# =========================================================
# KPIs
# =========================================================

st.subheader("📌 KPIs Principales")

total_deliverys = int(df_filtrado["CANTIDAD_DELIVERYS"].sum())

venta_total = df_filtrado["VENTA_TOTAL"].sum()

ticket_promedio = df_filtrado["TICKET_PROMEDIO"].mean()

mejor_anio = (
    df_filtrado.groupby("AÑO")["VENTA_TOTAL"]
    .sum()
    .idxmax()
)

mejor_mes = (
    df_filtrado.loc[
        df_filtrado["VENTA_TOTAL"].idxmax(),
        "MES"
    ]
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
        "🧾 Ticket Prom.",
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
        f"{mejor_mes}"
    )

st.divider()

# =========================================================
# HALLAZGOS
# =========================================================

st.subheader("📌 Hallazgos Clave")

st.info(
    """
Durante el periodo COVID-19 (2020-2021) se observa un incremento significativo
en la demanda de deliverys y ventas debido a las restricciones de movilidad
y el crecimiento del consumo mediante canales de entrega.
"""
)

# =========================================================
# TOPS
# =========================================================

st.subheader("🏆 Top Meses por Ventas")

top_meses = (
    df_filtrado
    .sort_values(by="VENTA_TOTAL", ascending=False)
    [["AÑO", "MES", "VENTA_TOTAL", "CANTIDAD_DELIVERYS"]]
    .head(5)
)

st.dataframe(
    top_meses,
    use_container_width=True
)

st.divider()

# =========================================================
# GRAFICO VENTAS
# =========================================================

st.subheader("💰 Comparativa de Ventas por Año")

fig1 = px.bar(
    df_filtrado,
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

# =========================================================
# GRAFICO DELIVERYS
# =========================================================

st.subheader("📦 Comparativa de Deliverys")

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
    height=500,
    xaxis_title="Mes",
    yaxis_title="Cantidad Deliverys",
    legend_title="Año"
)

st.plotly_chart(fig2, use_container_width=True)

# =========================================================
# EVOLUCION POR MES
# =========================================================

st.subheader("📈 Evolución Histórica por Mes")

for mes in meses_seleccionados:

    st.markdown(f"### {mes}")

    df_mes = df_filtrado[df_filtrado["MES"] == mes]

    fig_mes = px.line(
        df_mes,
        x="AÑO",
        y="VENTA_TOTAL",
        markers=True,
        text="VENTA_TOTAL"
    )

    fig_mes.update_layout(
        template="plotly_dark",
        height=400,
        xaxis_title="Año",
        yaxis_title="Venta Total"
    )

    st.plotly_chart(fig_mes, use_container_width=True)

# =========================================================
# CRECIMIENTO %
# =========================================================

st.subheader("📊 Crecimiento Porcentual por Año")

df_crecimiento = df_filtrado.copy()

df_crecimiento["CRECIMIENTO_%"] = (
    df_crecimiento
    .groupby("MES")["VENTA_TOTAL"]
    .pct_change() * 100
)

fig_growth = px.bar(
    df_crecimiento,
    x="AÑO",
    y="CRECIMIENTO_%",
    color="MES",
    barmode="group",
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
# TICKET PROMEDIO
# =========================================================

st.subheader("🧾 Evolución Ticket Promedio")

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
    yaxis_title="Ticket Promedio"
)

st.plotly_chart(fig3, use_container_width=True)

# =========================================================
# TABLA DETALLADA
# =========================================================

st.subheader("📋 Tabla Detallada")

st.dataframe(
    df_filtrado,
    use_container_width=True
)

# =========================================================
# CONCLUSION
# =========================================================

st.subheader("📌 Conclusión Ejecutiva")

st.success(
    """
El negocio presenta una tendencia positiva en ventas y cantidad de deliverys,
con un crecimiento acelerado durante el periodo de pandemia y estabilización
en los años posteriores. El ticket promedio mantiene una tendencia estable,
lo que evidencia consistencia en el comportamiento de compra.
"""
)

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")
st.caption("Dashboard desarrollado en Streamlit")
