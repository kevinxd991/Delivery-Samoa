# app.py

```python
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

# Crecimiento porcentual

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
# TOP 3 AÑOS
# =========================================================

st.subheader("🏆 Top 3 Mejores Años")

top_anios = (
    df.groupby("AÑO")["VENTA_TOTAL"]
    .sum()
    .sort_values(ascending=False)
    .head(3)
)

col_top1, col_top2, col_top3 = st.columns(3)

ranking = list(top_anios.items())

medallas = ["🥇", "🥈", "🥉"]

for i, col in enumerate([col_top1, col_top2, col_top3]):
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

st.dataframe(comparacion, use_container_width=True)

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

st.plotly_chart(fig_heatmap, use_container_width=True)

st.divider()

# =========================================================
# MODO GENERAL
# =========================================================

if modo == "Vista General":

    st.subheader("💰 Ventas por Mes y Año")

    fig1 = px.bar(
        df,
        x="MES",
        y="VENTA_TOTAL",
        color="AÑO",
        barmode="group"
    )

    fig1.update_layout(
        template="plotly_dark",
        height=500
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("📦 Deliverys por Mes y Año")

    fig2 = px.bar(
        df,
        x="MES",
        y="CANTIDAD_DELIVERYS",
        color="AÑO",
        barmode="group"
    )

    fig2.update_layout(
        template="plotly_dark",
        height=500
    )

    st.plotly_chart(fig2, use_container_width=True)

# =========================================================
# ANALISIS POR MES
# =========================================================

else:

    st.subheader("📈 Evolución Histórica por Mes")

    mes_seleccionado = st.selectbox(
        "Selecciona un Mes",
        sorted(
            df["MES"].unique(),
            key=lambda x: orden_meses[x]
        )
    )

    df_mes = df[df["MES"] == mes_seleccionado]

    # =====================================================
    # KPI DEL MES
    # =====================================================

    top_anio_mes = (
        df_mes.loc[df_mes["VENTA_TOTAL"].idxmax()]
    )

    colm1, colm2, colm3 = st.columns(3)

    with colm1:
        st.metric(
            "🏆 Mejor Año",
            f"{top_anio_mes['AÑO']}"
        )

    with colm2:
        st.metric(
            "💰 Mayor Venta",
            f"S/ {top_anio_mes['VENTA_TOTAL']:,.0f}"
        )

    with colm3:
        st.metric(
            "📦 Deliverys",
            f"{int(top_anio_mes['CANTIDAD_DELIVERYS']):,}"
        )

    st.divider()

    # =====================================================
    # DELIVERYS
    # =====================================================

    st.subheader(f"📦 Evolución Deliverys - {mes_seleccionado}")

    fig_delivery = px.bar(
        df_mes,
        x="AÑO",
        y="CANTIDAD_DELIVERYS",
        text_auto=True
    )

    fig_delivery.update_layout(
        template="plotly_dark",
        height=500
    )

    st.plotly_chart(fig_delivery, use_container_width=True)

    # =====================================================
    # VENTAS
    # =====================================================

    st.subheader(f"💰 Evolución Ventas - {mes_seleccionado}")

    fig_ventas = px.bar(
        df_mes,
        x="AÑO",
        y="VENTA_TOTAL",
        text_auto='.2s'
    )

    fig_ventas.update_layout(
        template="plotly_dark",
        height=500
    )

    st.plotly_chart(fig_ventas, use_container_width=True)

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
        height=500
    )

    st.plotly_chart(fig_ticket, use_container_width=True)

    # =====================================================
    # CRECIMIENTO
    # =====================================================

    st.subheader(f"📈 Crecimiento % - {mes_seleccionado}")

    fig_growth = px.bar(
        df_mes,
        x="AÑO",
        y="CRECIMIENTO_%",
        text_auto='.2f'
    )

    fig_growth.update_layout(
        template="plotly_dark",
        height=500
    )

    st.plotly_chart(fig_growth, use_container_width=True)

    # =====================================================
    # VARIACION VS AÑO ANTERIOR
    # =====================================================

    st.subheader("🚦 Variación vs Año Anterior")

    ultimo_crecimiento = df_mes["CRECIMIENTO_%"].iloc[-1]

    if ultimo_crecimiento > 10:
        st.success(
            f"🟢 Crecimiento positivo de {ultimo_crecimiento:.2f}% respecto al año anterior"
        )
    elif ultimo_crecimiento > 0:
        st.warning(
            f"🟡 Crecimiento moderado de {ultimo_crecimiento:.2f}%"
        )
    else:
        st.error(
            f"🔴 Caída de {ultimo_crecimiento:.2f}% respecto al año anterior"
        )

st.divider()

# =========================================================
# TABLA DETALLADA
# =========================================================

st.subheader("📋 Tabla Detallada")

st.dataframe(df, use_container_width=True)

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
```


