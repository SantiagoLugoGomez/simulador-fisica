from functools import partial

import numpy as np
import streamlit as st
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon

from sims.comun import AZUL, GRIS, GRIS_CLARO, MORADO, NARANJA, VERDE, controles_tiempo, flecha, mostrar_escena


def plano_inclinado(m, angulo, mu_s, mu_k, g):
    th = np.radians(angulo)
    normal = m * g * np.cos(th)
    paralela = m * g * np.sin(th)
    if paralela <= mu_s * normal:
        return normal, paralela, 0.0, False
    friccion = mu_k * normal
    return normal, friccion, (paralela - friccion) / m, True


def angulo_critico(mu_s):
    return np.degrees(np.arctan(mu_s))


def figura_escena(m, angulo, mu_s, mu_k, g, largo, instante):
    normal, friccion, a, _ = plano_inclinado(m, angulo, mu_s, mu_k, g)
    th = np.radians(angulo)
    lado = 0.1 * largo
    total = largo + lado
    abajo = np.array([np.cos(th), -np.sin(th)])
    fuera = np.array([np.sin(th), np.cos(th)])
    cima = np.array([0.0, total * np.sin(th)])
    s = a * instante**2 / 2
    centro = cima + (s + lado / 2) * abajo + lado / 2 * fuera
    esquinas = [centro + i * lado / 2 * abajo + j * lado / 2 * fuera for i, j in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]
    escala = 0.4 * largo / (m * g)

    fig = Figure(figsize=(5, 4.8), layout="constrained")
    ax = fig.subplots()
    base = total * np.cos(th)
    ax.add_patch(Polygon([[0, 0], [base, 0], cima], closed=True, fc="#f3f3f1", ec=GRIS_CLARO, lw=1.5))
    ax.add_patch(Polygon(esquinas, closed=True, fc=AZUL, ec="white", lw=1.5, zorder=3))
    fuerzas = [
        (np.array([0.0, -m * g]), GRIS, f"Peso: {m * g:.1f} N"),
        (normal * fuera, VERDE, f"Normal: {normal:.1f} N"),
        (-friccion * abajo, NARANJA, f"Fricción: {friccion:.1f} N"),
        (m * a * abajo, MORADO, f"Fuerza neta: {m * a:.1f} N"),
    ]
    for vector, color, _ in fuerzas:
        flecha(ax, *centro, *(escala * vector), color)
    ax.set_aspect("equal")
    ax.set_xlim(-0.5 * largo, base + 0.45 * largo)
    ax.set_ylim(-0.45 * largo, total * np.sin(th) + 0.55 * largo)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title(f"Diagrama de fuerzas, t = {instante:.2f} s")
    fig.legend(handles=[Line2D([], [], color=c, label=etiqueta) for _, c, etiqueta in fuerzas],
               loc="outside lower center", ncols=2)
    return fig


def figura_graficas(m, angulo, mu_s, mu_k, g):
    angulos = np.linspace(0, 89, 400)
    datos = np.array([plano_inclinado(m, th, mu_s, mu_k, g)[1:3] for th in angulos])
    friccion, a, _ = plano_inclinado(m, angulo, mu_s, mu_k, g)[1:]
    critico = angulo_critico(mu_s)

    fig = Figure(figsize=(5, 5), layout="constrained")
    ejes = fig.subplots(2, 1, sharex=True)
    for ax, y, yi, etiqueta, titulo in [
        (ejes[0], datos[:, 0], friccion, "f (N)", "Fuerza de fricción vs ángulo"),
        (ejes[1], datos[:, 1], a, "a (m/s²)", "Aceleración del bloque vs ángulo"),
    ]:
        ax.plot(angulos, y, color=AZUL)
        ax.axvline(critico, color=GRIS_CLARO, lw=1, ls="--")
        ax.plot(angulo, yi, "o", color=AZUL, ms=9, mec="white", mew=2)
        ax.set_ylabel(etiqueta)
        ax.set_title(titulo)
    ejes[1].set_xlabel("Ángulo del plano θ (°)")
    return fig


def mostrar():
    st.header("Dinámica: bloque en un plano inclinado")
    st.caption("El bloque parte del reposo en lo alto del plano. Si la componente del peso paralela al plano "
               "supera la fricción estática máxima, desliza con fricción cinética.")

    st.sidebar.header("Parámetros")
    m = st.sidebar.slider("Masa m (kg)", 0.5, 50.0, 5.0, 0.5)
    angulo = st.sidebar.slider("Ángulo del plano θ (°)", 0.0, 85.0, 35.0, 0.5)
    mu_s = st.sidebar.slider("Coeficiente de fricción estática μₛ", 0.0, 1.5, 0.5, 0.01)
    mu_k = st.sidebar.slider("Coeficiente de fricción cinética μₖ", 0.0, 1.5, 0.3, 0.01)
    largo = st.sidebar.slider("Longitud del plano L (m)", 1.0, 20.0, 5.0, 0.5)
    g = st.sidebar.slider("Gravedad g (m/s²)", 1.0, 25.0, 9.81, 0.01)
    if mu_k > mu_s:
        st.sidebar.warning("μₖ no puede superar a μₛ; se usa μₖ = μₛ.")
        mu_k = mu_s

    normal, friccion, a, desliza = plano_inclinado(m, angulo, mu_s, mu_k, g)
    critico = angulo_critico(mu_s)
    if desliza:
        st.write(f"**El bloque desliza** porque θ supera el ángulo crítico de {critico:.1f}°; actúa la fricción cinética.")
    else:
        st.write(f"**El bloque permanece en reposo**: la fricción estática equilibra el peso paralelo al plano "
                 f"(θ ≤ {critico:.1f}°).")

    c1, c2, c3 = st.columns(3)
    c1.metric("Fuerza normal", f"{normal:.2f} N", border=True)
    c2.metric(f"Fricción {'cinética' if desliza else 'estática'}", f"{friccion:.2f} N", border=True)
    c3.metric("Aceleración", f"{a:.2f} m/s²", border=True)
    c4, c5, c6 = st.columns(3)
    c4.metric("Ángulo crítico", f"{critico:.1f}°", border=True)
    c5.metric("Tiempo hasta la base", f"{np.sqrt(2 * largo / a):.2f} s" if desliza else "—", border=True)
    c6.metric("Rapidez en la base", f"{np.sqrt(2 * a * largo):.2f} m/s" if desliza else "—", border=True)

    izq, der = st.columns(2, gap="large")
    if desliza:
        t_final = np.sqrt(2 * largo / a)
        instante, animado, lugar = controles_tiempo(izq, t_final)
    else:
        t_final, instante, animado, lugar = 0.0, 0.0, False, izq.empty()
    izq.caption("Las flechas parten del centro del bloque y su longitud es proporcional a la magnitud de cada fuerza.")
    der.pyplot(figura_graficas(m, angulo, mu_s, mu_k, g))
    der.caption("La línea discontinua marca el ángulo crítico θc = arctan(μₛ); el punto, el ángulo actual.")
    mostrar_escena(lugar, partial(figura_escena, m, angulo, mu_s, mu_k, g, largo), instante, t_final, animado)
