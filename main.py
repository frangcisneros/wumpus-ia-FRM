from tablero import generar_tablero, percibir, adyacentes, disparar_flecha, TAMANIO
from agente import Agente
from base_conocimiento import BaseConocimiento
from motor_inferencia import inferir
from visualizacion import mostrar_tablero


def elegir_accion(agente, base):
    """Política de decisión: elige la próxima acción basándose en la base de conocimiento."""
    if agente.tiene_oro and (agente.x, agente.y) == (1, 1):
        return ('salir', None)

    if agente.tiene_oro:
        destino = (1, 1)
        if destino in base.seguras:
            return ('mover', destino)
        return ('detener', None)

    if agente.tiene_flecha and not base.wumpus_muerto:
        percepcion = base.percepciones.get((agente.x, agente.y), {})
        if percepcion.get('stench') and base.wumpus_confirmado:
            return ('disparar', None)

    candidatas = base.casillas_por_explorar()
    if candidatas:
        destino = min(candidatas, key=lambda c: abs(c[0] - agente.x) + abs(c[1] - agente.y))
        return ('mover', destino)

    return ('detener', None)


def simular():
    """Ejecuta la simulación completa: ciclo percibir → inferir → decidir → actuar."""
    tablero = generar_tablero()
    agente = Agente()
    base = BaseConocimiento()
    paso = 1
    hay_grito = False
    hubo_golpe = False

    print("=" * 60)
    print("  SIMULACIÓN - MUNDO DEL WUMPUS (Sistema Experto)")
    print("=" * 60)
    print("-" * 60)

    while agente.vivo:
        percepcion = percibir(tablero, agente.x, agente.y, hay_grito, hubo_golpe)
        base.registrar_percepcion(agente.x, agente.y, percepcion)
        hay_grito = False
        hubo_golpe = False

        print(f"\nPaso {paso}: Agente en ({agente.x}, {agente.y}). Percibe: {percepcion}")

        inferir(base)

        mostrar_tablero(agente, base)

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

        accion, destino = elegir_accion(agente, base)

        if accion == 'mover':
            print(f"  -> Acción: mover a {destino} (casilla segura)")
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
