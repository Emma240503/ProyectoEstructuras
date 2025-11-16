"""
clima.py.

Aquí se maneja el sistema de clima del juego
con ayuda de la API, también maneja
los efectos del clima sobre el jugador.
"""

import random
import time
import json


class SistemaClima:
    """Sistema de clima dinámico.

    Está basado en una cadena de Markov
    y datos externos.

    Administra condiciones climáticas,
    las actualiza automáticamente según
    probabilidades configuradas y aplica efectos
    como multiplicadores de velocidad
    e incremento de consumo de resistencia.
    """

    def __init__(self, api_module=None):
        """Inicializa el sistema de clima.

        Carga la configuración desde la API o archivo local y define el estado
        inicial como "clear".

        Args:
            api_module: Módulo de API con un método `obtener_clima()`, o None
                para usar archivo local.
        """
        self.api = api_module

        # Multiplicadores de velocidad para cada clima
        self.multiplicadores = {
            'clear': 1.00,
            'clouds': 0.98,
            'rain_light': 0.90,
            'rain': 0.85,
            'storm': 0.75,
            'fog': 0.88,
            'wind': 0.92,
            'heat': 0.90,
            'cold': 0.92
        }

        # Consumo extra de resistencia por clima
        self.consumo_resistencia = {
            'clear': 0.0,
            'clouds': 0.0,
            'rain_light': 0.05,
            'rain': 0.1,
            'storm': 0.3,
            'fog': 0.0,
            'wind': 0.1,
            'heat': 0.2,
            'cold': 0.05
        }

        # Variables del sistema
        self.estados_disponibles = []
        self.matriz_transicion = {}
        self.estado_actual = 'clear'
        self.intensidad_actual = 0.0
        self.tiempo_cambio = (
                time.time() + random.randint(45, 90))
        # 45-90 segundos

        # Variables de transición suave
        self.en_transicion = False
        self.estado_anterior = 'clear'
        self.multiplicador_anterior = 1.0
        self.tiempo_inicio_transicion = 0
        self.duracion_transicion = 3.0  # 3 segundos de transición

        # Cargar configuración del clima desde API
        self.cargar_configuracion_clima()

    def cargar_configuracion_clima(self):
        """Carga la configuración del clima desde la API o archivo local.

        Si la API falla o el formato es incorrecto, usa una configuración
        predeterminada.

        Raises:
            Exception: Si ocurre un error al
            leer archivo local o procesar datos.
        """
        try:
            if self.api:
                clima_data = self.api.obtener_clima()
            else:
                # Fallback a archivo local
                with open("data/clima.json", "r") as f:
                    clima_data = json.load(f)

            # Extraer datos de la API
            if "data" in clima_data:
                data = clima_data["data"]

                # Estados disponibles
                self.estados_disponibles =\
                    data.get("conditions", list(self.multiplicadores.keys()))

                # Configuración inicial
                initial = data.get(
                    "initial", {"condition": "clear", "intensity": 0.0})
                self.estado_actual = initial.get("condition", "clear")
                self.intensidad_actual = initial.get("intensity", 0.0)

                # Matriz de transición desde la API
                transition_data = data.get("transition", {})
                self.matriz_transicion =\
                    self._procesar_matriz_transicion(transition_data)

                print("Configuración del clima cargada desde API")
                print(f"Estado inicial: {self.estado_actual}")
                print(f"Estados disponibles: {len(self.estados_disponibles)}")

            else:
                print("Formato de API inesperado,"
                      " usando configuración por defecto")
                self._usar_configuracion_por_defecto()

        except Exception as e:
            print(f"Error al cargar clima de API: {e}")
            self._usar_configuracion_por_defecto()

    def _procesar_matriz_transicion(self, transition_data):
        """Convierte la matriz de transición.

         Del formato API al formato interno.

        El formato de entrada esperado es:
            {"clear": {"clouds": 0.3, "rain": 0.1, ...}, ...}

        El formato interno es:
            {"clear": {"estados": [...], "probabilidades": [...]}, ...}

        Args:
            transition_data (dict): Diccionario de transiciones desde la API.

        Returns:
            dict: Matriz de transición procesada y normalizada.
        """
        matriz_procesada = {}

        for estado_origen, transiciones in transition_data.items():
            if estado_origen in self.estados_disponibles:
                # Extraer estados destino y sus probabilidades.
                estados_destino = []
                probabilidades = []

                for estado_destino, prob in transiciones.items():
                    if estado_destino in self.estados_disponibles:
                        estados_destino.append(estado_destino)
                        probabilidades.append(prob)

                # Normalizar probabilidades para asegurar que sumen 1.0.
                suma_prob = sum(probabilidades)
                if suma_prob > 0:
                    probabilidades = [p / suma_prob for p in probabilidades]

                    matriz_procesada[estado_origen] = {
                        'estados': estados_destino,
                        'probabilidades': probabilidades
                    }

        return matriz_procesada

    def _usar_configuracion_por_defecto(self):
        """Carga una configuración interna.

        Opta por esta opción si la API falla.
        """
        self.estados_disponibles =\
            ['clear', 'clouds', 'rain_light', 'rain', 'storm',
             'fog', 'wind', 'heat', 'cold']
        self.estado_actual = 'clear'
        self.intensidad_actual = 0.5

        self.matriz_transicion = {  # Traduce los climas.
            'clear': {'estados': ['clear', 'clouds', 'wind'],
                      'probabilidades': [0.5, 0.3, 0.2]},
            'clouds': {'estados': ['clear', 'clouds', 'rain_light'],
                       'probabilidades': [0.3, 0.4, 0.3]},
            'rain_light': {'estados': ['clouds', 'rain_light', 'rain'],
                           'probabilidades': [0.4, 0.4, 0.2]},
            'rain': {'estados': ['clouds', 'rain', 'storm'],
                     'probabilidades': [0.4, 0.4, 0.2]},
            'storm': {'estados': ['rain', 'clouds', 'storm'],
                      'probabilidades': [0.5, 0.3, 0.2]},
            'fog': {'estados': ['fog', 'clouds', 'clear'],
                    'probabilidades': [0.5, 0.3, 0.2]},
            'wind': {'estados': ['wind', 'clouds', 'clear'],
                     'probabilidades': [0.5, 0.3, 0.2]},
            'heat': {'estados': ['heat', 'clear', 'clouds'],
                     'probabilidades': [0.5, 0.3, 0.2]},
            'cold': {'estados': ['cold', 'clear', 'clouds'],
                     'probabilidades': [0.5, 0.3, 0.2]}
        }

        print("Usando configuración de clima por defecto")

    def obtener_multiplicador_actual(self):
        """Calcula el multiplicador de velocidad según el clima actual.

        Aplica interpolación lineal si hay una transición activa.

        Returns:
            float: Multiplicador de velocidad (entre ~0.75 y 1.00).
        """
        if not self.en_transicion:
            base_mult = self.multiplicadores.get(self.estado_actual, 1.0)
            # Aplicar intensidad: a mayor intensidad, mayor efecto.
            return base_mult * (
                    1.0 - 0.5 * self.intensidad_actual * (1.0 - base_mult))

        # Durante transición, interpolar entre estados.
        tiempo_transcurrido = time.time() - self.tiempo_inicio_transicion
        progreso = min(1.0, tiempo_transcurrido / self.duracion_transicion)

        mult_anterior = self.multiplicadores.get(self.estado_anterior, 1.0)
        mult_nuevo = self.multiplicadores.get(self.estado_actual, 1.0)
        mult_nuevo *= (1.0 - 0.5 * self.intensidad_actual * (1.0 - mult_nuevo))

        # Interpolación linear.
        multiplicador = mult_anterior + (mult_nuevo - mult_anterior) * progreso

        # Finalizar transición.
        if progreso >= 1.0:
            self.en_transicion = False

        return multiplicador

    def obtener_consumo_resistencia_extra(self):
        """Calcula el consumo extra de resistencia debido al clima.

        Si hay una transición activa, interpola entre ambos estados.

        Returns:
            float: Consumo adicional de resistencia (0.0 a ~0.3+).
        """
        consumo_base = self.consumo_resistencia.get(self.estado_actual, 0.0)

        if not self.en_transicion:
            return consumo_base * (1.0 + self.intensidad_actual)

        # Durante transición, interpolar.
        tiempo_transcurrido = time.time() - self.tiempo_inicio_transicion
        progreso = min(1.0, tiempo_transcurrido / self.duracion_transicion)

        consumo_anterior = self.consumo_resistencia.get(
            self.estado_anterior, 0.0)
        consumo_nuevo = consumo_base * (1.0 + self.intensidad_actual)

        return consumo_anterior + (consumo_nuevo - consumo_anterior) * progreso

    def actualizar(self):
        """Actualiza el estado del clima.

        Lo actualiza según el tiempo y la cadena de Markov.
        """
        ahora = time.time()

        # Verificar si es hora de cambiar el clima.
        if ahora >= self.tiempo_cambio:
            self._cambiar_clima()

    def _cambiar_clima(self):
        """Cambia el clima usando la matriz de Markov cargada.

        Selecciona un nuevo estado basándose en probabilidades
        y genera una nueva intensidad entre 0.2 y 1.0.
        Inicia una transición suave.
        """
        if self.estado_actual not in self.matriz_transicion:
            print(f"Estado {self.estado_actual} no encontrado en matriz,"
                  f" usando aleatorio")
            nuevo_estado = random.choice(self.estados_disponibles)
        else:
            transicion = self.matriz_transicion[self.estado_actual]
            estados = transicion['estados']
            probabilidades = transicion['probabilidades']

            # Seleccionar siguiente estado basado en probabilidades.
            nuevo_estado = random.choices(estados, weights=probabilidades)[0]

        # Generar nueva intensidad (0.0 a 1.0).
        nueva_intensidad = random.uniform(0.2, 1.0)

        # Iniciar transición suave.
        self.estado_anterior = self.estado_actual
        self.estado_actual = nuevo_estado
        self.intensidad_actual = nueva_intensidad

        self.en_transicion = True
        self.tiempo_inicio_transicion = time.time()

        # Programar próximo cambio (45-90 segundos según especificación).
        self.tiempo_cambio = time.time() + random.randint(45, 90)

        print(f"Clima: {self.estado_anterior} → {self.estado_actual}"
              f" (intensidad: {self.intensidad_actual:.2f})")

    def obtener_info_clima(self):
        """Retorna información útil del clima para mostrar en pantalla.

        Returns:
            dict: Información con estado, intensidad, multiplicador, consumo,
                si está en transición y tiempo restante.
        """
        return {
            'estado': self.estado_actual,
            'intensidad': self.intensidad_actual,
            'multiplicador': self.obtener_multiplicador_actual(),
            'en_transicion': self.en_transicion,
            'tiempo_hasta_cambio': max(0, self.tiempo_cambio - time.time()),
            'consumo_extra': self.obtener_consumo_resistencia_extra()
        }

    def traducir_clima(self, estado):
        """Traduce un estado climático al texto visible para el jugador.

        Args:
            estado (str): Clave del estado climático (e.g., "rain", "fog").

        Returns:
            str: Nombre traducido al español.
        """
        traducciones = {
            'clear': 'Despejado ',
            'clouds': 'Nublado ',
            'rain_light': 'Llovizna ',
            'rain': 'Lluvia ',
            'storm': 'Tormenta ',
            'fog': 'Niebla ',
            'wind': 'Viento ',
            'heat': 'Calor ',
            'cold': 'Frío '
        }
        return traducciones.get(estado, f"{estado} ")

    def obtener_efecto_descripcion(self):
        """Genera una descripción cualitativa de las condiciones climáticas.

        Returns:
            str: Texto indicando la severidad del clima
                ("Condiciones ideales", "Condiciones extremas", etc.).
        """
        mult = self.obtener_multiplicador_actual()
        consumo = self.obtener_consumo_resistencia_extra()

        if mult >= 0.95 and consumo <= 0.05:
            return "Condiciones ideales"
        elif mult >= 0.85:
            return "Condiciones buenas"
        elif mult >= 0.75:
            return "Condiciones difíciles"
        else:
            return "Condiciones extremas"

    def debug_info(self):
        """Retorna información interna útil para depuración.

        Returns:
            dict: Datos estructurados sobre estados, transiciones y conexión.
        """
        return {
            'estados_disponibles': self.estados_disponibles,
            'matriz_size': len(self.matriz_transicion),
            'estado_actual': self.estado_actual,
            'transiciones_disponibles':
                list(self.matriz_transicion.get(self.estado_actual, {})
                     .get('estados', [])),
            'api_conectada': self.api is not None
        }
