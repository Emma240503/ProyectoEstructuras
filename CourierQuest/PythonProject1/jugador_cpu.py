"""
jugador_cpu.py.

Implementa el jugador CPU con tres niveles de dificultad:
- Fácil: Movimiento aleatorio
- Media: Evaluación con heurísticas (Greedy/Expectimax)
- Difícil: Rutas óptimas con A*/Dijkstra
"""

import random
import time
from jugador import Jugador


class JugadorCPU(Jugador):
    """Jugador controlado por IA con diferentes niveles de dificultad."""

    def __init__(self, x, y, dificultad='facil', capacidad=10):
        """Inicializa la IA del jugador CPU.

        Args:
            x (int): Posición inicial en el eje X.
            y (int): Posición inicial en el eje Y.
            dificultad (str): Nivel de IA ('facil', 'media', 'dificil').
            capacidad (int): Capacidad máxima de peso que puede cargar.
        """
        super().__init__(x, y, capacidad)
        self.dificultad = dificultad

        # Variables para nivel fácil
        self.objetivo_actual = None  # Pedido objetivo o [x, y]
        self.ultimo_cambio_objetivo = time.time()
        self.tiempo_cambio_objetivo = random.randint(3, 6)  # Segundos

        # Control de velocidad de movimiento
        self.movimientos_por_segundo = 8  # Movimientos por segundo
        self.tiempo_entre_movimientos = 1.0 / self.movimientos_por_segundo
        self.ultimo_movimiento = time.time()

        # Detección de bucles (para evitar quedar atrapado)
        self.historial_posiciones = []  # Últimas 10 posiciones
        self.max_historial = 10
        self.modo_escape = False
        self.tiempo_escape = 0
        self.duracion_escape = 2  # Segundos en modo escape

        # Variables para nivel medio (implementar después)
        self.horizonte_busqueda = 3  # Profundidad de búsqueda

        # Variables para nivel difícil (implementar después)
        self.ruta_planeada = []  # Lista de posiciones [x, y]

        self.clima_mult_anterior = 1.0
        self.ultimo_replan = 0

    def actualizar(self, mapa, pedidos_activos,
                   clima_mult, consumo_clima_extra):
        """Actualiza el comportamiento del CPU según su dificultad.

        Args:
            mapa (list[list[str]]): Matriz del mapa.
            pedidos_activos (list[Pedido]): Lista de pedidos disponibles.
            clima_mult (float): Multiplicador de movimiento según el clima.
            consumo_clima_extra (float): Costo adicional por clima.
        """
        # Recuperar resistencia (heredado de Jugador)
        self.recuperar()

        # Si está bloqueado por falta de resistencia, no hacer nada
        if self.bloqueado:
            return

        # Verificar si es tiempo de moverse (control de velocidad)
        ahora = time.time()
        if ahora - self.ultimo_movimiento < self.tiempo_entre_movimientos:
            return  # Todavía no es tiempo de moverse

        self.ultimo_movimiento = ahora

        # Seleccionar dificultad desde el menu
        if self.dificultad == 'facil':
            self._ia_facil(mapa, pedidos_activos,
                           clima_mult, consumo_clima_extra)
        elif self.dificultad == 'media':
            self._ia_media(mapa, pedidos_activos,
                           clima_mult, consumo_clima_extra)
        elif self.dificultad == 'dificil':
            self._ia_dificil(mapa, pedidos_activos,
                             clima_mult, consumo_clima_extra)

    # ========================================
    # NIVEL FÁCIL
    # ========================================

    def _ia_facil(self, mapa, pedidos_activos,
                  clima_mult, consumo_clima_extra):
        """IA básica con movimiento aleatorio y objetivos simples.

        Args:
            mapa (list[list[str]]): Mapa del juego.
            pedidos_activos (list[Pedido]): Pedidos no recogidos.
            clima_mult (float): Multiplicador climático.
            consumo_clima_extra (float): Costo adicional por clima.
        """
        ahora = time.time()

        # Guardar posición actual en historial
        self.historial_posiciones.append((self.x, self.y))
        if len(self.historial_posiciones) > self.max_historial:
            self.historial_posiciones.pop(0)

        # Detectar si está en un bucle
        if not self.modo_escape and len(self.historial_posiciones) >= 6:
            # Contar cuántas veces aparece la posición actual
            # en el historial reciente
            posicion_actual = (self.x, self.y)
            repeticiones = (self.historial_posiciones[-6:]
                            .count(posicion_actual))

            # Si ha estado en la misma posición 3+
            # veces en las últimas 6 posiciones
            if repeticiones >= 3:

                self.modo_escape = True
                self.tiempo_escape = ahora
                self.objetivo_actual = None  # Cambiar de objetivo

        # Desactivar modo escape
        if (self.modo_escape and
                (ahora - self.tiempo_escape > self.duracion_escape)):
            self.modo_escape = False
            self.historial_posiciones.clear()  # Limpiar historial

        # Verificar si hay que cambiar de objetivo
        if (self.objetivo_actual is None or
                ahora - self.ultimo_cambio_objetivo >
                self.tiempo_cambio_objetivo):
            self._elegir_objetivo_aleatorio(pedidos_activos)
            self.ultimo_cambio_objetivo = ahora
            self.tiempo_cambio_objetivo = random.randint(3, 6)

        # Intentar recoger pedido si estamos en un pickup
        for pedido in list(pedidos_activos):
            if [self.x, self.y] == pedido.pickup:
                if self.recoger_pedido(pedido):
                    pedidos_activos.remove(pedido)
                    # Si recogimos nuestro objetivo, cambiar a entrega
                    if self.objetivo_actual == pedido.pickup:
                        self.objetivo_actual = pedido.dropoff

        # Intentar entregar pedido
        entregado = self.entregar_pedido()
        if entregado:

            # Cambiar objetivo después de entregar
            self.objetivo_actual = None
            self.historial_posiciones.clear()  # Limpiar historial

        # Decidir movimiento según modo
        if self.modo_escape:

            self._mover_aleatorio(mapa, clima_mult, consumo_clima_extra)
        elif self.objetivo_actual:
            # Modo normal: 70% hacia objetivo, 30% aleatorio
            if random.random() < 0.7:
                (self._mover_hacia_objetivo
                 (mapa, clima_mult, consumo_clima_extra))
            else:
                self._mover_aleatorio(mapa, clima_mult, consumo_clima_extra)
        else:
            # Si no hay objetivo, moverse aleatorio
            self._mover_aleatorio(mapa, clima_mult, consumo_clima_extra)

    def _elegir_objetivo_aleatorio(self, pedidos_activos):
        """Selecciona aleatoriamente un pedido como objetivo.

        Args:
            pedidos_activos (list[Pedido]): Pedidos disponibles.
        """
        # Si tenemos pedidos en inventario, priorizar entregarlos
        if self.inventario:
            pedido_prioritario = max(self.inventario, key=lambda p: p.priority)
            self.objetivo_actual = pedido_prioritario.dropoff
            return

        # Si no, elegir un pedido disponible al azar
        if pedidos_activos:
            pedido_aleatorio = random.choice(pedidos_activos)
            self.objetivo_actual = pedido_aleatorio.pickup
        else:
            self.objetivo_actual = None

    def _mover_hacia_objetivo(self, mapa, clima_mult, consumo_clima_extra):
        """Se mueve aproximadamente hacia el objetivo actual.

        Args:
            mapa (list[list[str]]): Mapa del juego.
            clima_mult (float): Multiplicador climático.
            consumo_clima_extra (float): Costo extra por clima.
        """
        if not self.objetivo_actual:
            return

        objetivo_x, objetivo_y = self.objetivo_actual

        # Calcular diferencia
        diff_x = objetivo_x - self.x
        diff_y = objetivo_y - self.y

        # Si ya llegó al objetivo, no moverse
        if diff_x == 0 and diff_y == 0:
            return

        # Lista de direcciones a intentar (en orden de prioridad)
        intentos = []

        # Prioridad 1: Dirección hacia el objetivo (eje mayor)
        if abs(diff_x) > abs(diff_y):
            # Mover en X primero
            dx = 1 if diff_x > 0 else -1
            intentos.append((dx, 0))
            # Luego intentar Y
            if diff_y != 0:
                dy = 1 if diff_y > 0 else -1
                intentos.append((0, dy))
        else:
            # Mover en Y primero
            dy = 1 if diff_y > 0 else -1
            intentos.append((0, dy))
            # Luego intentar X
            if diff_x != 0:
                dx = 1 if diff_x > 0 else -1
                intentos.append((dx, 0))

        # Prioridad 2: Direcciones perpendiculares (para rodear obstáculos)
        if abs(diff_x) > abs(diff_y):
            # Si el eje principal es X, agregar movimientos en Y
            intentos.append((0, 1))
            intentos.append((0, -1))
        else:
            # Si el eje principal es Y, agregar movimientos en X
            intentos.append((1, 0))
            intentos.append((-1, 0))

        # Intentar cada dirección en orden
        for dx, dy in intentos:
            nx, ny = self.x + dx, self.y + dy

            # Verificar si es válido
            if (0 <= nx < len(mapa[0]) and
                    0 <= ny < len(mapa) and mapa[ny][nx] != "B"):
                # Verificar que no sea una posición reciente (evitar bucles)
                if ((nx, ny) not in
                        self.historial_posiciones[-4:]):
                    if self.mover(dx, dy, mapa, clima_mult,
                                  consumo_clima_extra):
                        return  # Movimiento exitoso

        # Si todos los intentos fallaron, moverse aleatorio
        self._mover_aleatorio(mapa, clima_mult, consumo_clima_extra)

    def _mover_aleatorio(self, mapa, clima_mult, consumo_clima_extra):
        """Realiza un movimiento aleatorio válido.

        Args:
            mapa (list[list[str]]): Mapa del juego.
            clima_mult (float): Multiplicador climático.
            consumo_clima_extra (float): Costo adicional.
        """
        # Direcciones posibles: arriba, abajo, izquierda, derecha
        direcciones = [
            (0, -1),  # Arriba
            (0, 1),  # Abajo
            (-1, 0),  # Izquierda
            (1, 0)  # Derecha
        ]

        # Mezclar para verdadera aleatoriedad
        random.shuffle(direcciones)

        # Filtrar direcciones válidas (que no sean edificios ni fuera del mapa)
        direcciones_validas = []
        direcciones_validas_no_recientes = []

        for dx, dy in direcciones:
            nx, ny = self.x + dx, self.y + dy

            # Verificar límites
            if not (0 <= nx < len(mapa[0]) and 0 <= ny < len(mapa)):
                continue

            # Verificar que no sea edificio
            if mapa[ny][nx] == "B":
                continue

            direcciones_validas.append((dx, dy))

            # Preferir direcciones que no estén en el historial reciente
            if (nx, ny) not in self.historial_posiciones[-4:]:
                direcciones_validas_no_recientes.append((dx, dy))

        # Intentar primero direcciones no recientes
        if direcciones_validas_no_recientes:
            dx, dy = direcciones_validas_no_recientes[0]
            self.mover(dx, dy, mapa, clima_mult, consumo_clima_extra)
        # Si no hay opciones nuevas, usar cualquier dirección válida
        elif direcciones_validas:
            dx, dy = direcciones_validas[0]
            self.mover(dx, dy, mapa, clima_mult, consumo_clima_extra)

    # ========================================
    # NIVEL MEDIO - GREEDY/EXPECTIMAX
    # ========================================

    def _ia_media(self, mapa, pedidos_activos,
                  clima_mult, consumo_clima_extra):
        """IA nivel medio (Expectimax).

        - Evalúa varios movimientos adelante (profundidad)
        - Calcula el valor esperado de cada
        movimiento considerando aleatoriedad
        - Elige el movimiento con mayor valor esperado
        Args:
            mapa (list[list[str]]): Mapa del juego.
            pedidos_activos (list[Pedido]): Pedidos disponibles.
            clima_mult (float): Multiplicador climático.
            consumo_clima_extra (float): Costo adicional.
        """

        ahora = time.time()

        # Guardar posición actual en historial
        self.historial_posiciones.append((self.x, self.y))
        if len(self.historial_posiciones) > self.max_historial:
            self.historial_posiciones.pop(0)

        # Detectar si está en bucle
        if not self.modo_escape and len(self.historial_posiciones) >= 6:
            pos_actual = (self.x, self.y)
            repeticiones = self.historial_posiciones[-6:].count(pos_actual)

            # Si ha estado en la misma posición 3+
            # veces en las últimas 6 posiciones
            if repeticiones >= 3:
                self.modo_escape = True
                self.tiempo_escape = ahora
                self.objetivo_actual = None

        # Desactivar modo escape después del tiempo
        if self.modo_escape and (ahora - self.tiempo_escape >
                                 self.duracion_escape):
            self.modo_escape = False
            self.historial_posiciones.clear()

        # Elegir objetivo (más cercano o más importante)
        if (self.objetivo_actual is None or
                ahora - self.ultimo_cambio_objetivo >
                self.tiempo_cambio_objetivo):
            self._elegir_objetivo_expectimax(pedidos_activos)
            self.ultimo_cambio_objetivo = ahora
            self.tiempo_cambio_objetivo = random.randint(5, 9)

        # Recoger pedido si estamos en pickup
        for pedido in list(pedidos_activos):
            if [self.x, self.y] == pedido.pickup:
                if self.recoger_pedido(pedido):
                    pedidos_activos.remove(pedido)
                    if self.objetivo_actual == pedido.pickup:
                        self.objetivo_actual = pedido.dropoff

        # Entregar pedido si estamos en dropoff
        entregado = self.entregar_pedido()
        if entregado:

            self.objetivo_actual = None
            self.historial_posiciones.clear()

        # Decide el movimiento
        if self.modo_escape:
            self._mover_aleatorio(mapa, clima_mult, consumo_clima_extra)
        elif self.objetivo_actual:
            self._mover_expectimax(mapa, clima_mult,
                                   consumo_clima_extra, profundidad=2)
        else:
            self._mover_aleatorio(mapa, clima_mult, consumo_clima_extra)

    def _mover_expectimax(self, mapa, clima_mult,
                          consumo_clima_extra, profundidad=2):
        """Selecciona el mejor movimiento usando Expectimax.

        Args:
            mapa (list[list[str]]): Mapa del juego.
            clima_mult (float): Efecto del clima.
            consumo_clima_extra (float): Costo extra.
            profundidad (int): Profundidad de búsqueda.
        """
        direcciones = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        # Arriba, abajo, izquierda, derecha

        mejor_valor = float('-inf')
        mejor_movimiento = None

        for dx, dy in direcciones:
            nx, ny = self.x + dx, self.y + dy

            if not (0 <= nx < len(mapa[0]) and 0 <= ny < len(mapa)):
                continue
            if mapa[ny][nx] == "B":
                continue

            valor = (self._expectimax_valor
                     (mapa, nx, ny, profundidad - 1, es_turno_cpu=False))
            if valor > mejor_valor:
                mejor_valor = valor
                mejor_movimiento = (dx, dy)

        # Ejecutar mejor movimiento encontrado
        if mejor_movimiento:
            dx, dy = mejor_movimiento
            self.mover(dx, dy, mapa, clima_mult, consumo_clima_extra)
        else:
            self._mover_aleatorio(mapa, clima_mult, consumo_clima_extra)

    def _expectimax_valor(self, mapa, x, y, profundidad, es_turno_cpu):
        """Calcula el valor esperado de un estado para Expectimax.

        Args:
            mapa (list[list[str]]): Mapa del juego.
            x (int): Posición X evaluada.
            y (int): Posición Y evaluada.
            profundidad (int): Profundidad restante.
            es_turno_cpu (bool): Si el nodo es MAX o CHANCE.

        Returns:
            float: Valor heurístico estimado.
        """
        if profundidad == 0 or not self.objetivo_actual:
            return -self._distancia_objetivo(x, y)

        if es_turno_cpu:
            # CPU elige el mejor movimiento (MAX node)
            mejor = float('-inf')
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = x + dx, y + dy
                if not (0 <= nx < len(mapa[0]) and 0 <= ny < len(mapa)):
                    continue
                if mapa[ny][nx] == "B":
                    continue
                valor = (self._expectimax_valor
                         (mapa, nx, ny, profundidad - 1, es_turno_cpu=False))
                mejor = max(mejor, valor)
            return mejor
        else:
            # Turno "aleatorio" (CHANCE node):
            # se asume que puede moverse a cualquiera de 4 direcciones
            # con igual probabilidad
            total = 0
            count = 0
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = x + dx, y + dy
                if not (0 <= nx < len(mapa[0]) and 0 <= ny < len(mapa)):
                    continue
                if mapa[ny][nx] == "B":
                    continue
                total += (self._expectimax_valor
                          (mapa, nx, ny, profundidad - 1, es_turno_cpu=True))
                count += 1
            return total / count if count > 0 else\
                -self._distancia_objetivo(x, y)

    def _distancia_objetivo(self, x, y):
        """Calcula la distancia al objetivo actual.

        Args:
            x (int): Posición X.
            y (int): Posición Y.

        Returns:
            int: Distancia al objetivo o 9999 si no existe.
        """
        if not self.objetivo_actual:
            return 9999
        ox, oy = self.objetivo_actual
        return abs(ox - x) + abs(oy - y)

    def _elegir_objetivo_expectimax(self, pedidos_activos):
        """Elige el mejor objetivo considerando prioridad y distancia.

        Args:
            pedidos_activos (list[Pedido]): Pedidos disponibles.
        """
        if self.inventario:
            pedido_prioritario = max(self.inventario, key=lambda p: p.priority)
            self.objetivo_actual = pedido_prioritario.dropoff
            return

        if not pedidos_activos:
            self.objetivo_actual = None
            return

        # Combinar distancia y prioridad
        def valor(p):
            px, py = p.pickup
            dist = abs(px - self.x) + abs(py - self.y)
            return p.priority * 10 - dist  # más prioridad, menos distancia

        mejor_pedido = max(pedidos_activos, key=valor)
        self.objetivo_actual = mejor_pedido.pickup

    # ========================================
    # NIVEL DIFÍCIL - A*
    # ========================================

    def _ia_dificil(self, mapa, pedidos_activos, clima_mult,
                    consumo_clima_extra):
        """IA nivel dificil, usa rutas óptimas mediante A*.

        Args:
            mapa (list[list[str]]): Mapa del juego.
            pedidos_activos (list[Pedido]): Pedidos activos.
            clima_mult (float): Modificador climático.
            consumo_clima_extra (float): Penalización climática.
        """
        ahora = time.time()

        # Guardar posición actual en historial
        self.historial_posiciones.append((self.x, self.y))
        if len(self.historial_posiciones) > self.max_historial:
            self.historial_posiciones.pop(0)

        # Verificar si necesita replanificar ruta
        necesita_replanificar = (
                not self.ruta_planeada or  # No hay ruta
                len(self.ruta_planeada) == 0 or  # Ruta vacía
                ahora - self.ultimo_replan > 10  # Cada 10 segundos
        )

        cambio_clima = abs(clima_mult - self.clima_mult_anterior) > 0.1
        if cambio_clima:
            necesita_replanificar = True

        self.clima_mult_anterior = clima_mult

        # Intentar recoger pedido si estamos en un pickup
        for pedido in list(pedidos_activos):
            if [self.x, self.y] == pedido.pickup:
                if self.recoger_pedido(pedido):
                    pedidos_activos.remove(pedido)
                    necesita_replanificar = True
                    # Replanifica despues de recoger

        # Intentar entregar pedido
        entregado = self.entregar_pedido()
        if entregado:

            necesita_replanificar = True  # Replanificar después de entregar

        # Elegir mejor objetivo y planificar ruta
        if necesita_replanificar:
            self._planificar_estrategia_entregas(
                mapa, pedidos_activos, clima_mult, consumo_clima_extra
            )
            self.ultimo_replan = ahora

        # Ejecutar siguiente paso de la ruta
        if self.ruta_planeada and len(self.ruta_planeada) > 0:
            siguiente_pos = self.ruta_planeada[0]

            # Calcular dirección hacia siguiente posición
            dx = 0 if siguiente_pos[0] == self.x else\
                (1 if siguiente_pos[0] > self.x else -1)
            dy = 0 if siguiente_pos[1] == self.y else\
                (1 if siguiente_pos[1] > self.y else -1)

            # Intentar moverse
            if self.mover(dx, dy, mapa, clima_mult, consumo_clima_extra):
                # Si el movimiento fue exitoso y
                # llegamos a la siguiente posición
                if (self.x, self.y) == siguiente_pos:
                    self.ruta_planeada.pop(0)
            else:
                # Si no puede moverse, replanificar
                self.ruta_planeada = []
        else:
            # Sin ruta, moverse aleatorio
            self._mover_aleatorio(mapa, clima_mult, consumo_clima_extra)

    def _planificar_estrategia_entregas(self, mapa, pedidos_activos,
                                        clima_mult, consumo_clima_extra):
        """Planifica la mejor estrategia para recoger/entregar pedidos.

        Args:
            mapa (list[list[str]]): Mapa.
            pedidos_activos (list[Pedido]): Lista de pedidos.
            clima_mult (float): Velocidad por clima.
            consumo_clima_extra (float): Penalización.
        """
        # Prioridad 1: Entregar pedidos en inventario
        if self.inventario:
            mejor_pedido = max(
                self.inventario,
                key=lambda p: (p.priority * 100 + p.payout)
            )
            destino = tuple(mejor_pedido.dropoff)

            # Calcular ruta con A*
            self.ruta_planeada = self._a_star(
                mapa, (self.x, self.y),
                destino, clima_mult, consumo_clima_extra
            )

            if self.ruta_planeada:
                print(f"CPU va en camino a recoge un pedido pipi:"
                      f" {len(self.ruta_planeada)} pasos")
            return

        # Prioridad 2: Recoger el mejor pedido disponible
        if not pedidos_activos:
            self.ruta_planeada = []
            return

        # Evaluar todos los pedidos con función de valor completa
        mejor_valor = float('-inf')
        mejor_pedido = None
        mejor_ruta = []

        for pedido in pedidos_activos:
            # Verificar capacidad
            if self.peso_total() + pedido.weight > self.capacidad:
                continue

            destino = tuple(pedido.pickup)

            # Calcular ruta con A*
            ruta = self._a_star(
                mapa, (self.x, self.y),
                destino, clima_mult, consumo_clima_extra
            )

            if not ruta:
                continue

            # Calcular valor del pedido
            distancia = len(ruta)

            # Función de valor: payout / (distancia + 1) * factores
            valor = pedido.payout / (distancia + 1)

            # Bonus por prioridad
            if pedido.priority >= 1:
                valor *= 1.5

            # Penalización por clima malo
            if clima_mult < 0.85:
                valor *= 0.8

            # Bonus por resistencia alta (puede tomar pedidos lejanos)
            if self.resistencia > 70:
                valor *= 1.1

            # Penalización si resistencia baja (preferir pedidos cercanos)
            if self.resistencia < 30:
                if distancia > 10:
                    valor *= 0.5

            if valor > mejor_valor:
                mejor_valor = valor
                mejor_pedido = pedido
                mejor_ruta = ruta

        if mejor_pedido and mejor_ruta:
            self.ruta_planeada = mejor_ruta

        else:
            self.ruta_planeada = []

    def _a_star(self, mapa, inicio, destino, clima_mult, consumo_clima_extra):
        """Calcula una ruta óptima usando A*.

        Args:
            mapa (list[list[str]]): Mapa del juego.
            inicio (tuple[int, int]): Posición inicial.
            destino (tuple[int, int]): Meta.
            clima_mult (float): Multiplicador climático.
            consumo_clima_extra (float): Penalización.

        Returns:
            list[tuple[int, int]]: Lista de posiciones representando la ruta.
        """
        from heapq import heappush, heappop

        # Verificar que destino sea válido
        if destino[1] >= len(mapa) or destino[0] >= len(mapa[0]):
            return []
        if mapa[destino[1]][destino[0]] == "B":
            return []

        # Conjuntos y estructuras
        frontera = []
        contador = 0

        g_score = {inicio: 0}

        # f_score: g_score + heurística
        f_score = {inicio: self._heuristica(inicio, destino)}

        vino_de = {}

        # Agregar nodo inicial
        heappush(frontera, (f_score[inicio], contador, inicio))
        contador += 1

        # Nodos ya visitados
        visitados = set()

        # Direcciones
        direcciones = [(0, -1), (0, 1), (-1, 0), (1, 0)]

        while frontera:
            _, _, actual = heappop(frontera)

            if actual == destino:
                return self._reconstruir_camino(vino_de, actual)

            # Skip
            if actual in visitados:
                continue

            visitados.add(actual)

            for dx, dy in direcciones:
                vecino = (actual[0] + dx, actual[1] + dy)

                # Verifica límites
                if not (0 <= vecino[0] < len(mapa[0]) and
                        0 <= vecino[1] < len(mapa)):
                    continue

                # Verificar que no sea edificio
                if mapa[vecino[1]][vecino[0]] == "B":
                    continue

                # Calcular costo del movimiento
                costo_movimiento = self._calcular_costo_arista(
                    mapa, actual, vecino, clima_mult, consumo_clima_extra
                )

                # Calcular g_score tentativo
                tentativo_g = g_score[actual] + costo_movimiento

                # Si encontramos un camino mejor a este vecino
                if vecino not in g_score or tentativo_g < g_score[vecino]:
                    vino_de[vecino] = actual
                    g_score[vecino] = tentativo_g
                    f_score[vecino] = (tentativo_g +
                                       self._heuristica(vecino, destino))

                    heappush(frontera, (f_score[vecino], contador, vecino))
                    contador += 1

        # No se encontró ruta
        return []

    def _calcular_costo_arista(self, mapa, desde, hacia, clima_mult,
                               consumo_clima_extra):
        """Calcula el costo de mover de un nodo a otro.

                Args:
                    mapa (list[list[str]]): Mapa del juego.
                    desde (tuple[int, int]): Nodo origen.
                    hacia (tuple[int, int]): Nodo destino.
                    clima_mult (float): Multiplicador climático.
                    consumo_clima_extra (float): Costo adicional.

                Returns:
                    float: Costo total del movimiento.
                """
        costo = 1.0

        # Factor por tipo de superficie
        tile_destino = mapa[hacia[1]][hacia[0]]
        surface_weights = {
            'C': 1.0,  # Calle
            'P': 0.95,  # Parque (más rápido)
            'B': 999.0  # Edificio (bloqueado)
        }
        surface_weight = surface_weights.get(tile_destino, 1.0)

        # Ajustar costo por superficie (invertir: menor peso = menor costo)
        costo /= surface_weight

        # Ajustar por clima (peor clima = mayor costo)
        costo *= (2.0 - clima_mult)
        # clima_mult=1.0 → costo*1.0, clima_mult=0.75 → costo*1.25

        # Ajustar por consumo extra de resistencia
        costo *= (1.0 + consumo_clima_extra)

        # Penalización si resistencia baja (evitar rutas largas)
        if self.resistencia < 30:
            costo *= 1.5
        elif self.resistencia < 50:
            costo *= 1.2

        return costo

    def _heuristica(self, pos_actual, pos_destino):
        """Heurística Manhattan usada por A*.

        Args:
            pos_actual (tuple[int, int]): Nodo actual.
            pos_destino (tuple[int, int]): Meta.

        Returns:
            int: Distancia heurística.
        """
        return (abs(pos_actual[0] - pos_destino[0])
                + abs(pos_actual[1] - pos_destino[1]))

    def _reconstruir_camino(self, vino_de, actual):
        """Reconstruye la ruta generada por A*.

        Args:
            vino_de (dict): Diccionario de predecesores.
            actual (tuple[int, int]): Nodo final.

        Returns:
            list[tuple[int, int]]: Ruta reconstruida.
        """
        camino = []
        while actual in vino_de:
            camino.append(actual)
            actual = vino_de[actual]

        camino.reverse()
        return camino
