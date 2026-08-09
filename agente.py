from tablero import TAMANIO, DIRECCIONES


class Agente:
    """
    Representa el estado físico del agente dentro del Mundo del Wumpus.
    No toma decisiones lógicas por sí mismo: solo almacena estado y ejecuta
    las acciones físicas que el orquestador o motor le indiquen.
    """

    ORDEN_DIRECCIONES = ['este', 'norte', 'oeste', 'sur']

    def __init__(self, x=1, y=1, orientacion='este'):
        self.x = x
        self.y = y
        self.orientacion = orientacion  # 'este', 'norte', 'oeste', 'sur'
        self.tiene_oro = False
        self.tiene_flecha = True
        self.vivo = True
        self.salio_de_cueva = False

    def mover_a(self, x, y):
        """Mueve directamente al agente a la casilla indicada (x, y)."""
        self.x = x
        self.y = y

    def avanzar(self):
        """
        Intenta avanzar una casilla en la dirección actual.
        Si choca contra una pared, no cambia su posición y retorna True (hubo golpe).
        """
        dx, dy = DIRECCIONES[self.orientacion]
        nueva_x = self.x + dx
        nueva_y = self.y + dy

        if 1 <= nueva_x <= TAMANIO and 1 <= nueva_y <= TAMANIO:
            self.x = nueva_x
            self.y = nueva_y
            return False  # No hubo golpe
        else:
            return True  # Chocó contra un límite del tablero (Bump)

    def girar_izquierda(self):
        """Gira 90 grados a la izquierda."""
        idx = self.ORDEN_DIRECCIONES.index(self.orientacion)
        self.orientacion = self.ORDEN_DIRECCIONES[(idx + 1) % 4]

    def girar_derecha(self):
        """Gira 90 grados a la derecha."""
        idx = self.ORDEN_DIRECCIONES.index(self.orientacion)
        self.orientacion = self.ORDEN_DIRECCIONES[(idx - 1) % 4]

    def agarrar_oro(self):
        """Toma la pieza de oro si está en la casilla actual."""
        self.tiene_oro = True

    def usar_flecha(self):
        """
        Dispara la única flecha disponible.
        Retorna True si tenía la flecha y se disparó, False si no tenía flechas.
        """
        if self.tiene_flecha:
            self.tiene_flecha = False
            return True
        return False

    def salir_de_cueva(self):
        """Sale de la cueva (únicamente posible desde la casilla (1, 1))."""
        if self.x == 1 and self.y == 1:
            self.salio_de_cueva = True
            return True
        return False

    def morir(self):
        """Marca al agente como fallecido."""
        self.vivo = False

    def __repr__(self):
        return (
            f"Agente(pos=({self.x}, {self.y}), orientacion='{self.orientacion}', "
            f"oro={self.tiene_oro}, flecha={self.tiene_flecha}, vivo={self.vivo})"
        )
