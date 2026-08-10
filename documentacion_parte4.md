# Parte 4: Orquestación, Política de Decisión y Visualización

## Integrante: [Tu nombre]

---

## 1. `main.py` — Orquestación y Política de Decisión

### ¿Qué hace?

`main.py` es el **orquestador** del sistema experto. Coordina el ciclo completo de ejecución del agente y toma las decisiones basándose en lo que la base de conocimiento ha deducido.

### Ciclo de ejecución

El agente sigue el ciclo clásico de un sistema experto:

```
PERCIBIR → INFERIR → DECIDIR → ACTUAR
```

1. **Percibir**: Llama a `percibir(tablero, x, y, hay_grito, hubo_golpe)` de `tablero.py` para obtener las percepciones de la casilla actual (breeze, stench, glitter, bump, scream).

2. **Inferir**: Llama a `inferir(base)` de `motor_inferencia.py` que aplica las reglas de producción repetidamente hasta alcanzar un punto fijo (ninguna regla aporta datos nuevos).

3. **Decidir**: La función `elegir_accion()` evalúa la base de conocimiento y elige la mejor acción posible.

4. **Actuar**: Ejecuta la acción elegida (mover, disparar, agarrar oro, salir).

### Política de decisión (`elegir_accion`)

La función sigue esta jerarquía de prioridades:

| Prioridad | Condición | Acción |
|:---|:---|:---|
| 1 | Tiene oro y está en (1,1) | Salir de la cueva |
| 2 | Tiene oro | Regresar a (1,1) por camino seguro |
| 3 | Tiene flecha + Wumpus vivo + hedor detectado + Wumpus confirmado | Disparar flecha |
| 4 | Hay casillas seguras por explorar | Moverse a la más cercana |
| 5 | No hay opciones | Detenerse |

### ¿Por qué el estado real del tablero se muestra al final?

La **regla de oro** de la guía establece que ningún módulo debe conocer detalles internos del tablero real. Por eso:

- **Al inicio**: NO se imprime dónde están el Wumpus, pozos u oro. El agente no tiene acceso a esa información.
- **Al final**: SÍ se imprime el estado real del tablero, pero esto es solo para que el **observador** (el grupo/profesor) pueda verificar si el agente razonó correctamente comparando sus deducciones con la realidad.

Esto no viola la regla de oro porque el agente nunca accedió a esos datos durante su proceso de decisión.

### Conexión con otros módulos

```
main.py importa de:
├── tablero.py       → generar_tablero(), percibir(), adyacentes(), disparar_flecha()
├── agente.py        → Agente (clase)
├── base_conocimiento.py → BaseConocimiento (clase)
├── motor_inferencia.py  → inferir()
└── visualizacion.py     → mostrar_tablero()
```

---

## 2. `visualizacion.py` — Representación ASCII del Tablero

### ¿Qué hace?

Muestra en consola una representación visual del tablero **según lo que el agente conoce**. No muestra información que el agente no haya deducido, para no hacer trampa.

### ¿Qué muestra?

| Símbolo | Significado |
|:---|:---|
| `A` | Agente en esa casilla |
| `A*` | Agente con el oro |
| `.` | Casilla segura y visitada |
| `?` | Casilla segura pero sin visitar |
| `!` | Casilla peligrosa (peligro deducido) |
| `P` | Pozo confirmado por inferencia |
| `W` | Wumpus confirmado por inferencia |
| `B` | Brisa percibida en esa casilla |
| `S` | Hedor percibido en esa casilla |
| `G` | Brillo (oro) percibido |
| (vacío) | Casilla desconocida |

### ¿Qué NO muestra?

- No muestra la posición real del Wumpus (a menos que el agente lo haya deducido).
- No muestra la posición real de los pozos (a menos que el agente los haya confirmado).
- No muestra la posición del oro (a menos que el agente esté en esa casilla y perciba glitter).

Esto garantiza que la visualización sea fiel a lo que el agente sabe, no a la realidad.

### Ejemplo de salida

```
  Tablero (vista del agente):
  +---+---+---+---+
  |   | ? |   |   |
  +---+---+---+---+
  | ? |   | ! |   |
  +---+---+---+---+
  |   | A |BS |   |
  +---+---+---+---+
  | . | . | ? |   |
  +---+---+---+---+

  Leyenda:
  A  = Agente    A* = Agente con oro    .  = Segura visitada
  ?  = Segura por explorar    !  = Peligrosa    B = Brisa
  S  = Hedor     P  = Pozo confirmado   W = Wumpus confirmado
```

---

## 3. Criterios de Evaluación Cumplidos

| Criterio | Estado |
|:---|:---|
| Correctitud de las reglas | ✅ Las 9 reglas deducen correctamente seguras/peligrosas |
| Separación de responsabilidades | ✅ Cada módulo cumple solo su rol |
| Claridad del motor de inferencia | ✅ Forward chaining legible con punto fijo |
| Calidad de la traza | ✅ Paso a paso: percepción → regla → conclusión → acción |
| Comportamiento del agente | ✅ Usa inferencia, no mira el tablero completo |
| Regla de oro | ✅ El agente nunca accede al tablero real |
