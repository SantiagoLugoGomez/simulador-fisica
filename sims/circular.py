from functools import partial

import numpy as np
import streamlit as st
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

from sims.comun import AZUL, GRIS, GRIS_CLARO, MORADO, NARANJA, VERDE, controles_tiempo, flecha, mostrar_escena


def movimiento_circular(w0, alfa, t):
    t = np.asarray(t, dtype=float)
    return w0 * t + alfa * t**2 / 2, w0 + alfa * t


def posicion(r, theta):
    return r * np.cos(theta), r * np.sin(theta)


def periodo(w):
    return 2 * np.pi / w


def figura_escena(r, w0, alfa, t_final, instante):
    theta, w = movimiento_circular(w0, alfa, instante)
    _, w_todos = movimiento_circular(w0, alfa, np.linspace(0, t_final, 300))
    w_max = np.abs(w_todos).max()
    a_max = np.hypot(w_todos**2 * r, alfa * r).max()
    x, y = posicion(r, theta)
    tangente = np.array([-np.sin(theta), np.cos(theta)])
    radial = -np.array([np.cos(theta), np.sin(theta)])

    fig = Figure(figsize=(4, 4.8), layout="constrained")
    ax = fig.subplots()
    angulos = np.linspace(0, 2 * np.pi, 200)
    ax.plot(r * np.cos(angulos), r * np.sin(angulos), color=GRIS_CLARO, lw=1.5)
    ax.plot([0, x], [0, y], color=GRIS_CLARO, lw=1)
    ax.plot(0, 0, "o", color=GRIS, ms=5)
    if w_max > 0:
        flecha(ax, x, y, *(0.6 * r * w / w_max * tangente), NARANJA)
    if a_max > 0:
        flecha(ax, x, y, *(0.6 * r * w**2 * r / a_max * radial), VERDE)
        flecha(ax, x, y, *(0.6 * r * alfa * r / a_max * tangente), MORADO)
    ax.plot(x, y, "o", color=AZUL, ms=13, zorder=5)
    ax.set_aspect("equal")
    ax.set_xlim(-1.7 * r, 1.7 * r)
    ax.set_ylim(-1.7 * r, 1.7 * r)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title(f"t = {instante:.2f} s")
    handles = [
        Line2D([], [], color=NARANJA, label="Velocidad"),
        Line2D([], [], color=VERDE, label="Aceleración centrípeta"),
    ]
    if alfa != 0:
        handles.append(Line2D([], [], color=MORADO, label="Aceleración tangencial"))
    fig.legend(handles=handles, loc="outside lower center")
    return fig


def figura_graficas(r, w0, alfa, t_final, instante):
    t = np.linspace(0, t_final, 400)
    theta, w = movimiento_circular(w0, alfa, t)
    thi, wi = movimiento_circular(w0, alfa, instante)

    fig = Figure(figsize=(6, 6), layout="constrained")
    ejes = fig.subplots(3, 1, sharex=True)
    ejes[0].plot(t, theta, color=AZUL)
    ejes[0].plot(instante, thi, "o", color=AZUL, ms=9, mec="white", mew=2)
    ejes[0].set_ylabel("θ (rad)")
    ejes[0].set_title("Posición angular vs tiempo")
    ejes[1].plot(t, w, color=AZUL)
    ejes[1].plot(instante, wi, "o", color=AZUL, ms=9, mec="white", mew=2)
    ejes[1].set_ylabel("ω (rad/s)")
    ejes[1].set_title("Velocidad angular vs tiempo")
    ejes[1].set_ylim(min(w.min(), 0) - 0.5, max(w.max(), 0) + 0.5)
    ejes[2].plot(t, w**2 * r, color=VERDE, label="Centrípeta")
    ejes[2].plot(t, np.full_like(t, alfa * r), color=MORADO, label="Tangencial")
    ejes[2].plot(instante, wi**2 * r, "o", color=VERDE, ms=9, mec="white", mew=2)
    ejes[2].set_ylabel("a (m/s²)")
    ejes[2].set_title("Aceleración vs tiempo")
    ejes[2].set_xlabel("Tiempo t (s)")
    fig.legend(loc="outside lower center", ncols=2)
    return fig


def mostrar():
    st.header("Movimiento circular")
    tipo = st.radio("Tipo de movimiento", ["Uniforme (MCU)", "Uniformemente acelerado (MCUA)"], horizontal=True)
    uniforme = tipo == "Uniforme (MCU)"

    st.sidebar.header("Parámetros")
    r = st.sidebar.slider("Radio r (m)", 0.5, 10.0, 2.0, 0.1)
    if uniforme:
        w0 = st.sidebar.slider("Velocidad angular ω (rad/s)", 0.1, 10.0, 1.5, 0.1)
        alfa = 0.0
    else:
        w0 = st.sidebar.slider("Velocidad angular inicial ω₀ (rad/s)", 0.0, 10.0, 0.5, 0.1)
        alfa = st.sidebar.slider("Aceleración angular α (rad/s²)", -2.0, 2.0, 0.3, 0.05)
    t_final = st.sidebar.slider("Tiempo total (s)", 1.0, 30.0, 10.0, 0.5)

    theta_f, w_f = movimiento_circular(w0, alfa, t_final)
    if uniforme:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Periodo T", f"{periodo(w0):.3f} s", border=True)
        c2.metric("Frecuencia f", f"{w0 / (2 * np.pi):.3f} Hz", border=True)
        c3.metric("Velocidad tangencial v", f"{w0 * r:.2f} m/s", border=True)
        c4.metric("Aceleración centrípeta", f"{w0**2 * r:.2f} m/s²", border=True)
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Velocidad angular final", f"{w_f:.2f} rad/s", border=True)
        c2.metric("Vueltas", f"{theta_f / (2 * np.pi):.2f}", border=True)
        c3.metric("Velocidad tangencial final", f"{w_f * r:.2f} m/s", border=True)
        c4, c5, c6 = st.columns(3)
        c4.metric("Aceleración centrípeta final", f"{w_f**2 * r:.2f} m/s²", border=True)
        c5.metric("Aceleración tangencial", f"{alfa * r:.2f} m/s²", border=True)
        c6.metric("Aceleración total final", f"{np.hypot(w_f**2 * r, alfa * r):.2f} m/s²", border=True)

    izq, der = st.columns([2, 3], gap="large")
    instante, animado, lugar = controles_tiempo(izq, t_final)
    izq.caption("Las flechas muestran la dirección de la velocidad y de las aceleraciones en el instante t.")
    der.pyplot(figura_graficas(r, w0, alfa, t_final, instante))
    mostrar_escena(lugar, partial(figura_escena, r, w0, alfa, t_final), instante, t_final, animado)
