from reglas import REGLAS

TIPOS_SOPORTADOS = ('segura', 'peligrosa', 'no_pozo', 'no_wumpus',
                    'pozo_confirmado', 'wumpus_confirmado', 'wumpus_muerto')


def _incorporar(base, tipo, destino):
    """Aplica una conclusion a la base y devuelve True si es novedad."""
    if tipo == 'segura':
        if destino not in base.seguras:
            base.marcar_segura(destino)
            return True
    elif tipo == 'peligrosa':
        if destino not in base.peligrosas:
            base.marcar_peligrosa(destino)
            return True
    elif tipo == 'no_pozo':
        if destino not in base.no_pozo:
            base.marcar_no_pozo(destino)
            return True
    elif tipo == 'no_wumpus':
        if destino not in base.no_wumpus:
            base.marcar_no_wumpus(destino)
            return True
    elif tipo == 'pozo_confirmado':
        if destino not in base.pozos_confirmados:
            base.marcar_pozo_confirmado(destino)
            return True
    elif tipo == 'wumpus_confirmado':
        if base.wumpus_confirmado != destino:
            base.marcar_wumpus_confirmado(destino)
            return True
    elif tipo == 'wumpus_muerto':
        if not base.wumpus_muerto:
            base.marcar_wumpus_muerto()
            return True
    return False


def aplicar_reglas(base, traza=None):
    """Recorre todas las casillas visitadas y dispara cada regla.

    Devuelve True si se agrego conocimiento nuevo (para repetir el
    ciclo, tal como hace un motor de encadenamiento hacia adelante).
    Si se pasa 'traza', registra cada (regla, tipo, destino) aplicado.
    """
    hubo_novedades = False
    for casilla in list(base.visitadas):
        for regla in REGLAS:
            conclusiones = regla(casilla, base)
            for tipo, destino in conclusiones:
                if tipo not in TIPOS_SOPORTADOS:
                    raise ValueError(
                        f"Tipo de conclusion no soportado por el motor: {tipo!r}"
                    )
                if _incorporar(base, tipo, destino):
                    hubo_novedades = True
                    if traza is not None:
                        traza.append((regla.__name__, tipo, destino))
    return hubo_novedades


def inferir(base, traza=None):
    """Aplica las reglas repetidas veces hasta el punto fijo.

    Devuelve la lista de inferencias aplicadas (regla, tipo, destino),
    util para imprimir la traza del razonamiento.
    """
    aplicadas = traza if traza is not None else []
    while aplicar_reglas(base, aplicadas):
        pass
    return aplicadas