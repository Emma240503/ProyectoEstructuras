"""
pedidos.py.

Se encarga de la aparición de los pedidos
en el mapa del juego.
"""

from collections import deque
from clases import Pedido
import random


def obtener_casillas_libres(mapa, ocupadas=None):
    """Obtiene todas las casillas libres del mapa.

    Es decir aquella que no esté bloqueada ("B") y no esté
    incluida en el conjunto de casillas ocupadas.

    Args:
        mapa (list[list[str]]): Matriz del mapa.
        ocupadas (set | None): Conjunto opcional de tuplas (x, y)
            que representan casillas ya ocupadas.

    Returns:
        list[tuple[int, int]]: Lista de coordenadas libres del mapa.
    """
    if ocupadas is None:
        ocupadas = set()

    casillas_libres = []
    for y in range(len(mapa)):
        for x in range(len(mapa[0])):
            if mapa[y][x] != "B" and (x, y) not in ocupadas:
                casillas_libres.append((x, y))
    return casillas_libres


def asignar_posicion_aleatoria(mapa, ocupadas, separacion=4):
    """Asigna una casilla aleatoria libre respetando separación mínima.

    La función busca una casilla libre que no esté bloqueada ni ocupada
    y que además cumpla con una distancia mínima definida por `separacion`
    respecto a cualquier casilla ocupada.

    Args:
        mapa (list[list[str]]): Matriz del mapa.
        ocupadas (set): Conjunto de tuplas (x, y) que representan
            casillas ocupadas.
        separacion (int): Distancia mínima alrededor de la casilla candidata.

    Returns:
        list[int] | None: Coordenadas [x, y] si se encuentra espacio válido,
        o None si no existe ninguna casilla adecuada.
    """
    casillas_libres = obtener_casillas_libres(mapa, ocupadas)
    random.shuffle(casillas_libres)
    # Mezclar para obtener posiciones aleatorias.

    for nx, ny in casillas_libres:
        libre = True
        for sx in range(-separacion, separacion + 1):
            for sy in range(-separacion, separacion + 1):
                tx, ty = nx + sx, ny + sy
                if 0 <= tx < len(mapa[0]) and 0 <= ty < len(mapa):
                    if (tx, ty) in ocupadas:
                        libre = False
                        break
            if not libre:
                break

        if libre:
            ocupadas.add((nx, ny))
            return [nx, ny]

    return None


def reubicar_pedidos(pedidos, mapa, ocupadas=None, separacion=4):
    """Reubica pedidos evitando casillas bloqueadas u ocupadas.

    Si un pickup o dropoff se encuentra en una casilla inválida, se busca
    la casilla libre más cercana mediante BFS,
    respetando una separación mínima.

    Args:
        pedidos (list[dict]): Lista de pedidos, cada uno con claves
            "pickup" y "dropoff".
        mapa (list[list[str]]): Matriz del mapa.
        ocupadas (set | None): Conjunto de tuplas (x, y) ya ocupadas.
        separacion (int): Distancia mínima a mantener respecto a
            otras casillas ocupadas.
    """
    if ocupadas is None:
        ocupadas = set()

    for p in pedidos:
        for punto in ["pickup", "dropoff"]:
            x0, y0 = p[punto]

            if mapa[y0][x0] == "B" or (x0, y0) in ocupadas:
                visitados = set()
                cola = deque([(x0, y0)])
                encontrado = False
                intentos = 0
                max_intentos = len(mapa) * len(mapa[0])

                while cola and not encontrado and intentos < max_intentos:
                    intentos += 1
                    x, y = cola.popleft()

                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < len(mapa[0]) and 0 <= ny < len(mapa):
                            if (nx, ny) not in visitados:
                                visitados.add((nx, ny))

                                libre = (
                                        mapa[ny][nx] != "B"
                                        and (nx, ny) not in ocupadas
                                )

                                if libre and separacion > 0:
                                    for sx in range(
                                            -separacion, separacion + 1):
                                        for sy in range(
                                                -separacion, separacion + 1):
                                            tx, ty = nx + sx, ny + sy
                                            if (0 <= tx < len(mapa[0])
                                                    and 0 <= ty < len(mapa)):
                                                if (tx, ty) in ocupadas:
                                                    libre = False
                                                    break
                                        if not libre:
                                            break

                                if libre:
                                    p[punto] = [nx, ny]
                                    ocupadas.add((nx, ny))
                                    encontrado = True
                                    break
                                else:
                                    cola.append((nx, ny))

                # Si no se encontró lugar, mover a casilla libre cercana
                if not encontrado:
                    for dx in range(-3, 4):
                        for dy in range(-3, 4):
                            nx, ny = x0 + dx, y0 + dy
                            if 0 <= nx < len(mapa[0]) and 0 <= ny < len(mapa):
                                if mapa[ny][nx] != "B":
                                    p[punto] = [nx, ny]
                                    ocupadas.add((nx, ny))
                                    encontrado = True
                                    break
                        if encontrado:
                            break
            else:
                ocupadas.add((x0, y0))


def crear_objetos_pedidos(pedidos_data):
    """Crea instancias de Pedido a partir de datos JSON.

    Args:
        pedidos_data (list[dict]): Lista de diccionarios obtenidos de la API,
            cada uno con claves como "pickup", "dropoff", "weight", etc.

    Returns:
        list[Pedido]: Lista de objetos Pedido construidos.
    """
    return [Pedido(p["pickup"], p["dropoff"],
                   p.get("weight", 1), p.get("priority", 0),
                   p.get("payout", 100)) for p in
            pedidos_data]
