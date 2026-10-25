import pytest
from streamlit.testing.v1 import AppTest

MODULOS = ["Cinemática", "Tiro parabólico", "Movimiento circular", "Dinámica", "Energía", "Colisiones 1D"]


@pytest.mark.parametrize("modulo", MODULOS)
def test_cada_modulo_se_muestra_sin_errores(modulo):
    app = AppTest.from_file("../app.py", default_timeout=60).run()
    app.sidebar.radio[0].set_value(modulo).run()
    assert not app.exception
    opciones = app.main.radio[0].options if app.main.radio else []
    for opcion in opciones:
        app.main.radio[0].set_value(opcion).run()
        assert not app.exception


def test_la_animacion_se_ejecuta():
    app = AppTest.from_file("../app.py", default_timeout=60).run()
    tiempo_total = next(s for s in app.sidebar.slider if s.label == "Tiempo total (s)")
    tiempo_total.set_value(1.0).run()
    app.button[0].click().run()
    assert not app.exception
