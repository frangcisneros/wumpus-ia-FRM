class BaseConocimiento:
    """Base de hechos del sistema experto.

    Almacena las percepciones acumuladas por casilla visitada y las
    conclusiones que el motor de inferencia deduce (segura, peligrosa,
    no_pozo, no_wumpus, pozo confirmado, wumpus confirmado).

    Solo registra y consulta hechos: no razona por si misma.
    """

    def __init__(self):
        self.percepciones = {}      # (x, y) -> {'breeze':.., 'stench':.., 'glitter':.., ...}
        self.seguras = {(1, 1)}
        self.peligrosas = set()
        self.visitadas = {(1, 1)}

        self.no_pozo = set()          # casillas libres de pozo (deducidas)
        self.no_wumpus = set()        # casillas libres de wumpus (deducidas)
        self.pozos_confirmados = set()
        self.wumpus_confirmado = None  # casilla donde se dedujo el wumpus
        self.wumpus_muerto = False

    def registrar_percepcion(self, x, y, percepcion):
        self.percepciones[(x, y)] = percepcion
        self.visitadas.add((x, y))

    def marcar_segura(self, casilla):
        self.seguras.add(casilla)
        self.peligrosas.discard(casilla)

    def marcar_peligrosa(self, casilla):
        self.peligrosas.add(casilla)

    def marcar_no_pozo(self, casilla):
        self.no_pozo.add(casilla)
        self.pozos_confirmados.discard(casilla)
        if casilla != self.wumpus_confirmado:
            self.peligrosas.discard(casilla)

    def marcar_no_wumpus(self, casilla):
        self.no_wumpus.add(casilla)
        if casilla == self.wumpus_confirmado:
            self.wumpus_confirmado = None
        if casilla not in self.pozos_confirmados:
            self.peligrosas.discard(casilla)

    def marcar_pozo_confirmado(self, casilla):
        self.pozos_confirmados.add(casilla)
        self.peligrosas.add(casilla)

    def marcar_wumpus_confirmado(self, casilla):
        self.wumpus_confirmado = casilla
        self.peligrosas.add(casilla)

    def marcar_wumpus_muerto(self):
        self.wumpus_muerto = True
        self.wumpus_confirmado = None
        self.peligrosas = {
            c for c in self.peligrosas
            if c in self.pozos_confirmados
        }

    def no_pozo_o_segura(self, casilla):
        return casilla in self.no_pozo or casilla in self.seguras

    def casillas_por_explorar(self):
        return self.seguras - self.visitadas - self.peligrosas