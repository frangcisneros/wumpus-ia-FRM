from tablero import TAMANIO


def mostrar_tablero(agente, base):
    """Muestra el tablero ASCII según lo que el agente conoce (sin hacer trampa)."""
    print("\n  Tablero (vista del agente):")
    print("  +" + "---+" * TAMANIO)

    for fila in range(TAMANIO, 0, -1):
        linea = "  |"
        for col in range(1, TAMANIO + 1):
            casilla = (col, fila)

            if casilla == (agente.x, agente.y):
                if agente.tiene_oro:
                    celda = " A*"
                else:
                    celda = " A "
            elif casilla in base.pozos_confirmados:
                celda = " P "
            elif casilla == base.wumpus_confirmado:
                celda = " W "
            elif casilla in base.peligrosas:
                celda = " ! "
            elif casilla in base.visitadas:
                percepcion = base.percepciones.get(casilla, {})
                partes = []
                if percepcion.get('breeze'):
                    partes.append("B")
                if percepcion.get('stench'):
                    partes.append("S")
                if percepcion.get('glitter'):
                    partes.append("G")
                if partes:
                    celda = " " + "".join(partes) + " "
                else:
                    celda = " . "
            elif casilla in base.seguras:
                celda = " ? "
            else:
                celda = "   "

            linea += celda + "|"
        print(linea)
        print("  +" + "---+" * TAMANIO)

    print("\n  Leyenda:")
    print("  A  = Agente    A* = Agente con oro    .  = Segura visitada")
    print("  ?  = Segura por explorar    !  = Peligrosa    B = Brisa")
    print("  S  = Hedor     P  = Pozo confirmado   W = Wumpus confirmado")
