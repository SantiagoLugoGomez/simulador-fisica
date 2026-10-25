import numpy as np
import pytest

from sims.energia import energias_pendulo, pendulo, periodo_pendulo, resorte

G = 9.81


def test_resorte_conserva_la_energia():
    m, k, amplitud = 2.0, 50.0, 0.3
    _, _, K, U = resorte(m, k, amplitud, np.linspace(0, 10, 2001))
    assert np.allclose(K + U, k * amplitud**2 / 2)


def test_resorte_periodo():
    m, k, amplitud = 0.5, 20.0, 0.1
    T = 2 * np.pi * np.sqrt(m / k)
    x, _, _, _ = resorte(m, k, amplitud, [T / 2, T])
    assert x[0] == pytest.approx(-amplitud)
    assert x[1] == pytest.approx(amplitud)


def test_resorte_rapidez_maxima_en_el_equilibrio():
    m, k, amplitud = 1.0, 16.0, 0.5
    x, v, K, _ = resorte(m, k, amplitud, np.pi / 2 / np.sqrt(k / m))
    assert x == pytest.approx(0.0, abs=1e-12)
    assert abs(v) == pytest.approx(amplitud * np.sqrt(k / m))
    assert K == pytest.approx(k * amplitud**2 / 2)


def test_pendulo_conserva_la_energia():
    m, largo, theta0 = 1.5, 1.0, np.radians(60)
    theta, w = pendulo(largo, theta0, G, np.linspace(0, 10, 2001))
    K, U = energias_pendulo(m, largo, G, theta, w)
    E = K + U
    assert E[0] == pytest.approx(m * G * largo * (1 - np.cos(theta0)))
    assert np.abs(E - E[0]).max() / E[0] < 1e-6


def test_pendulo_con_angulo_pequeno_es_armonico():
    largo, theta0 = 2.0, np.radians(2)
    t = np.linspace(0, 5, 2001)
    theta, _ = pendulo(largo, theta0, G, t)
    assert np.allclose(theta, theta0 * np.cos(np.sqrt(G / largo) * t), atol=1e-3 * theta0)


def test_periodo_exacto_valores_conocidos():
    T0 = 2 * np.pi * np.sqrt(1.0 / G)
    assert periodo_pendulo(1.0, 1e-6, G) == pytest.approx(T0)
    assert periodo_pendulo(1.0, np.pi / 2, G) / T0 == pytest.approx(1.180341, rel=1e-6)


@pytest.mark.parametrize("grados", [10, 60, 120, 160])
def test_tras_un_periodo_exacto_vuelve_al_inicio(grados):
    largo, theta0 = 1.0, np.radians(grados)
    T = periodo_pendulo(largo, theta0, G)
    theta, w = pendulo(largo, theta0, G, np.linspace(0, T, 4001))
    assert theta[-1] == pytest.approx(theta0, rel=1e-6)
    assert w[-1] == pytest.approx(0.0, abs=1e-5)
    assert np.abs(largo * w).max() == pytest.approx(np.sqrt(2 * G * largo * (1 - np.cos(theta0))), rel=1e-4)
