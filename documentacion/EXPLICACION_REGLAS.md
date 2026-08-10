# Explicación Detallada de `reglas.py`

El módulo [`reglas.py`](reglas.py) constituye el **Conjunto de Reglas de Producción** del Sistema Experto. Traduce el conocimiento del Mundo del Wumpus en un conjunto de funciones modulares e independientes expresadas en la forma canónica:

$$\text{SI } \langle \text{Condiciones sobre la Base de Hechos} \rangle \implies \text{ENTONCES } \langle \text{Nuevas Conclusiones} \rangle$$

---

## 1. Arquitectura y Firma de las Reglas

Cada regla del sistema se define como una función pura que respeta la misma firma de parámetros y retorno:

```python
def regla_ejemplo(casilla, base):
    """SI <condicion> ENTONCES <conclusión>"""
    conclusiones = []
    # Lógica de evaluación sobre la casilla visitada y la base de hechos
    return conclusiones
```

### Parámetros:
- `casilla`: Tupla `(x, y)` correspondiente a una casilla visitada por el agente.
- `base`: Objeto `BaseConocimiento` (Base de Hechos) que contiene percepciones acumuladas, casillas visitadas, conjuntos de casillas seguras, peligrosas, descartadas (`no_pozo`, `no_wumpus`) y el estado de `wumpus_muerto`.

### Retorno:
Devuelve una lista de tuplas `(tipo_conclusion, objetivo)` que representan las deducciones que el motor de inferencia incorporará a la Base de Conocimiento.

---

## 2. Tipos de Conclusiones Producidas

| Tipo de Conclusión | Parámetro Objetivo | Significado Lógico |
| :--- | :--- | :--- |
| `'segura'` | `(x, y)` | La casilla `(x, y)` no contiene ni pozo ni Wumpus vivo. Es apta para transitar. |
| `'peligrosa'` | `(x, y)` | La casilla `(x, y)` contiene una amenaza confirmada (pozo o Wumpus). |
| `'no_pozo'` | `(x, y)` | Se ha demostrado que la casilla `(x, y)` está libre de pozos. |
| `'no_wumpus'` | `(x, y)` | Se ha demostrado que la casilla `(x, y)` está libre de Wumpus. |
| `'pozo_confirmado'` | `(x, y)` | Inferencia exacta: existe un pozo en la casilla `(x, y)`. |
| `'wumpus_confirmado'`| `(x, y)` | Inferencia exacta: el Wumpus está en la casilla `(x, y)`. |
| `'wumpus_muerto'` | `True` | Inferencia global: el Wumpus ha sido eliminado. |

---

## 3. Explicación Detallada de las 9 Reglas de Producción

### 3.1. `regla_casilla_visitada_es_segura(casilla, base)`
- **Lógica:** Si el agente ha visitado `casilla` y sigue con vida, por definición empírica esa casilla no tenía un pozo ni un Wumpus activo.
- **Conclusiones generadas:** `('segura', casilla)`, `('no_pozo', casilla)`, `('no_wumpus', casilla)`.

---

### 3.2. `regla_sin_breeze_ni_stench(casilla, base)`
- **Lógica:** Si en la casilla visitada no se sintió ni `breeze` ni `stench` (o el Wumpus ya murió), no hay ningún peligro en sus casillas contiguas.
- **Conclusiones generadas:** Marca todas las casillas vecinas devueltas por `adyacentes(x, y)` como `segura`, `no_pozo` y `no_wumpus`.

---

### 3.3. `regla_sin_breeze(casilla, base)`
- **Lógica:** Si no se percibe `breeze` en `casilla`, ninguna de sus casillas adyacentes puede contener un pozo.
- **Conclusiones generadas:** `('no_pozo', vecina)` para cada vecina.

---

### 3.4. `regla_sin_stench(casilla, base)`
- **Lógica:** Si no se percibe `stench` en `casilla` (o si el Wumpus está muerto), ninguna de sus casillas adyacentes puede contener al Wumpus vivo.
- **Conclusiones generadas:** `('no_wumpus', vecina)` para cada vecina.

---

### 3.5. `regla_breeze_confirmar_pozo(casilla, base)`
- **Lógica (Deducción por descarte de pozo):** Si hay `breeze` en `casilla`, sabemos que al menos una adyacente tiene pozo. Se inspeccionan todas sus vecinas y se filtran las que **aún no están descartadas** (es decir, aquellas que no son `seguras` ni están en el conjunto `no_pozo`).
- **Condición de disparo:** Si la lista de candidatas sospechosas se reduce a **exactamente 1 casilla**, se deduce con certeza absoluta que esa casilla es un pozo.
- **Conclusiones generadas:** `('pozo_confirmado', pozo)` y `('peligrosa', pozo)`.

---

### 3.6. `regla_stench_confirmar_wumpus(casilla, base)`
- **Lógica (Deducción por descarte de Wumpus):** Si hay `stench` en `casilla` y el Wumpus no está muerto, se evalúan sus adyacentes. Si todas menos una están en `base.seguras` o `base.no_wumpus`, la única adyacente restante debe contener al Wumpus.
- **Conclusiones generadas:** `('wumpus_confirmado', wumpus_loc)` y `('peligrosa', wumpus_loc)`.

---

### 3.7. `regla_interseccion_stench(casilla, base)`
- **Lógica (Inferencia Espacial Avanzada):** Si se percibe `stench` en 2 o más casillas visitadas distintas, el Wumpus solo puede habitar en la **intersección geográfica** de las adyacentes de esas casillas con stench.
- **Mecanismo:**
  1. Calcula la intersección de adyacentes entre las casillas con `stench`.
  2. Cualquier adyacente a una casilla con `stench` que quede fuera de dicha intersección es inmediatamente marcada como `no_wumpus`.
  3. Si la intersección resulta en una única casilla, se confirma la ubicación del Wumpus.

---

### 3.8. `regla_descarte_wumpus_por_muerte(casilla, base)`
- **Lógica:** Si el agente percibió la brisa auditiva de la muerte del Wumpus (`scream` en las percepciones) o el estado `wumpus_muerto` es `True`, la amenaza del Wumpus se extingue.
- **Conclusiones generadas:** Genera `('wumpus_muerto', True)` y marca todas las 16 casillas de la grilla 4×4 como `no_wumpus`.

---

### 3.9. `regla_deducir_casilla_segura(casilla, base)`
- **Lógica (Síntesis de Hechos):** Una casilla `(x, y)` no visitada es declarada completamente **segura** si y solo si concurren dos hechos deducidos:
  $$\text{Casilla } (x,y) \in \text{no\_pozo} \quad \land \quad \left( (x,y) \in \text{no\_wumpus} \ \lor \ \text{Wumpus\_Muerto} \right)$$
- **Conclusiones generadas:** `('segura', (x, y))`.

---

## 4. El Arreglo `REGLAS` y el Proceso de Encadenamiento

Todas las funciones descritas se exportan ordenadamente en la lista `REGLAS`:

```python
REGLAS = [
    regla_casilla_visitada_es_segura,
    regla_sin_breeze_ni_stench,
    regla_sin_breeze,
    regla_sin_stench,
    regla_breeze_confirmar_pozo,
    regla_stench_confirmar_wumpus,
    regla_interseccion_stench,
    regla_descarte_wumpus_por_muerte,
    regla_deducir_casilla_segura
]
```

### Ciclo del Motor de Inferencia (*Forward Chaining*):
1. El motor de inferencia toma cada casilla en `base.visitadas`.
2. Para esa casilla, ejecuta secuencialmente las funciones de `REGLAS`.
3. Si una regla aporta una nueva conclusión no registrada previamente en la `BaseConocimiento`, se actualiza la base y se marca `hubo_novedades = True`.
4. El proceso se repite en bucle (`while hubo_novedades:`) hasta alcanzar el **Punto Fijo** (momento en que ninguna regla genera nuevos hechos).
