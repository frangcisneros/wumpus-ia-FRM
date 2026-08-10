from tablero import generar_tablero, percibir, adyacentes, disparar_flecha, TAMANIO, DIRECCIONES
from agente import Agente
from base_conocimiento import BaseConocimiento
from motor_inferencia import inferir
from visualizacion import mostrar_tablero
from collections import deque


def _direccion_hacia(origen, destino):
    dx = destino[0] - origen[0]
    dy = destino[1] - origen[1]
    for nombre, (vx, vy) in DIRECCIONES.items():
        if (vx, vy) == (dx, dy):
            return nombre
    return None


def _orientar_y_disparar(agente, candidatas):
    for candidata in candidatas:
        dir_objetivo = _direccion_hacia((agente.x, agente.y), candidata)
        if dir_objetivo is None:
            continue
        while agente.orientacion != dir_objetivo:
            agente.girar_derecha()
        return ('disparar', None)
    return None


def _camino_seguro(origen, destino, base):
    if origen == destino:
        return []
    visitados = {origen}
    cola = deque([(origen, [])])
    while cola:
        actual, camino = cola.popleft()
        for vecina in adyacentes(*actual):
            if vecina == destino:
                return camino + [vecina]
            if vecina not in visitados and vecina in base.visitadas:
                visitados.add(vecina)
                cola.append((vecina, camino + [vecina]))
    return None


def elegir_accion(agente, base):
    pos = (agente.x, agente.y)

    if agente.tiene_oro:
        if pos == (1, 1):
            return ('salir', None)
        if (1, 1) in base.seguras:
            return ('mover', (1, 1))
        return ('detener', None)

    candidatas = base.casillas_por_explorar()
    if candidatas:
        destino = min(candidatas, key=lambda c: abs(c[0] - agente.x) + abs(c[1] - agente.y))
        return ('mover', destino)

    if agente.tiene_flecha and not base.wumpus_muerto:
        percepcion = base.percepciones.get(pos, {})
        if percepcion.get('stench') and not base.wumpus_confirmado:
            vecinas = adyacentes(agente.x, agente.y)
            candidatas_wumpus = [
                v for v in vecinas
                if v not in base.seguras and v not in base.no_wumpus
            ]
            if len(candidatas_wumpus) == 2:
                return _orientar_y_disparar(agente, candidatas_wumpus)

    def _score_riesgo(casilla):
        score = 0
        for c in base.visitadas:
            perc = base.percepciones.get(c, {})
            vecinas_c = adyacentes(*c)
            if perc.get('breeze') and casilla in vecinas_c:
                score += 1
            if perc.get('stench') and casilla in vecinas_c:
                score += 1
        return score

    for visitada in base.visitadas:
        vecinas_visitada = adyacentes(*visitada)
        opciones = [v for v in vecinas_visitada
                    if v not in base.visitadas and v not in base.peligrosas and v not in base.pozos_confirmados]
        if opciones:
            mejor = min(opciones, key=_score_riesgo)
            if visitada == pos:
                return ('mover', mejor)
            camino = _camino_seguro(pos, visitada, base)
            if camino:
                return ('mover', camino[0])

    vecinas = adyacentes(agente.x, agente.y)
    arriesgadas = [v for v in vecinas if v not in base.visitadas]
    if arriesgadas:
        destino = min(arriesgadas, key=_score_riesgo)
        return ('mover', destino)

    return ('detener', None)


def simular():
    tablero = generar_tablero()
    agente = Agente()
    base = BaseConocimiento()
    paso = 1
    hay_grito = False
    hubo_golpe = False
    historial = []

    print("=" * 60)
    print("  SIMULACION - MUNDO DEL WUMPUS (Sistema Experto)")
    print("=" * 60)
    print("-" * 60)

    while agente.vivo:
        pos_actual = (agente.x, agente.y)
        historial.append(pos_actual)
        if len(historial) > 12:
            historial.pop(0)

        if len(historial) >= 4:
            ultimas4 = historial[-4:]
            if ultimas4[0] == ultimas4[2] and ultimas4[1] == ultimas4[3]:
                print(f"\n  -> Agente atrapado en ciclo. Fin de la simulacion.")
                break

        percepcion = percibir(tablero, agente.x, agente.y, hay_grito, hubo_golpe)
        base.registrar_percepcion(agente.x, agente.y, percepcion)
        hay_grito = False
        hubo_golpe = False

        print(f"\nPaso {paso}: Agente en ({agente.x}, {agente.y}). Percibe: {percepcion}")

        inferir(base)

        mostrar_tablero(agente, base)

        if percepcion['glitter']:
            agente.agarrar_oro()
            print("  -> Encontro el oro! Lo agarra.")
            print("  -> Regresando a (1,1) para salir...")
            while (agente.x, agente.y) != (1, 1):
                if (1, 1) in base.seguras:
                    print(f"  -> Mueve a (1, 1)")
                    agente.mover_a(1, 1)
                else:
                    print("  -> No hay camino seguro de regreso. Fin.")
                    break
            if (agente.x, agente.y) == (1, 1):
                print("\n" + "=" * 60)
                print("  SIMULACION TERMINADA CON EXITO! El agente salio con el oro.")
                print("=" * 60)
                print("\n  Estado REAL del tablero (para verificacion del observador):")
                print(f"  Wumpus: {tablero['wumpus']}")
                print(f"  Pozos:  {tablero['pozos']}")
                print(f"  Oro:    {tablero['oro']}")
            break

        accion, destino = elegir_accion(agente, base)

        if accion == 'mover':
            print(f"  -> Accion: mover a {destino}")
            agente.mover_a(*destino)
            if destino in tablero['pozos']:
                agente.morir()
                print(f"  -> El agente cayo en un pozo en {destino}!")
            elif destino == tablero['wumpus'] and tablero.get('wumpus_vivo', True):
                agente.morir()
                print(f"  -> El agente fue devorado por el Wumpus en {destino}!")

        elif accion == 'disparar':
            print("  -> Accion: DISPARAR FLECHA (hedor detectado)")
            grito = disparar_flecha(tablero, agente.x, agente.y, agente.orientacion)
            agente.usar_flecha()
            if grito:
                print("  -> Grito! El Wumpus murio.")
                hay_grito = True
                base.marcar_wumpus_muerto()
            else:
                print("  -> La flecha no dio en el Wumpus. Se perdio.")

        elif accion == 'salir':
            agente.salir_de_cueva()
            print("\n" + "=" * 60)
            print("  SIMULACION TERMINADA CON EXITO! El agente salio con el oro.")
            print("=" * 60)
            print("\n  Estado REAL del tablero (para verificacion del observador):")
            print(f"  Wumpus: {tablero['wumpus']}")
            print(f"  Pozos:  {tablero['pozos']}")
            print(f"  Oro:    {tablero['oro']}")
            break

        else:
            print("  -> No quedan casillas seguras por explorar. Fin de la simulacion.")
            break

        paso += 1

    if not agente.vivo:
        print("\n" + "=" * 60)
        print("  SIMULACION TERMINADA - El agente murio.")
        print("=" * 60)
        print("\n  Estado REAL del tablero (para verificacion del observador):")
        print(f"  Wumpus: {tablero['wumpus']}")
        print(f"  Pozos:  {tablero['pozos']}")
        print(f"  Oro:    {tablero['oro']}")


if __name__ == '__main__':
    simular()
