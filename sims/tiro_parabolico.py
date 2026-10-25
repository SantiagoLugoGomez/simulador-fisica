from functools import partial

import numpy as np
import streamlit as st
from matplotlib.figure import Figure

from sims.comun import AZUL, COLORES, GRIS, GRIS_CLARO, NARANJA, controles_tiempo, flecha, mostrar_escena

ANGULOS_COMPARACION = [10, 20, 30, 45, 60, 70, 80]


def resultados(v0, angulo, h0, g):
    th = np.radians(angulo)
    vx, vy = v0 * np.cos(th), v0 * np.sin(th)
    t_vuelo = (vy + np.sqrt(vy**2 + 2 * g * h0)) / g
    return t_vuelo, vx * t_vuelo, h0 + vy**2 / (2 * g)


def trayectoria(v0, angulo, h0, g, t):
    th = np.radians(angulo)
    t = np.asarray(t, dtype=float)
    x = v0 * np.cos(th) * t
    y = h0 + v0 * np.sin(th) * t - g * t**2 / 2
    vx = np.full_like(t, v0 * np.cos(th))
    vy = v0 * np.sin(th) - g * t
    return x, y, vx, vy


def figura_escena(v0, angulo, h0, g, instante):
    t_vuelo, alcance, altura = resultados(v0, angulo, h0, g)
    x, y, _, _ = trayectoria(v0, angulo, h0, g, np.linspace(0, t_vuelo, 300))
    xr, yr, _, _ = trayectoria(v0, angulo, h0, g, np.linspace(0, instante, 300))
    xi, yi, vxi, vyi = trayectoria(v0, angulo, h0, g, instante)
    escala = 0.15 * max(alcance, altura) / v0

    fig = Figure(figsize=(6, 3.6), layout="constrained")
    ax = fig.subplots()
    ax.plot(x, y, color=GRIS_CLARO, lw=1.5, ls="--")
    ax.plot(xr, yr, color=AZUL)
    ax.plot(xi, yi, "o", color=AZUL, ms=11, zorder=5)
    flecha(ax, xi, yi, escala * vxi, escala * vyi, NARANJA)
    ax.set_aspect("equal")
    ax.axhline(0, color=GRIS, lw=1)
    ax.set_xlim(-0.05 * alcance - 1, alcance + 0.2 * max(alcance, altura) + 1)
    ax.set_ylim(-0.12 * max(alcance, altura), 1.15 * altura + 0.5)
    ax.set_xlabel("Posición horizontal x (m)")
    ax.set_ylabel("Altura y (m)")
    ax.set_title(f"Trayectoria, t = {instante:.2f} s")
    return fig


def figura_velocidades(v0, angulo, h0, g, instante):
    t_vuelo, _, _ = resultados(v0, angulo, h0, g)
    t = np.linspace(0, t_vuelo, 300)
    _, _, vx, vy = trayectoria(v0, angulo, h0, g, t)
    _, _, vxi, vyi = trayectoria(v0, angulo, h0, g, instante)

    fig = Figure(figsize=(4, 4.4), layout="constrained")
    ejes = fig.subplots(2, 1, sharex=True)
    for ax, y, yi, etiqueta, titulo in [
        (ejes[0], vx, vxi, "$v_x$ (m/s)", "Velocidad horizontal vs tiempo"),
        (ejes[1], vy, vyi, "$v_y$ (m/s)", "Velocidad vertical vs tiempo"),
    ]:
        ax.plot(t, y, color=AZUL)
        ax.plot(instante, yi, "o", color=AZUL, ms=9, mec="white", mew=2)
        ax.set_ylabel(etiqueta)
        ax.set_title(titulo)
    ejes[0].set_ylim(0, v0 * 1.1 + 0.1)
    ejes[1].axhline(0, color=GRIS_CLARO, lw=1)
    ejes[1].set_xlabel("Tiempo t (s)")
    return fig


def figura_comparacion(v0, angulos, h0, g):
    fig = Figure(figsize=(10, 4), layout="constrained")
    ax = fig.subplots()
    for angulo in angulos:
        t_vuelo, _, _ = resultados(v0, angulo, h0, g)
        x, y, _, _ = trayectoria(v0, angulo, h0, g, np.linspace(0, t_vuelo, 300))
        color = COLORES[ANGULOS_COMPARACION.index(angulo)]
        ax.plot(x, y, color=color, label=f"{angulo}°")
    ax.set_aspect("equal")
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Posición horizontal x (m)")
    ax.set_ylabel("Altura y (m)")
    ax.set_title("Trayectorias para distintos ángulos de lanzamiento")
    fig.legend(loc="outside right upper", title="Ángulo")
    return fig


def mostrar():
    st.header("Tiro parabólico")
    st.caption("Lanzamiento sin resistencia del aire desde una altura inicial h₀.")

    st.sidebar.header("Parámetros")
    v0 = st.sidebar.slider("Velocidad inicial v₀ (m/s)", 1.0, 60.0, 20.0, 0.5)
    angulo = st.sidebar.slider("Ángulo de lanzamiento θ (°)", 0.0, 90.0, 45.0, 1.0)
    h0 = st.sidebar.slider("Altura inicial h₀ (m)", 0.0, 50.0, 0.0, 0.5)
    g = st.sidebar.slider("Gravedad g (m/s²)", 1.0, 25.0, 9.81, 0.01)

    t_vuelo, alcance, altura = resultados(v0, angulo, h0, g)
    if t_vuelo == 0:
        st.info("Con ángulo de 0° y altura inicial de 0 m el proyectil no despega del suelo.")
        return

    _, _, vxf, vyf = trayectoria(v0, angulo, h0, g, t_vuelo)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tiempo de vuelo", f"{t_vuelo:.2f} s", border=True)
    c2.metric("Alcance", f"{alcance:.2f} m", border=True)
    c3.metric("Altura máxima", f"{altura:.2f} m", border=True)
    c4.metric("Rapidez de impacto", f"{np.hypot(vxf, vyf):.2f} m/s", border=True)

    izq, der = st.columns([3, 2], gap="large")
    instante, animado, lugar = controles_tiempo(izq, t_vuelo)
    izq.caption("Línea discontinua: trayectoria completa. Flecha naranja: velocidad en el instante t.")
    der.pyplot(figura_velocidades(v0, angulo, h0, g, instante))
    mostrar_escena(lugar, partial(figura_escena, v0, angulo, h0, g), instante, t_vuelo, animado)

    st.subheader("Comparar varios ángulos")
    angulos = st.multiselect("Ángulos a comparar (°)", ANGULOS_COMPARACION, default=[20, 30, 45, 60, 70],
                             help="Los ángulos complementarios (por ejemplo 30° y 60°) tienen el mismo alcance "
                                  "cuando h₀ = 0.")
    if angulos:
        angulos = sorted(angulos)
        st.pyplot(figura_comparacion(v0, angulos, h0, g))
        filas = [resultados(v0, a, h0, g) for a in angulos]
        columnas = ["Tiempo de vuelo (s)", "Alcance (m)", "Altura máxima (m)"]
        tabla = {"Ángulo (°)": angulos} | {c: [f[i] for f in filas] for i, c in enumerate(columnas)}
        st.dataframe(tabla, hide_index=True,
                     column_config={c: st.column_config.NumberColumn(format="%.2f") for c in columnas})
