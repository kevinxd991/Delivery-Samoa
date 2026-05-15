
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
        "Insights Automáticos"
    ]
)

# =========================================================
# RESUMEN EJECUTIVO
# =========================================================

if seccion == "Resumen Ejecutivo":

    st.subheader("📌 Resumen Ejecutivo")

    total_deliverys = int(df["CANTIDAD_DELIVERYS"].sum())
    venta_total = df["VENTA_TOTAL"].sum()
    ticket_promedio = df["TICKET_PROMEDIO"].mean()

    crecimiento_historico = (
        (
            df.iloc[-1]["VENTA_TOTAL"]
            - df.iloc[0]["VENTA_TOTAL"]
        )
        / df.iloc[0]["VENTA_TOTAL"]
    ) * 100

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "📦 Deliverys Totales",
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
            "📈 Crecimiento Histórico",
            f"{crecimiento_historico:.2f}%"
        )

    st.divider()

    st.info("""
    Durante el periodo COVID-19 (2020-2021)
    se observa un crecimiento importante en la
    demanda de deliverys debido al incremento
    del consumo mediante canales digitales.
    """)

    st.divider()

    st.subheader("📈 Panorama General")

    metrica_general = st.selectbox(
        "Selecciona métrica",
        [
            "VENTA_TOTAL",
            "CANTIDAD_DELIVERYS",
            "TICKET_PROMEDIO"
        ]
    )

    nombres = {
        "VENTA_TOTAL": "Ventas",
        "CANTIDAD_DELIVERYS": "Deliverys",
        "TICKET_PROMEDIO": "Ticket Promedio"
    }

    fig_general = px.line(
        df,
        x="AÑO",
        y=metrica_general,
        color="MES",
        markers=True
    )

    fig_general.update_layout(
        template="plotly_dark",
        height=600,
        title=f"Panorama General - {nombres[metrica_general]}",
        xaxis_title="Año",
        yaxis_title=nombres[metrica_general]
    )

    fig_general.add_vline(
        x=2020,
        line_width=2,
        line_dash="dash",
        line_color="red"
    )

    fig_general.add_annotation(
        x=2020,
        y=df[metrica_general].max(),
        text="COVID",
        showarrow=True
    )

    st.plotly_chart(
        fig_general,
        use_container_width=True
    )

# =========================================================
# KPIs
# =========================================================

elif seccion == "KPIs":

    st.subheader("📊 KPIs Estratégicos (YoY)")

    meses_ordenados = sorted(
        df["MES"].unique(),
        key=lambda x: orden_meses[x]
    )

    mes_kpi = st.selectbox(
        "Selecciona un mes",
        meses_ordenados
    )

    anios = sorted(df["AÑO"].unique())

    colf1, colf2 = st.columns(2)

    with colf1:

        anio_base = st.selectbox(
            "Año Base",
            anios,
            index=len(anios)-2
        )

    with colf2:

        anio_compare = st.selectbox(
            "Año Comparativo",
            anios,
            index=len(anios)-1
        )

    df_base = df[
        (df["MES"] == mes_kpi)
        &
        (df["AÑO"] == anio_base)
    ]

    df_compare = df[
        (df["MES"] == mes_kpi)
        &
        (df["AÑO"] == anio_compare)
    ]

    if df_base.empty or df_compare.empty:

        st.error("No existen datos para esa comparación.")

    else:

        venta_base = df_base["VENTA_TOTAL"].values[0]
        venta_compare = df_compare["VENTA_TOTAL"].values[0]

        delivery_base = df_base["CANTIDAD_DELIVERYS"].values[0]
        delivery_compare = df_compare["CANTIDAD_DELIVERYS"].values[0]

        ticket_base = df_base["TICKET_PROMEDIO"].values[0]
        ticket_compare = df_compare["TICKET_PROMEDIO"].values[0]

        diferencia_ventas = venta_compare - venta_base
        diferencia_deliverys = delivery_compare - delivery_base
        diferencia_ticket = ticket_compare - ticket_base

        crecimiento_ventas = (
            diferencia_ventas / venta_base
        ) * 100

        crecimiento_deliverys = (
            diferencia_deliverys / delivery_base
        ) * 100

        crecimiento_ticket = (
            diferencia_ticket / ticket_base
        ) * 100

        st.markdown(
            f"""
            ## 📌 Comparativa:
            {mes_kpi} {anio_base}
            vs
            {mes_kpi} {anio_compare}
            """
        )

        k1, k2, k3 = st.columns(3)

        with k1:

            st.metric(
                "💰 Ventas",
                f"S/ {venta_compare:,.0f}",
                delta=f"{crecimiento_ventas:.2f}%"
            )

        with k2:

            st.metric(
                "📦 Deliverys",
                f"{delivery_compare:,.0f}",
                delta=f"{crecimiento_deliverys:.2f}%"
            )

        with k3:

            st.metric(
                "🧾 Ticket Promedio",
                f"S/ {ticket_compare:,.2f}",
                delta=f"{crecimiento_ticket:.2f}%"
            )

        st.divider()

        st.subheader("📊 Diferencias Absolutas")

        d1, d2, d3 = st.columns(3)

        with d1:

            st.metric(
                "💵 Diferencia Ventas",
                f"S/ {diferencia_ventas:,.0f}"
            )

        with d2:

            st.metric(
                "🚚 Diferencia Deliverys",
                f"{diferencia_deliverys:,.0f}"
            )

        with d3:

            st.metric(
                "🧾 Diferencia Ticket",
                f"S/ {diferencia_ticket:,.2f}"
            )

        st.divider()

        st.subheader("📈 Comparación Visual")

        comparativo_df = pd.DataFrame({

            "Indicador": [
                "Ventas",
                "Deliverys",
                "Ticket"
            ],

            f"{anio_base}": [
                venta_base,
                delivery_base,
                ticket_base
            ],

            f"{anio_compare}": [
                venta_compare,
                delivery_compare,
                ticket_compare
            ]
        })

        comparativo_melt = comparativo_df.melt(
            id_vars="Indicador",
            var_name="Año",
            value_name="Valor"
        )

        fig_compare = px.bar(
            comparativo_melt,
            x="Indicador",
            y="Valor",
            color="Año",
            barmode="group",
            text_auto=".2s"
        )

        fig_compare.update_layout(
            template="plotly_dark",
            height=550
        )

        st.plotly_chart(
            fig_compare,
            use_container_width=True
        )

        st.divider()

        st.subheader("📌 Interpretación Ejecutiva")

        if crecimiento_ventas > 0:

            st.success(
                f"""
                El mes de {mes_kpi} del año {anio_compare}
                presentó un crecimiento de
                {crecimiento_ventas:.2f}% en ventas
                respecto al mismo mes del año {anio_base}.

                Esto representa una diferencia positiva de
                S/ {diferencia_ventas:,.0f}.
                """
            )

        else:

            st.error(
                f"""
                El mes de {mes_kpi} del año {anio_compare}
                presentó una caída de
                {abs(crecimiento_ventas):.2f}% en ventas
                respecto al mismo mes del año {anio_base}.
                """
            )

        st.divider()

        st.subheader("🧠 ¿Cómo se calcula el KPI?")

        st.info(
            f"""
            Fórmula del crecimiento YoY:

            ((Valor Nuevo - Valor Antiguo)
            / Valor Antiguo) x 100

            Ejemplo aplicado:

            (({venta_compare:,.0f}
            - {venta_base:,.0f})
            / {venta_base:,.0f}) x 100

            Resultado:
            {crecimiento_ventas:.2f}%
            """
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

# =========================================================
# COMPARACION AÑO VS AÑO
# =========================================================

elif seccion == "Comparación Año vs Año":

    st.subheader("⚖️ Comparación Año vs Año")

    anios = sorted(df["AÑO"].unique())

    anio1 = st.selectbox(
        "Selecciona Año Base",
        anios,
        index=len(anios)-2
    )

    anio2 = st.selectbox(
        "Selecciona Año Comparativo",
        anios,
        index=len(anios)-1
    )

    df_compare = df[
        df["AÑO"].isin([anio1, anio2])
    ]

    fig_compare = px.bar(
        df_compare,
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

    crecimiento_total = (
        (
            df.iloc[-1]["VENTA_TOTAL"]
            - df.iloc[0]["VENTA_TOTAL"]
        )
        / df.iloc[0]["VENTA_TOTAL"]
    ) * 100

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

    st.success(
        f"""
        📈 El negocio presenta crecimiento histórico
        acumulado de {crecimiento_total:.2f}%.
        """
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
```



