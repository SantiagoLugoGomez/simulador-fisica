from functools import partial

import numpy as np
import streamlit as st
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

from sims.comun import AZUL, GRIS, GRIS_CLARO, NARANJA, VERDE, controles_tiempo, mostrar_escena


def resorte(m, k, amplitud, t):
    w = np.sqrt(k / m)
    t = np.asarray(t, dtype=float)
    x = amplitud * np.cos(w * t)
    v = -amplitud * w * np.sin(w * t)
    return x, v, m * v**2 / 2, k * x**2 / 2


def pendulo(largo, theta0, g, t):
    def derivada(estado):
        return np.array([estado[1], -g / largo * np.sin(estado[0])])

    estados = np.empty((len(t), 2))
    estados[0] = theta0, 0.0
    for i, h in enumerate(np.diff(t)):
        y = estados[i]
        k1 = derivada(y)
        k2 = derivada(y + h / 2 * k1)
        k3 = derivada(y + h / 2 * k2)
        k4 = derivada(y + h * k3)
        estados[i + 1] = y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return estados[:, 0], estados[:, 1]


def energias_pendulo(m, largo, g, theta, w):
    return m * (largo * w) ** 2 / 2, m * g * largo * (1 - np.cos(theta))


def periodo_pendulo(largo, theta0, g):
    a, b = 1.0, np.cos(theta0 / 2)
    for _ in range(20):
        a, b = (a + b) / 2, np.sqrt(a * b)
    return 2 * np.pi * np.sqrt(largo / g) / a


def figura_resorte(m, k, amplitud, instante):
    x = resorte(m, k, amplitud, instante)[0]
    lado = 0.6 * amplitud
    pared = -2.5 * amplitud
    puntos = np.linspace(pared, x - lado / 2, 24)
    zigzag = np.zeros_like(puntos)
    zigzag[2:-2] = 0.12 * amplitud * np.where(np.arange(2, len(puntos) - 2) % 2 == 0, 1, -1)

    fig = Figure(figsize=(10, 2.4), layout="constrained")
    ax = fig.subplots()
    ax.plot([pared, 1.6 * amplitud], [0, 0], color=GRIS, lw=1.5)
    ax.plot([pared, pared], [0, 1.5 * lado], color=GRIS, lw=3)
    ax.axvline(0, color=GRIS_CLARO, lw=1, ls="--")
    ax.plot(puntos, lado / 2 + zigzag, color=GRIS, lw=1.5)
    ax.add_patch(Rectangle((x - lado / 2, 0), lado, lado, fc=AZUL, ec="white", lw=1.5, zorder=3))
    ax.set_aspect("equal")
    ax.set_xlim(pared - 0.1 * amplitud, 1.6 * amplitud)
    ax.set_ylim(-0.1 * amplitud, 1.6 * lado)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("Posición x (m)")
    ax.set_title(f"t = {instante:.2f} s")
    return fig


def figura_pendulo(largo, t, theta, instante):
    th = np.interp(instante, t, theta)
    th0 = np.abs(theta).max()
    arco = np.linspace(-th0, th0, 200)
    x, y = largo * np.sin(th), -largo * np.cos(th)

    fig = Figure(figsize=(10, 3.8), layout="constrained")
    ax = fig.subplots()
    ax.plot([-0.3 * largo, 0.3 * largo], [0, 0], color=GRIS, lw=3)
    ax.plot(largo * np.sin(arco), -largo * np.cos(arco), color=GRIS_CLARO, lw=1, ls="--")
    ax.plot([0, x], [0, y], color=GRIS, lw=1.5)
    ax.plot(x, y, "o", color=AZUL, ms=18, zorder=5)
    ax.set_aspect("equal")
    ax.set_xlim(-1.2 * largo, 1.2 * largo)
    ax.set_ylim(-1.2 * largo, max(0.2 * largo, -largo * np.cos(th0) + 0.2 * largo))
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title(f"t = {instante:.2f} s")
    return fig


def figura_energias(t, posicion, K, U, instante, etiqueta):
    Ki, Ui, xi = (np.interp(instante, t, y) for y in (K, U, posicion))

    fig = Figure(figsize=(10, 3.8), layout="constrained")
    ejes = fig.subplots(1, 2)
    for ax, x, marca in [(ejes[0], t, instante), (ejes[1], posicion, xi)]:
        ax.plot(x, K, color=AZUL, label="Cinética K")
        ax.plot(x, U, color=NARANJA, label="Potencial U")
        ax.plot(x, K + U, color=VERDE, label="Total E")
        ax.plot(marca, Ki, "o", color=AZUL, ms=9, mec="white", mew=2)
        ax.plot(marca, Ui, "o", color=NARANJA, ms=9, mec="white", mew=2)
        ax.set_ylabel("Energía (J)")
    ejes[0].set_title("Energía vs tiempo")
    ejes[0].set_xlabel("Tiempo t (s)")
    ejes[1].set_title("Energía vs posición")
    ejes[1].set_xlabel(etiqueta)
    fig.legend(*ejes[0].get_legend_handles_labels(), loc="outside lower center", ncols=3)
    return fig


def mostrar():
    st.header("Conservación de la energía")
    sistema = st.radio("Sistema", ["Masa-resorte", "Péndulo simple"], horizontal=True)

    st.sidebar.header("Parámetros")
    m = st.sidebar.slider("Masa m (kg)", 0.1, 10.0, 1.0, 0.1)
    if sistema == "Masa-resorte":
        st.caption("Resorte ideal sin fricción. La masa se suelta desde el reposo en x = A.")
        c1, c2, c3, c4 = st.columns(4)
        k = st.sidebar.slider("Constante del resorte k (N/m)", 1.0, 200.0, 20.0, 1.0)
        amplitud = st.sidebar.slider("Amplitud A (m)", 0.05, 2.0, 0.5, 0.05)
        t_final = st.sidebar.slider("Tiempo total (s)", 1.0, 30.0, 5.0, 0.5)
        t = np.linspace(0, t_final, 1000)
        posicion, _, K, U = resorte(m, k, amplitud, t)
        w = np.sqrt(k / m)
        c1.metric("Frecuencia angular ω", f"{w:.3f} rad/s", border=True)
        c2.metric("Periodo T", f"{2 * np.pi / w:.3f} s", border=True)
        c3.metric("Energía total E", f"{k * amplitud**2 / 2:.3f} J", border=True)
        c4.metric("Rapidez máxima", f"{amplitud * w:.3f} m/s", border=True)
        dibujar = partial(figura_resorte, m, k, amplitud)
        etiqueta = "Posición x (m)"
    else:
        st.caption("Péndulo sin fricción resuelto numéricamente (Runge-Kutta 4), válido también para ángulos grandes. "
                   "Se suelta desde el reposo en θ = θ₀.")
        c1, c2, c3, c4 = st.columns(4)
        largo = st.sidebar.slider("Longitud L (m)", 0.2, 5.0, 1.0, 0.1)
        angulo0 = st.sidebar.slider("Ángulo inicial θ₀ (°)", 1.0, 170.0, 30.0, 1.0)
        g = st.sidebar.slider("Gravedad g (m/s²)", 1.0, 25.0, 9.81, 0.01)
        t_final = st.sidebar.slider("Tiempo total (s)", 1.0, 30.0, 5.0, 0.5)
        theta0 = np.radians(angulo0)
        t = np.linspace(0, t_final, int(t_final * 200) + 1)
        posicion, w = pendulo(largo, theta0, g, t)
        K, U = energias_pendulo(m, largo, g, posicion, w)
        c1.metric("Periodo T", f"{periodo_pendulo(largo, theta0, g):.3f} s", border=True,
                  help="Periodo exacto para la amplitud θ₀, calculado con la integral elíptica completa.")
        c2.metric("Periodo aproximado T₀", f"{2 * np.pi * np.sqrt(largo / g):.3f} s", border=True,
                  help="T₀ = 2π√(L/g), aproximación válida solo para ángulos pequeños.")
        c3.metric("Energía total E", f"{m * g * largo * (1 - np.cos(theta0)):.3f} J", border=True)
        c4.metric("Rapidez máxima", f"{np.sqrt(2 * g * largo * (1 - np.cos(theta0))):.3f} m/s", border=True)
        dibujar = partial(figura_pendulo, largo, t, posicion)
        etiqueta = "Ángulo θ (rad)"

    E = K + U
    instante, animado, lugar = controles_tiempo(st, t_final)
    st.pyplot(figura_energias(t, posicion, K, U, instante, etiqueta))
    st.caption(f"La energía total se mantiene constante: su variación relativa durante la simulación es "
                f"{(E.max() - E.min()) / E[0]:.1e}.")
    mostrar_escena(lugar, dibujar, instante, t_final, animado)
