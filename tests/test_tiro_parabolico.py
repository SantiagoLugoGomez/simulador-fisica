import numpy as np
import pytest

from sims.tiro_parabolico import resultados, trayectoria

G = 9.81


def test_formulas_clasicas_desde_el_suelo():
    v0, angulo = 20.0, 35.0
    th = np.radians(angulo)
    t_vuelo, alcance, altura = resultados(v0, angulo, 0.0, G)
    assert t_vuelo == pytest.approx(2 * v0 * np.sin(th) / G)
    assert alcance == pytest.approx(v0**2 * np.sin(2 * th) / G)
    assert altura == pytest.approx((v0 * np.sin(th)) ** 2 / (2 * G))


@pytest.mark.parametrize("angulo", [10, 20, 30, 40])
def test_angulos_complementarios_tienen_el_mismo_alcance(angulo):
    assert resultados(25.0, angulo, 0.0, G)[1] == pytest.approx(resultados(25.0, 90 - angulo, 0.0, G)[1])


def test_45_grados_da_el_alcance_maximo():
    angulos = np.arange(1, 90)
    alcances = [resultados(18.0, a, 0.0, G)[1] for a in angulos]
    assert angulos[np.argmax(alcances)] == 45
    assert max(alcances) == pytest.approx(18.0**2 / G)


def test_la_trayectoria_es_una_parabola():
    v0, angulo = 15.0, 60.0
    th = np.radians(angulo)
    x, y, _, _ = trayectoria(v0, angulo, 0.0, G, np.linspace(0, 2, 50))
    assert np.allclose(y, x * np.tan(th) - G * x**2 / (2 * v0**2 * np.cos(th) ** 2))


def test_lanzamiento_desde_una_altura():
    v0, angulo, h0 = 12.0, 25.0, 8.0
    t_vuelo, alcance, _ = resultados(v0, angulo, h0, G)
    x, y, vx, vy = trayectoria(v0, angulo, h0, G, t_vuelo)
    assert y == pytest.approx(0.0, abs=1e-9)
    assert x == pytest.approx(alcance)
    assert np.hypot(vx, vy) == pytest.approx(np.sqrt(v0**2 + 2 * G * h0))


def test_lanzamiento_horizontal():
    t_vuelo, alcance, altura = resultados(10.0, 0.0, 20.0, G)
    assert t_vuelo == pytest.approx(np.sqrt(2 * 20.0 / G))
    assert alcance == pytest.approx(10.0 * t_vuelo)
    assert altura == pytest.approx(20.0)
