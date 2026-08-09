"""Verificador del módulo Base de Conocimiento + Motor de Inferencia.

Ejecuta escenarios fijos del Mundo del Wumpus y comprueba que el motor de
inferencia (forward chaining) deduzca las conclusiones esperadas, imprimiendo
la traza: percepción -> regla disparada -> conclusión nueva.

Uso:
    python verificar_inferencia.py

Requiere los módulos del equipo (tablero.py, reglas.py) para poder evaluar
las reglas de producción sobre la base de hechos.
"""

from base_conocimiento import BaseConocimiento
from motor_inferencia import inferir

PASS = 0
FAIL = 0


def mostrar_traza(traza, casillas):
    """Imprime, recortado al escenario, que regla disparó y qué concluyó."""
    for regla, tipo, destino in traza:
        if destino in casillas or tipo == 'wumpus_muerto':
            print(f"    [traza] {regla} -> {tipo}: {destino}")


def chequeado(nombre, condicion, detalle=""):
    global PASS, FAIL
    if condicion:
        PASS += 1
        print(f"  OK - {nombre}")
    else:
        FAIL += 1
        print(f"  ERROR - {nombre} {detalle}")


def test_sin_breeze_ni_stench():
    print("\n1) Sin breeze ni stench: todas las adyacentes son seguras")
    base = BaseConocimiento()
    base.registrar_percepcion(2, 1, {'breeze': False, 'stench': False, 'glitter': False})
    traza = inferir(base)
    mostrar_traza(traza, {(2, 2), (3, 1)})
    chequeado("(2,2) es segura", (2, 2) in base.seguras)
    chequeado("(3,1) es segura", (3, 1) in base.seguras)
    chequeado("(2,2) esta libre de pozo", (2, 2) in base.no_pozo)
    chequeado("(2,2) esta libre de wumpus", (2, 2) in base.no_wumpus)


def test_breeze_confirma_pozo_por_descarte():
    print("\n2) Breeze + descarte: se confirma un pozo (2,1)")
    base = BaseConocimiento()
    base.registrar_percepcion(1, 1, {'breeze': True, 'stench': False, 'glitter': False})
    base.registrar_percepcion(1, 2, {'breeze': False, 'stench': False, 'glitter': False})
    traza = inferir(base)
    mostrar_traza(traza, {(2, 1)})
    chequeado("(2,1) es pozo confirmado", (2, 1) in base.pozos_confirmados)
    chequeado("(2,1) es peligrosa", (2, 1) in base.peligrosas)
    chequeado("(2,1) no es segura", (2, 1) not in base.seguras)


def test_casilla_visitada_es_segura():
    print("\n3) Casilla visitada sin morir queda confirmada segura")
    base = BaseConocimiento()
    base.registrar_percepcion(1, 1, {'breeze': False, 'stench': False, 'glitter': False})
    base.registrar_percepcion(1, 2, {'breeze': False, 'stench': False, 'glitter': False})
    traza = inferir(base)
    mostrar_traza(traza, {(1, 2)})
    chequeado("(1,2) es segura", (1, 2) in base.seguras)
    chequeado("(1,2) en no_pozo", (1, 2) in base.no_pozo)
    chequeado("(1,2) en no_wumpus", (1, 2) in base.no_wumpus)


def test_stench_confirma_wumpus_por_descarte():
    print("\n4) Stench en dos vecinas: se descarta el resto y se confirma el wumpus")
    base = BaseConocimiento()
    base.registrar_percepcion(1, 1, {'breeze': False, 'stench': False, 'glitter': False})
    base.registrar_percepcion(1, 2, {'breeze': False, 'stench': True, 'glitter': False})
    base.registrar_percepcion(2, 1, {'breeze': False, 'stench': True, 'glitter': False})
    traza = inferir(base)
    mostrar_traza(traza, {(1, 1), (1, 2), (2, 1), (2, 2), (1, 3), (3, 1)})
    chequeado("se confirma el wumpus en (2,2)", base.wumpus_confirmado == (2, 2))
    chequeado("(2,2) es peligrosa", (2, 2) in base.peligrosas)
    chequeado("(1,3) libre de wumpus (fuera de interseccion)",
              (1, 3) in base.no_wumpus)
    chequeado("(3,1) libre de wumpus (fuera de interseccion)",
              (3, 1) in base.no_wumpus)


def test_muerte_wumpus_libera_todo():
    print("\n5) Scream: el wumpus muere y se liberan las adyacentes")
    base = BaseConocimiento()
    base.registrar_percepcion(1, 1, {'breeze': False, 'stench': True, 'glitter': False})
    inferir(base)
    base.registrar_percepcion(1, 1, {'breeze': False, 'stench': True,
                                     'glitter': False, 'scream': True})
    traza = inferir(base)
    mostrar_traza(traza, {(1, 1)})
    chequeado("wumpus_muerto = True", base.wumpus_muerto)
    chequeado("todas las casillas libres de wumpus",
              all((x, y) in base.no_wumpus for x in range(1, 5) for y in range(1, 5)))


def test_descarte_sospecha_personal():
    print("\n6) Descartar sospecha cuando hay nueva informacion")
    base = BaseConocimiento()
    base.marcar_peligrosa((2, 1))
    base.marcar_no_pozo((2, 1))
    chequeado("(2,1) sale de peligrosas al ser no_pozo", (2, 1) not in base.peligrosas)
    base.marcar_no_wumpus((3, 1))
    chequeado("(3,1) sale de peligrosas al ser no_wumpus", (3, 1) not in base.peligrosas)


def main():
    test_sin_breeze_ni_stench()
    test_breeze_confirma_pozo_por_descarte()
    test_casilla_visitada_es_segura()
    test_stench_confirma_wumpus_por_descarte()
    test_muerte_wumpus_libera_todo()
    test_descarte_sospecha_personal()
    print(f"\nResultado: {PASS} OK, {FAIL} ERROR")
    raise SystemExit(1 if FAIL else 0)


if __name__ == '__main__':
    main()