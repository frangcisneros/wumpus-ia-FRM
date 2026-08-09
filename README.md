# TP Integrador: Agente Racional para el Mundo del Wumpus (Sistemas Expertos)

**Asignatura:** Inteligencia Artificial — 5° Año (Ingeniería en Sistemas, UTN San Rafael)  
**Docentes:** Prof. Novas José – Prof. Arroyo Ricardo  

---

## 1. Objetivo del Proyecto

Implementar (en grupos de hasta 4 integrantes) un **agente racional** que resuelva el problema del **Mundo del Wumpus** aplicando los conceptos y mecanismos de un **Sistema Experto**:
- **Base de Conocimiento (Hechos):** Almacena hechos percibidos y conclusiones lógicas deducidas.
- **Reglas de Producción:** Conjunto de reglas `SI <condición> ENTONCES <conclusión>`.
- **Motor de Inferencia:** Mecanismo de encadenamiento hacia adelante (*forward chaining*) que deduce si las casillas son seguras, peligrosas o desconocidas.

> **Importante:** No es un juego interactivo para ser jugado manualmente. El tablero se genera aleatoriamente y el agente actúa de forma autónoma guiado exclusivamente por inferencia lógica. El grupo observa y documenta cómo razona el sistema.

---

## 2. Especificación del Entorno (Mundo del Wumpus)

### Reglas del Entorno (Russell & Norvig, cap. 7)
- **Grilla:** 4×4 casillas. El agente arranca en `(1, 1)`, mirando hacia el Este.
- **Wumpus:** 1 ubicado aleatoriamente (nunca en `(1, 1)`).
- **Pozos (Pits):** Entre 1 y 3 pozos ubicados aleatoriamente (nunca en `(1, 1)`).
- **Oro:** 1 pieza de oro ubicada aleatoriamente.
- **Armamento:** 1 flecha para disparar en línea recta y eliminar al Wumpus.

### Percepciones y Acciones

| Percepción | Significado | Aparece cuando... |
| :--- | :--- | :--- |
| **Stench** | Hedor | El Wumpus está en una casilla adyacente (no diagonal). |
| **Breeze** | Brisa | Hay un pozo en una casilla adyacente. |
| **Glitter** | Brillo | El oro está en la casilla actual. |
| **Bump** | Golpe | El agente choca contra un límite del tablero. |
| **Scream** | Grito | El Wumpus murió por la flecha. |

**Acciones disponibles para el agente:**
- Moverse hacia adelante.
- Girar 90° a la izquierda / derecha.
- Disparar la flecha (una sola vez, en la dirección actual).
- Agarrar el oro (si está en la casilla actual).
- Salir de la cueva (solo desde `(1, 1)`).

---

## 3. Conexión con Sistemas Expertos (Equivalencia Conceptual)

| Sistema Experto Clásico | Agente del Mundo del Wumpus |
| :--- | :--- |
| **Base de hechos** | Percepciones acumuladas por cada casilla visitada. |
| **Reglas de producción (SI... ENTONCES...)** | *"SI hay Breeze en (x,y) ENTONCES al menos una casilla adyacente no confirmada-segura es sospechosa de pozo"* |
| **Motor de inferencia (forward chaining)** | Recorre las reglas y actualiza qué casillas son seguras, peligrosas o desconocidas. |
| **Conclusión / Recomendación** | Próxima acción del agente, elegida entre las casillas seguras. |

> **Nota:** Esta tabla debe incluirse en el informe final acompañando un ejemplo propio desarrollado por el grupo.

---

## 4. Consigna y Etapas de Desarrollo

- **Etapa 1 — Simulación por consola (Obligatoria):**  
  El tablero se genera aleatoriamente en cada corrida (con posiciones válidas sin coincidir en `(1,1)`). El agente recorre el entorno de forma completamente autónoma imprimiendo paso a paso la traza del razonamiento: *Percepción recibida → Regla disparada → Conclusión nueva → Acción tomada*.
- **Etapa 2 — Visualización (A elección del grupo):**  
  Una vez funcionando la Etapa 1, se puede optar por:
  - Representación ASCII del tablero en cada paso (matriz impresa en consola).
  - Interfaz gráfica simple (Pygame, Tkinter, etc.).  
  *(Ambas opciones se evalúan por igual siempre que no reemplacen el trabajo de la Etapa 1)*.

---

## 5. Arquitectura del Proyecto

Se requiere dividir el trabajo en módulos con responsabilidades aisladas:

```text
wumpus_agente/
├── main.py                 # Orquesta la simulación, política de decisión e imprime la traza
├── tablero.py              # El mundo real (wumpus, pozos, oro, percepciones sin revelar datos al agente)
├── agente.py               # Estado físico del agente (posición, dirección, flecha, oro, vivo)
├── base_conocimiento.py    # Base de hechos ("Base de Hechos": percepciones, seguras, peligrosas)
├── reglas.py               # Reglas de producción SI-ENTONCES independientes
├── motor_inferencia.py     # Motor de inferencia por encadenamiento hacia adelante (forward chaining)
└── visualizacion.py        # Visualización ASCII o gráfica (Etapa 2, opcional)
```

> **Regla de Oro:** Ningún módulo debe conocer detalles internos de otro más allá de lo estrictamente necesario. Por ejemplo, el agente o motor nunca debe acceder directamente al tablero real (eso sería "hacer trampa"); solo pueden invocar `percibir(x, y)`.

---

## 6. Detalle de Módulos y Código Base

### 6.1. `tablero.py` — El Mundo Real
Genera el mundo aleatoriamente y expone únicamente lo que el agente tiene derecho a percibir.

```python
import random

TAMANIO = 4

def generar_tablero(cant_pozos=2):
    casillas = [(x, y) for x in range(1, TAMANIO+1)
                       for y in range(1, TAMANIO+1)
                       if (x, y) != (1, 1)]
    random.shuffle(casillas)
    wumpus = casillas.pop()
    pozos = [casillas.pop() for _ in range(cant_pozos)]
    oro = casillas.pop()
    return {'wumpus': wumpus, 'pozos': pozos, 'oro': oro}

def adyacentes(x, y):
    candidatas = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
    return [(a, b) for a, b in candidatas if 1 <= a <= TAMANIO and 1 <= b <= TAMANIO]

def percibir(tablero, x, y):
    vecinas = adyacentes(x, y)
    return {
        'breeze': any(v in tablero['pozos'] for v in vecinas),
        'stench': tablero['wumpus'] in vecinas,
        'glitter': (x, y) == tablero['oro'],
    }
```

### 6.2. `agente.py` — Estado Físico del Agente
Guarda posición y estado, ejecutando las acciones indicadas por el orquestador sin tomar decisiones por sí mismo.

```python
class Agente:
    def __init__(self):
        self.x, self.y = 1, 1
        self.tiene_oro = False
        self.tiene_flecha = True
        self.vivo = True

    def mover_a(self, x, y):
        self.x, self.y = x, y

    def agarrar_oro(self):
        self.tiene_oro = True
```

### 6.3. `base_conocimiento.py` — La Base de Hechos
Almacena por cada casilla visitada la percepción recibida y las conclusiones deducidas (*segura / peligrosa / desconocida*).

```python
class BaseConocimiento:
    def __init__(self):
        self.percepciones = {}  # (x,y) -> {'breeze': bool, 'stench': bool, ...}
        self.seguras = {(1, 1)}
        self.peligrosas = set()
        self.visitadas = {(1, 1)}

    def registrar_percepcion(self, x, y, percepcion):
        self.percepciones[(x, y)] = percepcion
        self.visitadas.add((x, y))

    def marcar_segura(self, casilla):
        self.seguras.add(casilla)

    def marcar_peligrosa(self, casilla):
        self.peligrosas.add(casilla)

    def casillas_por_explorar(self):
        return self.seguras - self.visitadas - self.peligrosas
```

### 6.4. `reglas.py` — Reglas de Producción
Cada regla es una función independiente con su docstring explicativo.

```python
from tablero import adyacentes

def regla_sin_breeze_ni_stench(casilla, base):
    """SI no hubo breeze ni stench en 'casilla' ENTONCES todas sus adyacentes son seguras."""
    x, y = casilla
    percepcion = base.percepciones[casilla]
    conclusiones = []
    if not percepcion['breeze'] and not percepcion['stench']:
        for vecina in adyacentes(x, y):
            conclusiones.append(('segura', vecina))
    return conclusiones

def regla_breeze(casilla, base):
    """SI hay breeze en 'casilla' ENTONCES al menos una adyacente no confirmada-segura es sospechosa de pozo."""
    x, y = casilla
    percepcion = base.percepciones[casilla]
    conclusiones = []
    if percepcion['breeze']:
        vecinas = adyacentes(x, y)
        sospechosas = [v for v in vecinas if v not in base.seguras]
        if len(sospechosas) == 1:
            conclusiones.append(('peligrosa', sospechosas[0]))
    return conclusiones

# Reglas activas del sistema (se evalúan en este orden)
REGLAS = [regla_sin_breeze_ni_stench, regla_breeze]
```
> **A completar por el grupo:** Reglas equivalentes para `stench` (deducir Wumpus) y reglas para descartar sospechas al recibir nueva información.

### 6.5. `motor_inferencia.py` — Encadenamiento Hacia Adelante
Recorre la lista de reglas y las aplica sobre cada casilla visitada hasta alcanzar un **punto fijo** (donde ninguna regla aporte datos nuevos).

```python
from reglas import REGLAS

def aplicar_reglas(base):
    hubo_novedades = False
    for casilla in base.visitadas:
        for regla in REGLAS:
            conclusiones = regla(casilla, base)
            for tipo, destino in conclusiones:
                if tipo == 'segura' and destino not in base.seguras:
                    base.marcar_segura(destino)
                    hubo_novedades = True
                elif tipo == 'peligrosa' and destino not in base.peligrosas:
                    base.marcar_peligrosa(destino)
                    hubo_novedades = True
    return hubo_novedades

def inferir(base):
    """Aplica las reglas repetidamente hasta que no surjan más conclusiones nuevas (punto fijo)."""
    while aplicar_reglas(base):
        pass
```

### 6.6. `main.py` — Orquestación y Traza
Ejecuta el ciclo: `percibir → inferir → decidir → actuar` e imprime la traza legible.

```python
from tablero import generar_tablero, percibir
from agente import Agente
from base_conocimiento import BaseConocimiento
from motor_inferencia import inferir

def elegir_accion(agente, base):
    candidatas = base.casillas_por_explorar()
    if candidatas:
        return ('mover', next(iter(candidatas)))
    return ('detener', None)

def simular():
    tablero = generar_tablero()
    agente = Agente()
    base = BaseConocimiento()
    paso = 1

    while agente.vivo and not agente.tiene_oro:
        percepcion = percibir(tablero, agente.x, agente.y)
        base.registrar_percepcion(agente.x, agente.y, percepcion)
        print(f"Paso {paso}: Agente en ({agente.x}, {agente.y}). Percibe: {percepcion}")

        inferir(base)

        if percepcion['glitter']:
            agente.agarrar_oro()
            print(' -> Encontró el oro. Simulación terminada con éxito.')
            break

        accion, destino = elegir_accion(agente, base)
        if accion == 'mover':
            print(f' -> Acción elegida: mover a {destino} (casilla segura)')
            agente.mover_a(*destino)
        else:
            print(' -> No quedan casillas seguras por explorar. Fin de la simulación.')
            break

        paso += 1

if __name__ == '__main__':
    simular()
```
> **A completar por el grupo:** Agregar el manejo de peligro (wumpus/pozo), disparo de flecha y salida con el oro hacia `(1,1)`.

---

## 7. Formato de Traza Esperado

La consola debe mostrar en cada paso un log claro con la estructura: `percepción → regla → conclusión → acción`:

```text
Paso 3: Agente en (2, 1). Percibe: {'breeze': True, 'stench': False, 'glitter': False}
  Regla disparada: regla_breeze
  Conclusión nueva: (2, 2) marcada como PELIGROSA (posible pozo)
  Acción elegida: mover a (1, 2) [casilla segura]
```

---

## 8. Reparto Sugerido dentro del Grupo (4 Integrantes)

1. `tablero.py` + `agente.py` — Modelado del mundo y del estado del agente.
2. `reglas.py` — Traducir el razonamiento lógico del Wumpus World a reglas de producción.
3. `base_conocimiento.py` + `motor_inferencia.py` — El "corazón" del sistema experto.
4. `main.py` + `visualizacion.py` — Orquestación, política de decisión, traza y visualización (opcional).

---

## 9. Entregables

- **Código fuente completo:** Organizado en los módulos indicados.
- **Informe breve (PDF o Word):**
  - Tabla de equivalencia con sistemas expertos completada con ejemplo propio del grupo.
  - Lista de reglas implementadas con una línea de justificación cada una.
  - Traza completa de al menos una corrida de ejemplo.
  - Sección corta por integrante explicando el módulo que desarrolló.
  - Aclaración de la opción elegida para la Etapa 2 (ASCII, gráfica o ninguna).

---

## 10. Criterios de Evaluación

| Criterio | Qué se observa |
| :--- | :--- |
| **Correctitud de las reglas** | Las reglas deducen correctamente casillas seguras/peligrosas según las percepciones. |
| **Separación de responsabilidades** | El agente no accede al tablero real; cada módulo cumple solo su rol. |
| **Claridad del motor de inferencia** | El ciclo de encadenamiento hacia adelante es legible y se entiende cuándo se detiene. |
| **Calidad de la traza** | Se puede seguir el razonamiento paso a paso desde la consola o el informe. |
| **Comportamiento del agente** | Evita pozos y Wumpus usando solo inferencia, sin mirar el tablero completo ni fuerza bruta. |
| **Trabajo en grupo** | Reparto de módulos reflejado en el informe y en el historial de trabajo del grupo. |