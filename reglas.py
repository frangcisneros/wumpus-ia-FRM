from tablero import adyacentes, TAMANIO


def regla_casilla_visitada_es_segura(casilla, base):
    """
    SI una casilla fue visitada y el agente sobrevivió
    ENTONCES esa casilla es confirmada como segura.
    """
    conclusiones = []
    if casilla in base.visitadas:
        conclusiones.append(('segura', casilla))
        conclusiones.append(('no_pozo', casilla))
        conclusiones.append(('no_wumpus', casilla))
    return conclusiones


def regla_sin_breeze_ni_stench(casilla, base):
    """
    SI no hubo breeze ni stench en 'casilla'
    ENTONCES todas sus casillas adyacentes son seguras (libres de pozo y Wumpus).
    """
    conclusiones = []
    percepcion = base.percepciones.get(casilla, {})
    if not percepcion:
        return conclusiones

    wumpus_muerto = getattr(base, 'wumpus_muerto', False)
    stench_activo = percepcion.get('stench', False) and not wumpus_muerto

    if not percepcion.get('breeze', False) and not stench_activo:
        for vecina in adyacentes(*casilla):
            conclusiones.append(('segura', vecina))
            conclusiones.append(('no_pozo', vecina))
            conclusiones.append(('no_wumpus', vecina))

    return conclusiones


def regla_sin_breeze(casilla, base):
    """
    SI no hay breeze en 'casilla'
    ENTONCES ninguna de sus casillas adyacentes contiene un pozo.
    """
    conclusiones = []
    percepcion = base.percepciones.get(casilla, {})
    if percepcion and not percepcion.get('breeze', False):
        for vecina in adyacentes(*casilla):
            conclusiones.append(('no_pozo', vecina))
    return conclusiones


def regla_sin_stench(casilla, base):
    """
    SI no hay stench en 'casilla' (o el Wumpus está muerto)
    ENTONCES ninguna de sus casillas adyacentes contiene un Wumpus vivo.
    """
    conclusiones = []
    percepcion = base.percepciones.get(casilla, {})
    wumpus_muerto = getattr(base, 'wumpus_muerto', False)

    if wumpus_muerto or (percepcion and not percepcion.get('stench', False)):
        for vecina in adyacentes(*casilla):
            conclusiones.append(('no_wumpus', vecina))
    return conclusiones


def regla_breeze_confirmar_pozo(casilla, base):
    """
    SI hay breeze en 'casilla'
    Y todas sus adyacentes menos una están confirmadas como libres de pozo (segura o no_pozo)
    ENTONCES esa única adyacente restante es un POZO CONFIRMADO (peligrosa).
    """
    conclusiones = []
    percepcion = base.percepciones.get(casilla, {})
    if percepcion and percepcion.get('breeze', False):
        vecinas = adyacentes(*casilla)
        no_pozo_set = getattr(base, 'no_pozo', set())
        sospechosas = [
            v for v in vecinas
            if v not in base.seguras and v not in no_pozo_set
        ]
        if len(sospechosas) == 1:
            pozo = sospechosas[0]
            conclusiones.append(('pozo_confirmado', pozo))
            conclusiones.append(('peligrosa', pozo))
    return conclusiones


def regla_stench_confirmar_wumpus(casilla, base):
    """
    SI hay stench en 'casilla'
    Y el Wumpus no está muerto
    Y todas sus adyacentes menos una están libres de Wumpus (segura o no_wumpus)
    ENTONCES esa única adyacente restante es el WUMPUS CONFIRMADO (peligrosa).
    """
    conclusiones = []
    percepcion = base.percepciones.get(casilla, {})
    wumpus_muerto = getattr(base, 'wumpus_muerto', False)

    if percepcion and percepcion.get('stench', False) and not wumpus_muerto:
        vecinas = adyacentes(*casilla)
        no_wumpus_set = getattr(base, 'no_wumpus', set())
        sospechosas = [
            v for v in vecinas
            if v not in base.seguras and v not in no_wumpus_set
        ]
        if len(sospechosas) == 1:
            wumpus_loc = sospechosas[0]
            conclusiones.append(('wumpus_confirmado', wumpus_loc))
            conclusiones.append(('peligrosa', wumpus_loc))
    return conclusiones


def regla_interseccion_stench(casilla, base):
    """
    SI hay stench percibido en múltiples casillas visitadas
    ENTONCES el Wumpus solo puede estar en la intersección de sus adyacentes.
    Cualquier adyacente fuera de la intersección se deduce como libre de Wumpus.
    """
    conclusiones = []
    wumpus_muerto = getattr(base, 'wumpus_muerto', False)
    if wumpus_muerto:
        return conclusiones

    casillas_con_stench = [
        c for c in base.visitadas
        if base.percepciones.get(c, {}).get('stench', False)
    ]

    if len(casillas_con_stench) >= 2:
        # Calcular intersección de adyacentes de todas las casillas con stench
        candidatas = set(adyacentes(*casillas_con_stench[0]))
        for c in casillas_con_stench[1:]:
            candidatas &= set(adyacentes(*c))

        # Todas las adyacentes a casillas con stench que no estén en la intersección son no_wumpus
        for c in casillas_con_stench:
            for vecina in adyacentes(*c):
                if vecina not in candidatas:
                    conclusiones.append(('no_wumpus', vecina))

        if len(candidatas) == 1:
            wumpus_loc = next(iter(candidatas))
            conclusiones.append(('wumpus_confirmado', wumpus_loc))
            conclusiones.append(('peligrosa', wumpus_loc))

    return conclusiones


def regla_descarte_wumpus_por_muerte(casilla, base):
    """
    SI se percibió un grito (scream) en cualquier momento
    ENTONCES el Wumpus está muerto y todas las casillas del tablero quedan libres de peligro de Wumpus.
    """
    conclusiones = []
    percepcion = base.percepciones.get(casilla, {})
    if percepcion.get('scream', False) or getattr(base, 'wumpus_muerto', False):
        conclusiones.append(('wumpus_muerto', True))
        for x in range(1, TAMANIO + 1):
            for y in range(1, TAMANIO + 1):
                conclusiones.append(('no_wumpus', (x, y)))
    return conclusiones


def regla_deducir_casilla_segura(casilla, base):
    """
    SI una casilla es confirmada como no_pozo Y (no_wumpus O Wumpus muerto)
    ENTONCES la casilla es declarada totalmente SEGURA.
    """
    conclusiones = []
    no_pozo_set = getattr(base, 'no_pozo', set())
    no_wumpus_set = getattr(base, 'no_wumpus', set())
    wumpus_muerto = getattr(base, 'wumpus_muerto', False)

    for x in range(1, TAMANIO + 1):
        for y in range(1, TAMANIO + 1):
            c = (x, y)
            if c in no_pozo_set and (c in no_wumpus_set or wumpus_muerto):
                conclusiones.append(('segura', c))
    return conclusiones


# Lista exportada de reglas de producción del sistema experto en el orden sugerido de evaluación
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
