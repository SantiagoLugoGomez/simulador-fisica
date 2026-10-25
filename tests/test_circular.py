import numpy as np
import pytest

from sims.circular import movimiento_circular, periodo, posicion


def derivadas(x, y, t):
    vx, vy = np.gradient(x, t), np.gradient(y, t)
    return vx, vy, np.gradient(vx, t), np.gradient(vy, t)


def test_mcu_rapidez_y_aceleracion_centripeta():
    r, w = 2.0, 3.0
    t = np.linspace(0, periodo(w), 20001)
    theta, _ = movimiento_circular(w, 0.0, t)
    x, y = posicion(r, theta)
    vx, vy, ax, ay = derivadas(x, y, t)
    centro = slice(5, -5)
    assert theta[-1] == pytest.approx(2 * np.pi)
    assert np.allclose(np.hypot(vx, vy)[centro], w * r, rtol=1e-6)
    assert np.allclose(np.hypot(ax, ay)[centro], w**2 * r, rtol=1e-6)
    assert np.allclose(ax[centro], -(w**2) * x[centro], atol=1e-5)
    assert np.allclose(ay[centro], -(w**2) * y[centro], atol=1e-5)


def test_periodo_y_frecuencia():
    assert periodo(2 * np.pi) == pytest.approx(1.0)
    assert periodo(np.pi / 2) == pytest.approx(4.0)


def test_mcua_ecuaciones_angulares():
    w0, alfa = 1.0, 0.5
    t = np.linspace(0, 6, 100)
    theta, w = movimiento_circular(w0, alfa, t)
    assert np.allclose(theta, w0 * t + alfa * t**2 / 2)
    assert np.allclose(w**2, w0**2 + 2 * alfa * theta)


def test_mcua_aceleracion_total():
    r, w0, alfa = 1.5, 0.5, 0.8
    t = np.linspace(0, 4, 40001)
    theta, w = movimiento_circular(w0, alfa, t)
    x, y = posicion(r, theta)
    vx, vy, ax, ay = derivadas(x, y, t)
    centro = slice(5, -5)
    assert np.allclose(np.hypot(vx, vy)[centro], (w * r)[centro], rtol=1e-6)
    assert np.allclose(np.hypot(ax, ay)[centro], np.hypot(w**2 * r, alfa * r)[centro], rtol=1e-5)
