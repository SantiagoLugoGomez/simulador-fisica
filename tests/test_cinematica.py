import numpy as np
import pytest

from sims.cinematica import altura_maxima, movimiento, tiempo_caida

G = 9.81


def test_mru_posicion_lineal_y_velocidad_constante():
    t = np.linspace(0, 10, 50)
    x, v, a = movimiento(3.0, 2.5, 0.0, t)
    assert np.allclose(x, 3.0 + 2.5 * t)
    assert np.allclose(v, 2.5)
    assert np.allclose(a, 0.0)


def test_mrua_cumple_la_ecuacion_de_torricelli():
    x0, v0, a = 1.0, 4.0, -1.5
    x, v, _ = movimiento(x0, v0, a, np.linspace(0, 8, 100))
    assert np.allclose(v**2, v0**2 + 2 * a * (x - x0))


def test_mrua_velocidad_es_la_derivada_de_la_posicion():
    t = np.linspace(0, 5, 5001)
    x, v, _ = movimiento(0.0, 3.0, 2.0, t)
    assert np.allclose(np.gradient(x, t)[1:-1], v[1:-1])


def test_caida_libre_desde_el_reposo():
    h = 20.0
    t = tiempo_caida(h, 0.0, G)
    _, v, _ = movimiento(h, 0.0, -G, t)
    assert t == pytest.approx(np.sqrt(2 * h / G))
    assert v == pytest.approx(-np.sqrt(2 * G * h))


def test_lanzamiento_vertical_hacia_arriba():
    h, v0 = 10.0, 15.0
    t = tiempo_caida(h, v0, G)
    y, v, _ = movimiento(h, v0, -G, t)
    assert altura_maxima(h, v0, G) == pytest.approx(h + v0**2 / (2 * G))
    assert y == pytest.approx(0.0, abs=1e-9)
    assert abs(v) == pytest.approx(np.sqrt(v0**2 + 2 * G * h))


def test_lanzamiento_hacia_abajo_no_sube():
    assert altura_maxima(30.0, -5.0, G) == 30.0
