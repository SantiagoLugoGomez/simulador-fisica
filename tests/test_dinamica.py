import numpy as np
import pytest

from sims.dinamica import angulo_critico, plano_inclinado

G = 9.81


def test_sin_friccion_la_aceleracion_es_g_por_seno():
    _, friccion, a, desliza = plano_inclinado(3.0, 30.0, 0.0, 0.0, G)
    assert desliza
    assert friccion == 0.0
    assert a == pytest.approx(G / 2)


def test_bajo_el_angulo_critico_queda_en_reposo():
    m, angulo, mu_s = 4.0, 20.0, 0.5
    normal, friccion, a, desliza = plano_inclinado(m, angulo, mu_s, 0.3, G)
    assert not desliza
    assert a == 0.0
    assert friccion == pytest.approx(m * G * np.sin(np.radians(angulo)))
    assert friccion <= mu_s * normal


def test_sobre_el_angulo_critico_desliza_con_friccion_cinetica():
    m, angulo, mu_k = 2.0, 40.0, 0.3
    th = np.radians(angulo)
    normal, friccion, a, desliza = plano_inclinado(m, angulo, 0.5, mu_k, G)
    assert desliza
    assert normal == pytest.approx(m * G * np.cos(th))
    assert friccion == pytest.approx(mu_k * normal)
    assert a == pytest.approx(G * (np.sin(th) - mu_k * np.cos(th)))


def test_angulo_critico():
    assert angulo_critico(1.0) == pytest.approx(45.0)
    mu_s = 0.6
    critico = angulo_critico(mu_s)
    assert not plano_inclinado(1.0, critico - 0.01, mu_s, 0.4, G)[3]
    assert plano_inclinado(1.0, critico + 0.01, mu_s, 0.4, G)[3]


def test_segunda_ley_de_newton():
    m, angulo = 5.0, 50.0
    th = np.radians(angulo)
    normal, friccion, a, _ = plano_inclinado(m, angulo, 0.4, 0.25, G)
    abajo = np.array([np.cos(th), -np.sin(th)])
    fuera = np.array([np.sin(th), np.cos(th)])
    suma = np.array([0.0, -m * G]) + normal * fuera - friccion * abajo
    assert np.allclose(suma, m * a * abajo)


def test_la_aceleracion_no_depende_de_la_masa():
    assert plano_inclinado(1.0, 45.0, 0.3, 0.2, G)[2] == pytest.approx(plano_inclinado(50.0, 45.0, 0.3, 0.2, G)[2])
