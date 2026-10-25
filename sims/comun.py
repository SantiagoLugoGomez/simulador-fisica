import io

import matplotlib as mpl
import numpy as np
from matplotlib.patches import FancyArrowPatch

AZUL = "#2a78d6"
NARANJA = "#eb6834"
VERDE = "#1baf7a"
MORADO = "#6250d6"
GRIS = "#52514e"
GRIS_CLARO = "#b5b4ae"
COLORES = [AZUL, NARANJA, VERDE, "#eda100", "#e87ba4", "#008300", MORADO, "#e34948"]

mpl.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": GRIS_CLARO,
    "axes.labelcolor": GRIS,
    "axes.titlecolor": "#0b0b0b",
    "axes.titlesize": 11,
    "axes.titlelocation": "left",
    "axes.labelsize": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "axes.prop_cycle": mpl.cycler(color=COLORES),
    "grid.color": "#ececea",
    "grid.linewidth": 0.8,
    "xtick.color": GRIS,
    "ytick.color": GRIS,
    "legend.frameon": False,
    "legend.fontsize": 9,
    "lines.linewidth": 2,
    "font.size": 10,
})


def flecha(ax, x, y, dx, dy, color):
    if dx == 0 and dy == 0:
        return
    ax.add_patch(FancyArrowPatch((x, y), (x + dx, y + dy), arrowstyle="-|>", mutation_scale=14,
                                 color=color, lw=2, zorder=4))


def controles_tiempo(columna, t_final):
    instante = columna.slider("Instante t (s)", 0.0, float(t_final), 0.0, format="%.2f")
    animado = columna.button("Animar")
    return instante, animado, columna.empty()


def a_png(fig):
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=200)
    return buffer


def mostrar_escena(lugar, dibujar, instante, t_final, animado):
    tiempos = np.linspace(0, t_final, int(min(t_final * 8, 120)) + 1) if animado else [instante]
    for t in tiempos:
        lugar.image(a_png(dibujar(t)), width="stretch")
