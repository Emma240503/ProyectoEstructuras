"""
clases.py.

Se crea la clase "Pedido" y se crea la clase
"ColaPedidos" que será utilizada mediante un
heap para ordenar los pedidos por prioridad.
"""

import heapq


class Pedido:
    """Representa un pedido con información de recogida, entrega y prioridad.

    Attributes:
        pickup (list[int] | tuple[int, int]):
            Coordenadas donde se recoge el pedido.
        dropoff (list[int] | tuple[int, int]):
            Coordenadas donde se entrega el pedido.
        weight (int):
            Peso del pedido. Útil para cálculos futuros.
        priority (int):
            Prioridad del pedido. Valores mayores representan
            mayor urgencia.
        payout (int):
            Recompensa monetaria al completar el pedido.
    """

    def __init__(self, pickup, dropoff, weight=1, priority=0, payout=100):
        """Inicializa un objeto Pedido.

        Args:
            pickup (list[int] | tuple[int, int]): Posición de recogida.
            dropoff (list[int] | tuple[int, int]): Posición de entrega.
            weight (int, optional): Peso del pedido. Por defecto 1.
            priority (int, optional): Nivel de prioridad. Por defecto 0.
            payout (int, optional): Pago por completar el pedido.
                Por defecto 100.
        """
        self.pickup = pickup
        self.dropoff = dropoff
        self.weight = weight
        self.priority = priority  # entre más alto, más urgente
        self.payout = payout

    def __lt__(self, other):
        """Define el orden entre pedidos basado en prioridad.

        Permite usar objetos Pedido dentro de un heap, donde los pedidos
        con mayor prioridad deben salir primero.

        Args:
            other (Pedido): Otro pedido con el cual comparar.

        Returns:
            bool: ``True`` si este pedido tiene mayor prioridad que ``other``.
        """
        return self.priority > other.priority


class ColaPedidos:
    """Cola de pedidos basada en un heap de prioridades.

    Esta estructura permite obtener siempre el pedido de mayor prioridad.

    Attributes:
        cola (list[Pedido]):
            Lista interna usada como heap para almacenar pedidos.
    """

    def __init__(self, lista_pedidos):
        """Inicializa la cola y construye el heap a partir de una lista.

        Args:
            lista_pedidos (list[dict]):
                Lista de diccionarios con datos de los pedidos.
                Cada diccionario debe incluir al menos:
                - "pickup"
                - "dropoff"
                Puede incluir opcionalmente:
                - "weight"
                - "priority"
                - "payout"
        """
        self.cola = []
        for p in lista_pedidos:
            pedido = Pedido(
                p["pickup"],
                p["dropoff"],
                p.get("weight", 1),
                p.get("priority", 0),
                p.get("payout", 100)
            )
            heapq.heappush(self.cola, pedido)

    def agregar_pedido(self, pedido):
        """Agrega un pedido a la cola de prioridades.

        Args:
            pedido (Pedido): El pedido a agregar.
        """
        heapq.heappush(self.cola, pedido)

    def obtener_siguiente(self):
        """Extrae el pedido con mayor prioridad.

        Returns:
            Pedido | None:
                El pedido de mayor prioridad del heap.
                Retorna ``None`` si la cola está vacía.
        """
        if self.cola:
            return heapq.heappop(self.cola)  # sale el de mayor prioridad
        return None
