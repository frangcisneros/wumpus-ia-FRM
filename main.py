from tablero import generar_tablero, percibir, adyacentes, disparar_flecha, TAMANIO, DIRECCIONES
from agente import Agente
from base_conocimiento import BaseConocimiento
from motor_inferencia import inferir
from visualizacion import mostrar_tablero


def _direccion_hacia(origen, destino):
    """Devuelve la dirección ('este','norte','oeste','sur') para ir de origen a destino."""
    dx = destino[0] - origen[0]
    dy = destino[1] - origen[1]
    for nombre, (vx, vy) in DIRECCIONES.items():
        if (vx, vy) == (dx, dy):
            return nombre
    return None


def _orientar_y_disparar(agente, base, candidatas):
    """Intenta orientar al agente hacia una candidata y disparar."""
    for candidata in candidatas:
        dir_objetivo = _direccion_hacia((agente.x, agente.y), candidata)
        if dir_objetivo is None:
            continue
        while agente.orientacion != dir_objetivo:
            agente.girar_derecha()
        return ('disparar', None)
    return None


def _backtrack(agente, base, ultima_pos=None):
    """Busca una casilla visitada adyacente a la que se puede volver (excepto la última posición)."""
    vecinas = adyacentes(agente.x, agente.y)
    for v in vecinas:
        if v in base.visitadas and v in base.seguras and v != ultima_pos:
            return v
    return None


def _buscar_visitada_con_opciones(agente, base):
    """Busca una casilla visitada que tenga vecinas sin visitar y seguras."""
    for visitada in base.visitadas:
        vecinas = adyacentes(visitada[0], visitada[1])
        for v in vecinas:
            if v in base.seguras and v not in base.visitadas and v not in base.peligrosas:
                return visitada
    return None


def elegir_accion(agente, base, ultima_pos=None):
    """Política de decisión: elige la próxima acción basándose en la base de conocimiento."""
    if agente.tiene_oro and (agente.x, agente.y) == (1, 1):
        return ('salir', None)

    if agente.tiene_oro:
        destino = (1, 1)
        if destino in base.seguras:
            return ('mover', destino)
        backtrack = _backtrack(agente, base, ultima_pos)
        if backtrack:
            return ('mover', backtrack)
        return ('detener', None)

    candidatas = base.casillas_por_explorar()
    if candidatas:
        destino = min(candidatas, key=lambda c: abs(c[0] - agente.x) + abs(c[1] - agente.y))
        return ('mover', destino)

    if agente.tiene_flecha and not base.wumpus_muerto:
        percepcion = base.percepciones.get((agente.x, agente.y), {})
        if percepcion.get('stench') and not base.wumpus_confirmado:
            vecinas = adyacentes(agente.x, agente.y)
            candidatas = [v for v in vecinas if v not in base.seguras and v not in base.no_wumpus]
            if len(candidatas) == 2:
                return _orientar_y_disparar(agente, base, candidatas)

    visitada_opcion = _buscar_visitada_con_opciones(agente, base)
    if visitada_opcion:
        return ('mover', visitada_opcion)

    backtrack = _backtrack(agente, base, ultima_pos)
    if backtrack:
        return ('mover', backtrack)

    if agente.tiene_flecha and not base.wumpus_muerto:
        percepcion = base.percepciones.get((agente.x, agente.y), {})
        if percepcion.get('stench') and not base.wumpus_confirmado:
            vecinas = adyacentes(agente.x, agente.y)
            candidatas = [v for v in vecinas if v not in base.seguras and v not in base.no_wumpus]
            if len(candidatas) == 2:
                return _orientar_y_disparar(agente, base, candidatas)

    vecinas = adyacentes(agente.x, agente.y)
    candidatas_arriesgadas = [v for v in vecinas if v not in base.visitadas
                               and v not in base.peligrosas]
    if candidatas_arriesgadas:
        destino = candidatas_arriesgadas[0]
        return ('mover', destino)

    return ('detener', None)


def simular():
    """Ejecuta la simulación completa: ciclo percibir → inferir → decidir → actuar."""
    tablero = generar_tablero()
    agente = Agente()
    base = BaseConocimiento()
    paso = 1
    sin_avance = 0
    MAX_SIN_AVANCE = 30
    hay_grito = False
    hubo_golpe = False
    ultima_pos = None

    print("=" * 60)
    print("  SIMULACIÓN - MUNDO DEL WUMPUS (Sistema Experto)")
    print("=" * 60)
    print("-" * 60)

    while agente.vivo and sin_avance < MAX_SIN_AVANCE:
        seguras_antes = len(base.seguras)
        visitadas_antes = len(base.visitadas)

        percepcion = percibir(tablero, agente.x, agente.y, hay_grito, hubo_golpe)
        base.registrar_percepcion(agente.x, agente.y, percepcion)
        hay_grito = False
        hubo_golpe = False

        print(f"\nPaso {paso}: Agente en ({agente.x}, {agente.y}). Percibe: {percepcion}")

        inferir(base)

        mostrar_tablero(agente, base)

        seguras_despues = len(base.seguras)
        visitadas_despues = len(base.visitadas)
        hubo_avance = (seguras_despues > seguras_antes or visitadas_despues > visitadas_antes)

        if percepcion['glitter']:
            agente.agarrar_oro()
            print("  -> ¡Encontró el oro! Lo agarra.")
            print("  -> Regresando a (1,1) para salir...")
            while (agente.x, agente.y) != (1, 1):
                destino = (1, 1)
                if destino in base.seguras:
                    print(f"  -> Mueve a {destino}")
                    agente.mover_a(*destino)
                else:
                    backtrack = _backtrack(agente, base, ultima_pos)
                    if backtrack:
                        print(f"  -> Retrocede a {backtrack}")
                        ultima_pos = (agente.x, agente.y)
                        agente.mover_a(*backtrack)
                    else:
                        print("  -> No hay camino seguro de regreso. Fin.")
                        break
            if (agente.x, agente.y) == (1, 1):
                print("\n" + "=" * 60)
                print("  ¡SIMULACIÓN TERMINADA CON ÉXITO! El agente salió con el oro.")
                print("=" * 60)
                print("\n  Estado REAL del tablero (para verificación del observador):")
                print(f"  Wumpus: {tablero['wumpus']}")
                print(f"  Pozos:  {tablero['pozos']}")
                print(f"  Oro:    {tablero['oro']}")
            break

        accion, destino = elegir_accion(agente, base, ultima_pos)

        if accion == 'mover':
            print(f"  -> Acción: mover a {destino}")
            ultima_pos = (agente.x, agente.y)
            agente.mover_a(*destino)

        elif accion == 'disparar':
            print("  -> Acción: DISPARAR FLECHA (hedor detectado)")
            grito = disparar_flecha(tablero, agente.x, agente.y, agente.orientacion)
            agente.usar_flecha()
            if grito:
                print("  -> ¡Grito! El Wumpus murió.")
                hay_grito = True
                base.marcar_wumpus_muerto()
            else:
                print("  -> La flecha no dio en el Wumpus. Se perdió.")

        elif accion == 'salir':
            agente.salir_de_cueva()
            print("\n" + "=" * 60)
            print("  ¡SIMULACIÓN TERMINADA CON ÉXITO! El agente salió con el oro.")
            print("=" * 60)
            print("\n  Estado REAL del tablero (para verificación del observador):")
            print(f"  Wumpus: {tablero['wumpus']}")
            print(f"  Pozos:  {tablero['pozos']}")
            print(f"  Oro:    {tablero['oro']}")
            break

        else:
            print("  -> No quedan casillas seguras por explorar. Fin de la simulación.")
            break

        paso += 1
        if hubo_avance:
            sin_avance = 0
        else:
            sin_avance += 1

    if not agente.vivo:
        print("\n" + "=" * 60)
        print("  SIMULACIÓN TERMINADA - El agente murió.")
        print("=" * 60)
        print("\n  Estado REAL del tablero (para verificación del observador):")
        print(f"  Wumpus: {tablero['wumpus']}")
        print(f"  Pozos:  {tablero['pozos']}")
        print(f"  Oro:    {tablero['oro']}")


if __name__ == '__main__':
    simular()
