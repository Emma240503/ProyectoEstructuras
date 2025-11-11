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
        """Construye el jugador CPU.

        Args:
            x (int): Posición inicial X
            y (int): Posición inicial Y
            dificultad (str): 'facil', 'media' o 'dificil'
            capacidad (int): Capacidad máxima de carga
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

        print(f"CPU creado en ({x}, {y}) con dificultad: {dificultad}")

    def actualizar(self, mapa, pedidos_activos, clima_mult, consumo_clima_extra):
        """Actualiza el estado del CPU según su dificultad.

        Args:
            mapa: Matriz del mapa del juego
            pedidos_activos: Lista de pedidos disponibles
            clima_mult: Multiplicador de velocidad por clima
            consumo_clima_extra: Consumo extra de resistencia por clima
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

        # Ejecutar IA según dificultad
        if self.dificultad == 'facil':
            self._ia_facil(mapa, pedidos_activos, clima_mult, consumo_clima_extra)
        elif self.dificultad == 'media':
            self._ia_media(mapa, pedidos_activos, clima_mult, consumo_clima_extra)
        elif self.dificultad == 'dificil':
            self._ia_dificil(mapa, pedidos_activos, clima_mult, consumo_clima_extra)

    # ========================================
    # NIVEL FÁCIL - MOVIMIENTO ALEATORIO
    # ========================================

    def _ia_facil(self, mapa, pedidos_activos, clima_mult, consumo_clima_extra):
        """IA nivel fácil: Movimiento hacia objetivos con aleatoriedad.

        Características:
        - Elige un pedido al azar como objetivo
        - Se mueve hacia el objetivo con 70% probabilidad, aleatorio 30%
        - Cambia de objetivo cada 3-6 segundos
        - Detecta bucles y activa modo escape
        """
        ahora = time.time()

        # Guardar posición actual en historial
        self.historial_posiciones.append((self.x, self.y))
        if len(self.historial_posiciones) > self.max_historial:
            self.historial_posiciones.pop(0)

        # Detectar si está en un bucle
        if not self.modo_escape and len(self.historial_posiciones) >= 6:
            # Contar cuántas veces aparece la posición actual en el historial reciente
            posicion_actual = (self.x, self.y)
            repeticiones = self.historial_posiciones[-6:].count(posicion_actual)

            # Si ha estado en la misma posición 3+ veces en las últimas 6 posiciones
            if repeticiones >= 3:
                print(f"⚠️ CPU detectó bucle en ({self.x}, {self.y}) - Activando modo escape")
                self.modo_escape = True
                self.tiempo_escape = ahora
                self.objetivo_actual = None  # Cambiar de objetivo

        # Desactivar modo escape después del tiempo
        if self.modo_escape and (ahora - self.tiempo_escape > self.duracion_escape):
            print(f"✅ CPU salió del modo escape")
            self.modo_escape = False
            self.historial_posiciones.clear()  # Limpiar historial

        # Verificar si hay que cambiar de objetivo
        if (self.objetivo_actual is None or
                ahora - self.ultimo_cambio_objetivo > self.tiempo_cambio_objetivo):
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
                    print(f"CPU recogió pedido!")

        # Intentar entregar pedido
        entregado = self.entregar_pedido()
        if entregado:
            print(f"CPU entregó pedido! ${self.puntaje}")
            # Cambiar objetivo después de entregar
            self.objetivo_actual = None
            self.historial_posiciones.clear()  # Limpiar historial

        # Decidir movimiento según modo
        if self.modo_escape:
            # En modo escape: 100% aleatorio para salir del bucle
            self._mover_aleatorio(mapa, clima_mult, consumo_clima_extra)
        elif self.objetivo_actual:
            # Modo normal: 70% hacia objetivo, 30% aleatorio
            if random.random() < 0.7:
                self._mover_hacia_objetivo(mapa, clima_mult, consumo_clima_extra)
            else:
                self._mover_aleatorio(mapa, clima_mult, consumo_clima_extra)
        else:
            # Si no hay objetivo, moverse aleatorio
            self._mover_aleatorio(mapa, clima_mult, consumo_clima_extra)

    def _elegir_objetivo_aleatorio(self, pedidos_activos):
        """Elige un pedido aleatorio como objetivo.

        Args:
            pedidos_activos: Lista de pedidos disponibles
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
        """Mueve al CPU hacia su objetivo actual.

        Args:
            mapa: Matriz del mapa
            clima_mult: Multiplicador de velocidad por clima
            consumo_clima_extra: Consumo extra de resistencia
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
            if (0 <= nx < len(mapa[0]) and 0 <= ny < len(mapa) and mapa[ny][nx] != "B"):
                # Verificar que no sea una posición reciente (evitar bucles)
                if (nx, ny) not in self.historial_posiciones[-4:]:
                    if self.mover(dx, dy, mapa, clima_mult, consumo_clima_extra):
                        return  # Movimiento exitoso

        # Si todos los intentos fallaron, moverse aleatorio
        self._mover_aleatorio(mapa, clima_mult, consumo_clima_extra)

    def _mover_aleatorio(self, mapa, clima_mult, consumo_clima_extra):
        """Mueve al CPU en una dirección aleatoria válida.

        Args:
            mapa: Matriz del mapa
            clima_mult: Multiplicador de velocidad por clima
            consumo_clima_extra: Consumo extra de resistencia
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
    # NIVEL MEDIO - GREEDY/EXPECTIMAX (TODO)
    # ========================================

    def _ia_media(self, mapa, pedidos_activos, clima_mult, consumo_clima_extra):
        """IA nivel medio: Evaluación con heurísticas.

        TODO: Implementar Greedy o Expectimax
        - Anticipar 2-3 movimientos
        - Evaluar con función de puntuación
        - Seleccionar mejor movimiento
        """
        # Por ahora, usar IA fácil
        print("IA Media aún no implementada, usando IA fácil")
        self._ia_facil(mapa, pedidos_activos, clima_mult, consumo_clima_extra)

    # ========================================
    # NIVEL DIFÍCIL - A*/DIJKSTRA (TODO)
    # ========================================

    def _ia_dificil(self, mapa, pedidos_activos, clima_mult, consumo_clima_extra):
        """IA nivel difícil: Rutas óptimas con grafos.

        TODO: Implementar A* o Dijkstra
        - Representar mapa como grafo
        - Calcular rutas óptimas
        - Optimizar secuencia de entregas
        """
        # Por ahora, usar IA fácil
        print("IA Difícil aún no implementada, usando IA fácil")
        self._ia_facil(mapa, pedidos_activos, clima_mult, consumo_clima_extra)