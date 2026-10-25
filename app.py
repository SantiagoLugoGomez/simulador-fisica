import streamlit as st

from sims import cinematica, circular, colisiones, dinamica, energia, tiro_parabolico

st.set_page_config(page_title="Simulador de Física Mecánica", layout="wide")

MODULOS = {
    "Cinemática": cinematica,
    "Tiro parabólico": tiro_parabolico,
    "Movimiento circular": circular,
    "Dinámica": dinamica,
    "Energía": energia,
    "Colisiones 1D": colisiones,
}

st.sidebar.title("Simulador de Física Mecánica")
st.sidebar.caption("Física I · Unidades del Sistema Internacional")
modulo = st.sidebar.radio("Módulo", list(MODULOS))
MODULOS[modulo].mostrar()
