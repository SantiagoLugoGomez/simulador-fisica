# Simulador de Física Mecánica

Simulador interactivo para el curso de **Física I**. Cada módulo tiene controles deslizantes para los parámetros, una escena que se puede animar, gráficas que se actualizan en vivo y un panel con los resultados numéricos clave. Todas las magnitudes están en unidades del Sistema Internacional.

Hecho con Python, NumPy, Matplotlib y Streamlit.

## Módulos

| Módulo | Archivo | Qué muestra |
| --- | --- | --- |
| Cinemática | `sims/cinematica.py` | MRU, MRUA y caída libre con gráficas x-t, v-t y a-t. |
| Tiro parabólico | `sims/tiro_parabolico.py` | Trayectoria, alcance, altura máxima y tiempo de vuelo, con comparación de varios ángulos. |
| Movimiento circular | `sims/circular.py` | MCU y MCUA: posición y velocidad angular, velocidad tangencial y aceleraciones centrípeta y tangencial. |
| Dinámica | `sims/dinamica.py` | Bloque en un plano inclinado con fricción estática y cinética, diagrama de fuerzas y aceleración resultante. |
| Energía | `sims/energia.py` | Conservación de la energía en un sistema masa-resorte y en un péndulo simple (energía cinética, potencial y total). |
| Colisiones 1D | `sims/colisiones.py` | Choques elásticos, inelásticos y perfectamente inelásticos, con la conservación del momento lineal. |

## Instalación

Se necesita Python 3.10 o superior.

```bash
git clone https://github.com/SantiagoLugoGomez/simulador-fisica.git
cd simulador-fisica
python -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecución

```bash
streamlit run app.py
```

Streamlit abre la aplicación en el navegador (por defecto en `http://localhost:8501`). El módulo se elige en la barra lateral, donde también están los parámetros. Debajo del panel de resultados hay un control **Instante t** para recorrer el movimiento y un botón **Animar** que lo reproduce.

## Pruebas

```bash
pytest
```

Las pruebas comparan los resultados de cada módulo con soluciones analíticas conocidas, por ejemplo:

- Ecuación de Torricelli en el MRUA y tiempo de caída `t = √(2h/g)`.
- Alcance máximo a 45° y mismo alcance para ángulos complementarios en el tiro parabólico.
- Rapidez `ωr` y aceleración centrípeta `ω²r` obtenidas derivando numéricamente la posición en el MCU.
- Ángulo crítico `θc = arctan(μₛ)` y segunda ley de Newton en el plano inclinado.
- Energía constante en el resorte y en el péndulo, y periodo exacto del péndulo para amplitudes grandes.
- Conservación del momento y coeficiente de restitución en las colisiones.

`tests/test_app.py` además abre cada módulo de la interfaz con el modo de pruebas de Streamlit para verificar que se muestra sin errores.

## Estructura

```
simulador-fisica/
├── app.py              # Punto de entrada: menú lateral y selección de módulo
├── sims/
│   ├── comun.py        # Estilo de las gráficas, flechas y controles de animación
│   ├── cinematica.py
│   ├── tiro_parabolico.py
│   ├── circular.py
│   ├── dinamica.py
│   ├── energia.py
│   └── colisiones.py
├── tests/              # Pruebas con pytest
└── requirements.txt
```

Cada archivo de `sims/` separa las funciones de física (puras, con NumPy) de la función `mostrar()`, que construye la interfaz del módulo. Así las mismas funciones se usan en la aplicación y en las pruebas.

## Modelos y supuestos

- Sin resistencia del aire en cinemática y tiro parabólico.
- En el plano inclinado el bloque parte del reposo. Si `μₖ > μₛ`, la aplicación usa `μₖ = μₛ`.
- El péndulo se resuelve numéricamente con Runge-Kutta de orden 4, sin la aproximación de ángulos pequeños. El periodo exacto se calcula con la integral elíptica completa (media aritmético-geométrica) y se compara con `T₀ = 2π√(L/g)`.
- En las colisiones, el coeficiente de restitución `e` va de 0 (perfectamente inelástica) a 1 (elástica).
