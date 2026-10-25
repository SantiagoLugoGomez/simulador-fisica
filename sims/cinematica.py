from functools import partial

import numpy as np
import streamlit as st
from matplotlib.figure import Figure

from sims.comun import AZUL, GRIS, GRIS_CLARO, NARANJA, controles_tiempo, flecha, mostrar_escena


def movimiento(x0, v0, a, t):
    t = np.asarray(t, dtype=float)
    x = x0 + v0 * t + a * t**2 / 2
    v = v0 + a * t
    return x, v, np.full_like(t, a)


def tiempo_caida(h, v0, g):
    return (v0 + np.sqrt(v0**2 + 2 * g * h)) / g


def altura_maxima(h, v0, g):
    return h + max(v0, 0) ** 2 / (2 * g)


def figura_escena(vertical, x0, v0, a, t_final, instante):
    x, v, _ = movimiento(x0, v0, a, np.linspace(0, t_final, 300))
    xi, vi, _ = movimiento(x0, v0, a, instante)
    rango = max(x.max() - x.min(), 1.0)
    vmax = np.abs(v).max()
    largo = 0.25 * rango * vi / vmax if vmax > 0 else 0.0

    if vertical:
        fig = Figure(figsize=(4, 4.4), layout="constrained")
        ax = fig.subplots()
        ax.axhline(0, color=GRIS, lw=1.5)
        ax.plot([0, 0], [0, x.max()], color=GRIS_CLARO, lw=1, ls="--")
        ax.plot(0, xi, "o", color=AZUL, ms=16, zorder=5)
        flecha(ax, 0, xi, 0, largo, NARANJA)
        ax.set_xlim(-1, 1)
        ax.set_ylim(-0.3 * rango, x.max() + 0.3 * rango)
        ax.set_xticks([])
        ax.set_ylabel("Altura y (m)")
        ax.spines["bottom"].set_visible(False)
    else:
        fig = Figure(figsize=(4, 1.8), layout="constrained")
        ax = fig.subplots()
        ax.axhline(0, color=GRIS_CLARO, lw=1)
        ax.plot(x0, 0, "o", color=GRIS_CLARO, ms=8, mfc="white")
        ax.plot(xi, 0, "o", color=AZUL, ms=16, zorder=5)
        flecha(ax, xi, 0, largo, 0, NARANJA)
        ax.set_xlim(x.min() - 0.3 * rango, x.max() + 0.3 * rango)
        ax.set_ylim(-1, 1)
        ax.set_yticks([])
        ax.set_xlabel("Posición x (m)")
        ax.spines["left"].set_visible(False)

    ax.set_title(f"t = {instante:.2f} s")
    return fig


def figura_graficas(vertical, x0, v0, a, t_final, instante):
    t = np.linspace(0, t_final, 400)
    x, v, ac = movimiento(x0, v0, a, t)
    xi, vi, ai = movimiento(x0, v0, a, instante)
    nombre = "y" if vertical else "x"
    datos = [
        (x, xi, f"{nombre} (m)", f"Posición vs tiempo ({nombre}-t)"),
        (v, vi, "v (m/s)", "Velocidad vs tiempo (v-t)"),
        (ac, ai, "a (m/s²)", "Aceleración vs tiempo (a-t)"),
    ]

    fig = Figure(figsize=(6, 6), layout="constrained")
    ejes = fig.subplots(3, 1, sharex=True)
    for ax, (y, yi, etiqueta, titulo) in zip(ejes, datos):
        ax.plot(t, y, color=AZUL)
        ax.plot(instante, yi, "o", color=AZUL, ms=9, mec="white", mew=2)
        ax.set_ylabel(etiqueta)
        ax.set_title(titulo)
    ejes[2].set_ylim(min(a, 0) - 1, max(a, 0) + 1)
    ejes[2].set_xlabel("Tiempo t (s)")
    return fig


def mostrar():
    st.header("Cinemática")
    tipo = st.radio("Tipo de movimiento", ["MRU", "MRUA", "Caída libre"], horizontal=True)

    st.sidebar.header("Parámetros")
    if tipo == "Caída libre":
        h = st.sidebar.slider("Altura inicial h (m)", 1.0, 200.0, 50.0, 1.0)
        v0 = st.sidebar.slider("Velocidad inicial v₀ (m/s)", -30.0, 30.0, 0.0, 0.5,
                               help="Positiva hacia arriba, negativa hacia abajo.")
        g = st.sidebar.slider("Gravedad g (m/s²)", 1.0, 25.0, 9.81, 0.01)
        x0, a = h, -g
        t_final = tiempo_caida(h, v0, g)
    else:
        x0 = st.sidebar.slider("Posición inicial x₀ (m)", -50.0, 50.0, 0.0, 0.5)
        v0 = st.sidebar.slider("Velocidad inicial v₀ (m/s)", -20.0, 20.0, 5.0, 0.5)
        a = st.sidebar.slider("Aceleración a (m/s²)", -10.0, 10.0, 1.0, 0.1) if tipo == "MRUA" else 0.0
        t_final = st.sidebar.slider("Tiempo total (s)", 1.0, 30.0, 10.0, 0.5)

    xf, vf, _ = movimiento(x0, v0, a, t_final)
    c1, c2, c3 = st.columns(3)
    if tipo == "Caída libre":
        c1.metric("Tiempo de caída", f"{t_final:.2f} s", border=True)
        c2.metric("Velocidad de impacto", f"{abs(vf):.2f} m/s", border=True)
        c3.metric("Altura máxima", f"{altura_maxima(h, v0, g):.2f} m", border=True)
    else:
        c1.metric("Posición final", f"{xf:.2f} m", border=True)
        c2.metric("Desplazamiento", f"{xf - x0:.2f} m", border=True)
        c3.metric("Velocidad final", f"{vf:.2f} m/s", border=True)

    vertical = tipo == "Caída libre"
    izq, der = st.columns([2, 3], gap="large")
    instante, animado, lugar = controles_tiempo(izq, t_final)
    izq.caption("La flecha naranja representa la velocidad en el instante t.")
    der.pyplot(figura_graficas(vertical, x0, v0, a, t_final, instante))
    mostrar_escena(lugar, partial(figura_escena, vertical, x0, v0, a, t_final), instante, t_final, animado)
