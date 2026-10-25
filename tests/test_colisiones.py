import numpy as np
import pytest

from sims.colisiones import T_FINAL, simular, velocidades_finales


def energia_cinetica(m1, m2, v1, v2):
    return (m1 * v1**2 + m2 * v2**2) / 2


def test_elastica_con_masas_iguales_intercambian_velocidades():
    u1, u2 = velocidades_finales(2.0, 2.0, 3.0, -1.0, 1.0)
    assert u1 == pytest.approx(-1.0)
    assert u2 == pytest.approx(3.0)


def test_elastica_formulas_clasicas():
    m1, m2, v1, v2 = 3.0, 1.0, 4.0, -2.0
    u1, u2 = velocidades_finales(m1, m2, v1, v2, 1.0)
    assert u1 == pytest.approx(((m1 - m2) * v1 + 2 * m2 * v2) / (m1 + m2))
    assert u2 == pytest.approx((2 * m1 * v1 + (m2 - m1) * v2) / (m1 + m2))
    assert energia_cinetica(m1, m2, u1, u2) == pytest.approx(energia_cinetica(m1, m2, v1, v2))


def test_elastica_contra_masa_muy_grande_rebota():
    u1, u2 = velocidades_finales(1.0, 1e9, 5.0, 0.0, 1.0)
    assert u1 == pytest.approx(-5.0)
    assert u2 == pytest.approx(0.0, abs=1e-6)


@pytest.mark.parametrize("e", [0.0, 0.3, 0.7, 1.0])
def test_el_momento_se_conserva(e):
    m1, m2, v1, v2 = 2.5, 4.0, 6.0, -3.0
    u1, u2 = velocidades_finales(m1, m2, v1, v2, e)
    assert m1 * u1 + m2 * u2 == pytest.approx(m1 * v1 + m2 * v2)


@pytest.mark.parametrize("e", [0.0, 0.3, 0.7, 1.0])
def test_coeficiente_de_restitucion(e):
    v1, v2 = 6.0, -3.0
    u1, u2 = velocidades_finales(2.5, 4.0, v1, v2, e)
    assert u2 - u1 == pytest.approx(e * (v1 - v2))


def test_perfectamente_inelastica():
    m1, m2, v1, v2 = 2.0, 3.0, 5.0, 0.0
    u1, u2 = velocidades_finales(m1, m2, v1, v2, 0.0)
    reducida = m1 * m2 / (m1 + m2)
    perdida = energia_cinetica(m1, m2, v1, v2) - energia_cinetica(m1, m2, u1, u2)
    assert u1 == pytest.approx(u2)
    assert u1 == pytest.approx((m1 * v1 + m2 * v2) / (m1 + m2))
    assert perdida == pytest.approx(reducida * (v1 - v2) ** 2 / 2)


def test_simulacion_conserva_el_momento_y_no_se_atraviesan():
    m1, m2 = 2.0, 1.0
    t = np.linspace(0, T_FINAL, 401)
    x1, x2, w1, w2 = simular(m1, m2, 4.0, -2.0, 0.5, t)
    assert np.allclose(m1 * w1 + m2 * w2, m1 * 4.0 + m2 * -2.0)
    assert np.all(x2 - x1 >= -1e-12)


def test_sin_acercamiento_no_hay_choque():
    t = np.linspace(0, T_FINAL, 101)
    _, _, w1, w2 = simular(1.0, 1.0, -2.0, 3.0, 1.0, t)
    assert np.allclose(w1, -2.0)
    assert np.allclose(w2, 3.0)
