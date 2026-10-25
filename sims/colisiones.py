from functools import partial

import numpy as np
import streamlit as st
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

from sims.comun import AZUL, GRIS, NARANJA, VERDE, controles_tiempo, flecha, mostrar_escena

T_FINAL = 4.0


def velocidades_finales(m1, m2, v1, v2, e):
    p = m1 * v1 + m2 * v2
    u1 = (p + m2 * e * (v2 - v1)) / (m1 + m2)
    u2 = (p + m1 * e * (v1 - v2)) / (m1 + m2)
    return u1, u2


def simular(m1, m2, v1, v2, e, t):
    t = np.asarray(t, dtype=float)
    choque = v1 > v2
    u1, u2 = velocidades_finales(m1, m2, v1, v2, e) if choque else (v1, v2)
    t_choque = T_FINAL / 2 if choque else 0.0
    antes = t < t_choque
    vel1 = np.where(antes, v1, u1)
    vel2 = np.where(antes, v2, u2)
    return vel1 * (t - t_choque), vel2 * (t - t_choque), vel1, vel2


def figura_escena(m1, m2, v1, v2, e, instante):
    x1, x2, _, _ = simular(m1, m2, v1, v2, e, np.linspace(0, T_FINAL, 200))
    rango = max(x2.max() - x1.min(), 1.0)
    lados = 0.12 * rango * np.cbrt(np.array([m1, m2]) / max(m1, m2))
    p1, p2, w1, w2 = simular(m1, m2, v1, v2, e, instante)
    centros = [p1 - lados[0] / 2, p2 + lados[1] / 2]
    escala = 0.12 * rango / max(abs(v1), abs(v2), 1e-9)

    fig = Figure(figsize=(10, 2.6), layout="constrained")
    ax = fig.subplots()
    ax.axhline(0, color=GRIS, lw=1.5)
    for centro, lado, v, color in zip(centros, lados, [w1, w2], [AZUL, NARANJA]):
        ax.add_patch(Rectangle((centro - lado / 2, 0), lado, lado, fc=color, ec="white", lw=1.5, zorder=3))
        flecha(ax, centro, lado + 0.04 * rango, escala * v, 0, color)
    ax.set_aspect("equal")
    ax.set_xlim(x1.min() - lados[0] - 0.2 * rango, x2.max() + lados[1] + 0.2 * rango)
    ax.set_ylim(-0.02 * rango, lados.max() + 0.12 * rango)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("Posición x (m)")
    ax.set_title(f"t = {instante:.2f} s")
    fig.legend(handles=[Line2D([], [], color=AZUL, lw=8, label=f"Bloque 1 (m₁ = {m1:.1f} kg)"),
                        Line2D([], [], color=NARANJA, lw=8, label=f"Bloque 2 (m₂ = {m2:.1f} kg)")],
               loc="outside lower center", ncols=2)
    return fig


def figura_graficas(m1, m2, v1, v2, e, instante):
    t = np.linspace(0, T_FINAL, 801)
    x1, x2, w1, w2 = simular(m1, m2, v1, v2, e, t)
    p1, p2 = m1 * w1, m2 * w2
    k1, k2 = m1 * w1**2 / 2, m2 * w2**2 / 2
    paneles = [
        ("Posición vs tiempo", "x (m)", x1, x2, None),
        ("Velocidad vs tiempo", "v (m/s)", w1, w2, None),
        ("Momento lineal vs tiempo", "p (kg·m/s)", p1, p2, p1 + p2),
        ("Energía cinética vs tiempo", "K (J)", k1, k2, k1 + k2),
    ]

    fig = Figure(figsize=(10, 5.5), layout="constrained")
    ejes = fig.subplots(2, 2, sharex=True).ravel()
    for ax, (titulo, etiqueta, y1, y2, total) in zip(ejes, paneles):
        ax.plot(t, y1, color=AZUL, label="Bloque 1")
        ax.plot(t, y2, color=NARANJA, label="Bloque 2")
        if total is not None:
            ax.plot(t, total, color=VERDE, label="Total")
        ax.axvline(instante, color=GRIS, lw=1, ls=":")
        ax.set_title(titulo)
        ax.set_ylabel(etiqueta)
    for ax in ejes[2:]:
        ax.set_xlabel("Tiempo t (s)")
    fig.legend(*ejes[2].get_legend_handles_labels(), loc="outside lower center", ncols=3)
    return fig


def mostrar():
    st.header("Colisiones en una dimensión")
    tipo = st.radio("Tipo de colisión", ["Elástica", "Inelástica", "Perfectamente inelástica"], horizontal=True)
    st.caption("El bloque 1 está a la izquierda y el bloque 2 a la derecha. Las velocidades son positivas hacia la "
               "derecha. No hay fuerzas externas, por lo que el momento lineal total se conserva.")

    st.sidebar.header("Parámetros")
    m1 = st.sidebar.slider("Masa del bloque 1 m₁ (kg)", 0.1, 20.0, 2.0, 0.1)
    m2 = st.sidebar.slider("Masa del bloque 2 m₂ (kg)", 0.1, 20.0, 1.0, 0.1)
    v1 = st.sidebar.slider("Velocidad inicial del bloque 1 v₁ (m/s)", -20.0, 20.0, 4.0, 0.5)
    v2 = st.sidebar.slider("Velocidad inicial del bloque 2 v₂ (m/s)", -20.0, 20.0, -2.0, 0.5)
    if tipo == "Elástica":
        e = 1.0
    elif tipo == "Perfectamente inelástica":
        e = 0.0
    else:
        e = st.sidebar.slider("Coeficiente de restitución e", 0.0, 1.0, 0.5, 0.05,
                              help="e = 1: elástica; e = 0: perfectamente inelástica.")

    if v1 > v2:
        u1, u2 = velocidades_finales(m1, m2, v1, v2, e)
    else:
        st.info("Con estas velocidades los bloques no se acercan, así que no chocan.")
        u1, u2 = v1, v2
    p_antes, p_despues = m1 * v1 + m2 * v2, m1 * u1 + m2 * u2
    k_antes, k_despues = (m1 * v1**2 + m2 * v2**2) / 2, (m1 * u1**2 + m2 * u2**2) / 2
    perdida = k_antes - k_despues

    c1, c2, c3 = st.columns(3)
    c1.metric("Velocidad final bloque 1", f"{u1:.2f} m/s", border=True)
    c2.metric("Velocidad final bloque 2", f"{u2:.2f} m/s", border=True)
    c3.metric("Energía cinética perdida", f"{100 * perdida / k_antes if k_antes > 0 else 0:.1f} %", border=True,
              help="Porcentaje de la energía cinética inicial que se transforma en calor, sonido o deformación.")
    c4, c5, c6 = st.columns(3)
    c4.metric("Momento total antes", f"{p_antes:.2f} kg·m/s", border=True)
    c5.metric("Momento total después", f"{p_despues:.2f} kg·m/s", border=True)
    c6.metric("Energía cinética antes → después", f"{k_antes:.2f} J → {k_despues:.2f} J", border=True)

    instante, animado, lugar = controles_tiempo(st, T_FINAL)
    st.pyplot(figura_graficas(m1, m2, v1, v2, e, instante))
    st.caption("La línea punteada vertical marca el instante t. La línea verde del momento total es horizontal: "
               "el momento se conserva en el choque.")
    mostrar_escena(lugar, partial(figura_escena, m1, m2, v1, v2, e), instante, T_FINAL, animado)
