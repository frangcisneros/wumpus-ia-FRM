import random

TAMANIO = 4

# Vectores de dirección para navegación y disparos
DIRECCIONES = {
    'este': (1, 0),
    'norte': (0, 1),
    'oeste': (-1, 0),
    'sur': (0, -1)
}


def generar_tablero(cant_pozos=2):
    """
    Genera un tablero aleatorio de 4x4 respetando las reglas del juego:
    - Casillas (1,1), (1,2) y (2,1) siempre libres de Wumpus, Pozos y Oro.
    - 1 Wumpus en posición aleatoria.
    - 'cant_pozos' Pozos en posiciones aleatorias (por defecto 2, entre 1 y 3).
    - 1 pieza de Oro en posición aleatoria.
    """
    seguras = {(1, 1), (1, 2), (2, 1)}
    casillas_disponibles = [
        (x, y)
        for x in range(1, TAMANIO + 1)
        for y in range(1, TAMANIO + 1)
        if (x, y) not in seguras
    ]
    random.shuffle(casillas_disponibles)

    wumpus = casillas_disponibles.pop()

    pozos = [casillas_disponibles.pop() for _ in range(cant_pozos)]

    oro = casillas_disponibles.pop()

    return {
        'wumpus': wumpus,
        'pozos': pozos,
        'oro': oro,
        'wumpus_vivo': True
    }


def adyacentes(x, y):
    """
    Devuelve las casillas adyacentes válidas (ortogonales) dentro de los límites del tablero 4x4.
    """
    candidatas = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    return [(a, b) for a, b in candidatas if 1 <= a <= TAMANIO and 1 <= b <= TAMANIO]


def percibir(tablero, x, y, hay_grito=False, hubo_golpe=False):
    """
    Retorna el diccionario de percepciones que el agente siente en la casilla (x, y).
    - breeze: Hay al menos un pozo adyacente.
    - stench: El Wumpus está vivo y en una casilla adyacente.
    - glitter: El oro está en la casilla actual.
    - bump: Ocurrió un golpe contra el muro al intentar avanzar.
    - scream: El Wumpus acaba de morir por el disparo de una flecha.
    """
    vecinas = adyacentes(x, y)
    wumpus_vivo = tablero.get('wumpus_vivo', True)

    return {
        'breeze': any(v in tablero['pozos'] for v in vecinas),
        'stench': wumpus_vivo and (tablero['wumpus'] in vecinas),
        'glitter': (x, y) == tablero['oro'],
        'bump': hubo_golpe,
        'scream': hay_grito
    }


def disparar_flecha(tablero, x, y, orientacion):
    """
    Simula el disparo de la flecha desde la casilla (x, y) en la dirección especificada.
    Recorre las casillas en línea recta. Si alcanza la posición del Wumpus y este está vivo,
    el Wumpus muere y devuelve True (grito). En caso contrario devuelve False.
    """
    if not tablero.get('wumpus_vivo', True):
        return False

    dx, dy = DIRECCIONES[orientacion]
    curr_x, curr_y = x + dx, y + dy

    while 1 <= curr_x <= TAMANIO and 1 <= curr_y <= TAMANIO:
        if (curr_x, curr_y) == tablero['wumpus']:
            tablero['wumpus_vivo'] = False
            return True
        curr_x += dx
        curr_y += dy

    return False
