"""
persistencia.py.

Maneja la persistencia del juego para
guardar y cargar datos y también maneja
un registro de los movimientos del jugador
para volver a un estado anterior.
"""

import pickle
import json
import os
import shutil
import time
import pygame
from datetime import datetime


class SistemaPersistencia:
    """Gestiona la persistencia de datos del juego.

    Esta clase se encarga de manejar la creación de carpetas,
    guardado y carga del estado del juego, puntajes, configuración,
    estadísticas y backups. También permite verificar integridad de
    archivos mediante checksums.
    """

    def __init__(self):
        """Inicializa el manejador de persistencia.

        Crea las carpetas necesarias para almacenar archivos de
        guardado, configuraciones, puntajes y estadísticas.

        Attributes:
            carpeta_saves (str): Carpeta donde se guardan los archivos .sav.
            carpeta_data (str): Carpeta para archivos JSON (puntajes, config, etc.).
            archivo_puntajes (str): Ruta al archivo de puntajes.
            archivo_config (str): Ruta al archivo de configuración.
            archivo_estadisticas (str): Ruta al archivo de estadísticas.
        """
        self.carpeta_saves = "saves"
        self.carpeta_data = "data"
        self.archivo_puntajes = "data/puntajes.json"
        self.archivo_config = "data/configuracion.json"
        self.archivo_estadisticas = "data/estadisticas.json"
        self.crear_carpetas()

    def restaurar_backup(self, fecha_backup):
        """Restaura un backup previamente creado.

        Args:
            fecha_backup (str): Fecha del backup en formato "YYYYMMDD_HHMMSS".

        Returns:
            bool: True si se restauró correctamente, False en caso de error.
        """
        carpeta_backup = f"backups/backup_{fecha_backup}"

        if not os.path.exists(carpeta_backup):
            return False

        try:
            # Hacer backup actual antes de restaurar
            self.crear_backup()

            # Restaurar saves
            if os.path.exists(f"{carpeta_backup}/saves"):
                shutil.rmtree(self.carpeta_saves)
                shutil.copytree(f"{carpeta_backup}/saves", self.carpeta_saves)

            # Restaurar datos
            if os.path.exists(f"{carpeta_backup}/data"):
                shutil.rmtree(self.carpeta_data)
                shutil.copytree(f"{carpeta_backup}/data", self.carpeta_data)

            print(f"Backup {fecha_backup} restaurado exitosamente")
            return True

        except Exception as e:
            print(f"Error al restaurar backup: {e}")
            return False

    def crear_carpetas(self):
        """Crea las carpetas si no existen."""
        for carpeta in [self.carpeta_saves, self.carpeta_data]:
            if not os.path.exists(carpeta):
                os.makedirs(carpeta)

    def guardar_juego(self, estado_juego, slot=1):
        """Guarda el estado completo del juego en un archivo .sav.

        Args:
            estado_juego (dict): Diccionario con el estado del juego.
            slot (int, optional): Número de slot donde guardar. Defaults to 1.

        Returns:
            bool: True si se guardó correctamente, False si ocurrió un error.
        """
        archivo = f"{self.carpeta_saves}/slot{slot}.sav"

        try:
            datos_guardado = {
                'timestamp': time.time(),
                'fecha_guardado': datetime.now().isoformat(),
                'version': '1.0',
                'estado_juego': estado_juego
            }

            with open(archivo, 'wb') as f:
                pickle.dump(datos_guardado, f)

            print(f"Juego guardado exitosamente en {archivo}")
            return True

        except Exception as e:
            print(f"Error al guardar juego: {e}")
            return False

    def cargar_juego(self, slot=1):
        """Carga un estado de juego desde un archivo .sav.

        Args:
            slot (int, optional): Slot del guardado a cargar. Defaults to 1.

        Returns:
            dict | None: Estado del juego si existe y es válido,
            None en caso de error o si el archivo no existe.
        """
        archivo = f"{self.carpeta_saves}/slot{slot}.sav"

        if not os.path.exists(archivo):
            print(f"No existe guardado en slot {slot}")
            return None

        try:
            with open(archivo, 'rb') as f:
                datos = pickle.load(f)

            print(f"Juego cargado desde {archivo}")
            print(f"Guardado el: {datos['fecha_guardado']}")
            return datos['estado_juego']

        except Exception as e:
            print(f"Error al cargar juego: {e}")
            return None

    def listar_guardados(self):
        """Obtiene la lista de partidas guardadas disponibles.

           Returns:
               list[dict]: Lista con información de cada guardado encontrado.
                   Cada elemento contiene:
                   - slot (int)
                   - fecha (str)
                   - timestamp (float)
        """
        guardados = []

        for i in range(1, 6):  # Slots 1-5
            archivo = f"{self.carpeta_saves}/slot{i}.sav"
            if os.path.exists(archivo):
                try:
                    with open(archivo, 'rb') as f:
                        datos = pickle.load(f)

                    guardados.append({
                        'slot': i,
                        'fecha': datos['fecha_guardado'],
                        'timestamp': datos['timestamp']
                    })
                except (pickle.UnpicklingError, EOFError, OSError) as e:
                    print(f"Error al leer {archivo}: {e}")
                    continue

        return guardados

    def guardar_puntaje(
            self, nombre_jugador, puntaje_final,
            datos_extra=None):
        """Guarda un puntaje en el archivo JSON de puntajes.

        Args:
            nombre_jugador (str): Nombre del jugador.
            puntaje_final (int): Puntaje obtenido.
            datos_extra (dict, optional): Información adicional. Defaults to None.

        Returns:
            bool: True si se guardó correctamente, False en caso de error.
        """
        nuevo_puntaje = {
            'nombre': nombre_jugador,
            'puntaje': puntaje_final,
            'fecha': datetime.now().isoformat(),
            'timestamp': time.time()
        }

        if datos_extra:
            nuevo_puntaje.update(datos_extra)

        puntajes = self.cargar_puntajes()

        puntajes.append(nuevo_puntaje)

        puntajes.sort(key=lambda x: x['puntaje'], reverse=True)

        puntajes = puntajes[:10]

        try:
            with open(self.archivo_puntajes, 'w', encoding='utf-8') as f:
                json.dump(puntajes, f, indent=2, ensure_ascii=False)

            print(f"Puntaje guardado: {puntaje_final} puntos")
            return True

        except Exception as e:
            print(f"Error al guardar puntaje: {e}")
            return False

    def cargar_puntajes(self):
        """Carga los puntajes almacenados en puntajes.json.

        Returns:
            list[dict]: Lista de puntajes. Puede estar vacía.
        """
        if not os.path.exists(self.archivo_puntajes):
            return []

        try:
            with open(self.archivo_puntajes, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error al cargar puntajes: {e}")
            return []

    def obtener_mejor_puntaje(self):
        """Obtiene el puntaje más alto registrado.

        Returns:
            int: El puntaje máximo registrado o 0 si no hay datos.
        """
        puntajes = self.cargar_puntajes()
        if puntajes:
            return puntajes[0]['puntaje']
        return 0

    def calcular_puntaje_final(self, jugador, tiempo_total,
                               duracion_objetivo, meta_ingresos):
        """Calcula el puntaje final del jugador según parámetros del juego.

        Args:
            jugador (Jugador): Objeto jugador con estadísticas actuales.
            tiempo_total (float): Tiempo final de la partida.
            duracion_objetivo (float): Tiempo máximo objetivo.
            meta_ingresos (int): Meta de ingresos a cumplir.

        Returns:
            dict: Diccionario con:
                - puntaje_final (int)
                - desglose (dict) con base, bonificaciones y penalizaciones
        """
        score_base = jugador.puntaje

        if jugador.reputacion >= 90:
            score_base = int(score_base * 1.05)

        bonus_tiempo = 0
        tiempo_restante_porcentaje =\
            (duracion_objetivo - tiempo_total) / duracion_objetivo
        if tiempo_restante_porcentaje > 0.2:
            bonus_tiempo = int(score_base * 0.1 * tiempo_restante_porcentaje)

        bonus_meta = 0
        if jugador.puntaje >= meta_ingresos:
            bonus_meta = int(meta_ingresos * 0.15)

        penalizaciones = 0

        puntaje_final = score_base + bonus_tiempo + bonus_meta - penalizaciones

        return {
            'puntaje_final': puntaje_final,
            'desglose': {
                'base': score_base,
                'bonus_tiempo': bonus_tiempo,
                'bonus_meta': bonus_meta,
                'penalizaciones': penalizaciones
            }
        }

    def guardar_juego_completo(self, estado_juego, nombre_descripcion="", slot=1):
        """Guarda un estado de juego con metadatos adicionales.

        Incluye un checksum para validar integridad al cargar.

        Args:
            estado_juego (dict): Estado del juego.
            nombre_descripcion (str, optional): Descripción del guardado.
            slot (int, optional): Número del slot. Defaults to 1.

        Returns:
            bool: True si se guardó correctamente, False si falló.
        """
        archivo = f"{self.carpeta_saves}/slot{slot}.sav"

        try:
            datos_guardado = {
                'timestamp': time.time(),
                'fecha_guardado': datetime.now().isoformat(),
                'version': '1.0',
                'descripcion': nombre_descripcion,
                'estado_juego': estado_juego,
                'checksum': self._calcular_checksum(estado_juego)
            }

            with open(archivo, 'wb') as f:
                pickle.dump(datos_guardado, f)

            print(f"Juego guardado exitosamente en {archivo}")
            return True

        except Exception as e:
            print(f"Error al guardar juego: {e}")
            return False

    def _calcular_checksum(self, data):
        """Calcula un checksum simple para verificar integridad.

        Args:
            data (dict | list | any): Datos a validar.

        Returns:
            str: Hash MD5 de 8 caracteres.
        """
        import hashlib
        data_str = str(data).encode('utf-8')
        return hashlib.md5(data_str).hexdigest()[:8]

    def verificar_guardado(self, slot=1):
        """Verifica la integridad de un guardado mediante checksum.

        Args:
            slot (int, optional): Slot del guardado. Defaults to 1.

        Returns:
            bool: True si el guardado es válido, False si está corrupto.
        """
        archivo = f"{self.carpeta_saves}/slot{slot}.sav"

        if not os.path.exists(archivo):
            return False

        try:
            with open(archivo, 'rb') as f:
                datos = pickle.load(f)

            # Verificar checksum
            checksum_calculado = self._calcular_checksum(datos['estado_juego'])
            return datos.get('checksum') == checksum_calculado

        except Exception:
            return False

    def guardar_configuracion(self, config):
        """Guarda ajustes de configuración del juego.

        Args:
            config (dict): Configuración a almacenar.

        Returns:
            bool: True si se guardó correctamente, False si falló.
        """
        try:
            config['ultima_actualizacion'] = datetime.now().isoformat()

            with open(self.archivo_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error al guardar configuración: {e}")
            return False

    def cargar_configuracion(self):
        """Carga la configuración del juego desde archivo.

        Si no existe, crea la configuración por defecto.

        Returns:
            dict: Configuración cargada o generada.
        """
        config_default = {
            'volumen_musica': 0.7,
            'volumen_efectos': 0.8,
            'pantalla_completa': False,
            'resolucion': [800, 600],
            'controles': {
                'arriba': pygame.K_UP,
                'abajo': pygame.K_DOWN,
                'izquierda': pygame.K_LEFT,
                'derecha': pygame.K_RIGHT
            }
        }

        if not os.path.exists(self.archivo_config):
            self.guardar_configuracion(config_default)
            return config_default

        try:
            with open(self.archivo_config, 'r', encoding='utf-8') as f:
                config_cargada = json.load(f)

            # Combinar con valores por defecto para nuevas configuraciones
            config_default.update(config_cargada)
            return config_default

        except Exception as e:
            print(f"Error al cargar configuración: {e}")
            return config_default

    def guardar_estadisticas_jugador(self, estadisticas):
        """Guarda estadísticas detalladas de una partida.

        Args:
            estadisticas (dict): Datos de la partida actual.

        Returns:
            bool: True si se guardó correctamente, False si falló.
        """
        try:
            # Cargar estadísticas existentes
            if os.path.exists(self.archivo_estadisticas):
                with open(self.archivo_estadisticas, 'r', encoding='utf-8') as f:
                    todas_estadisticas = json.load(f)
            else:
                todas_estadisticas = []

            # Agregar nuevas estadísticas
            estadisticas['fecha'] = datetime.now().isoformat()
            estadisticas['timestamp'] = time.time()
            todas_estadisticas.append(estadisticas)

            # Mantener solo las últimas 100 partidas
            if len(todas_estadisticas) > 100:
                todas_estadisticas = todas_estadisticas[-100:]

            with open(self.archivo_estadisticas, 'w', encoding='utf-8') as f:
                json.dump(todas_estadisticas, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"Error al guardar estadísticas: {e}")
            return False

    def obtener_estadisticas_totales(self):
        """Calcula estadísticas agregadas de todas las partidas registradas.

        Returns:
            dict: Estadísticas totales calculadas o {} si no hay datos.
        """
        if not os.path.exists(self.archivo_estadisticas):
            return {}

        try:
            with open(self.archivo_estadisticas, 'r', encoding='utf-8') as f:
                partidas = json.load(f)

            if not partidas:
                return {}

            totales = {
                'total_partidas': len(partidas),
                'partidas_ganadas': sum(1 for p in partidas if p.get('meta_alcanzada', False)),
                'total_entregas': sum(p.get('entregas_completadas', 0) for p in partidas),
                'promedio_puntaje': sum(p.get('puntaje', 0) for p in partidas) / len(partidas),
                'mejor_puntaje': max(p.get('puntaje', 0) for p in partidas),
                'total_dinero_ganado': sum(p.get('dinero_ganado', 0) for p in partidas),
                'promedio_tiempo': sum(p.get('tiempo_total', 0) for p in partidas) / len(partidas)
            }

            return totales

        except Exception as e:
            print(f"Error al calcular estadísticas: {e}")
            return {}

    def crear_backup(self):
        """Crea un backup completo del directorio de datos y saves.

        Returns:
            bool: True si el backup fue creado, False si ocurrió un error.
        """
        import shutil
        from datetime import datetime

        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        carpeta_backup = f"backups/backup_{fecha}"

        try:
            os.makedirs(carpeta_backup, exist_ok=True)

            # Copiar saves
            if os.path.exists(self.carpeta_saves):
                shutil.copytree(self.carpeta_saves, f"{carpeta_backup}/saves")

            # Copiar datos
            if os.path.exists(self.carpeta_data):
                shutil.copytree(self.carpeta_data, f"{carpeta_backup}/data")

            print(f"Backup creado en: {carpeta_backup}")
            return True

        except Exception as e:
            print(f"Error al crear backup: {e}")
            return False



class HistorialMovimientos:
    """Gestiona el historial de estados del jugador para permitir deshacer movimientos.

    Almacena una lista de estados previos limitados por `max_pasos`,
    permitiendo revertir la partida a un estado anterior.
    """

    def __init__(self, max_pasos=50):
        """Inicializa el historial.

        Args:
            max_pasos (int, optional): Número máximo de estados a almacenar.
                Defaults to 50.
        """
        self.historial = []
        self.max_pasos = max_pasos

    def guardar_estado(
            self, jugador, pedidos_activos, tiempo):
        """Guarda el estado actual del jugador y los pedidos activos.

        Args:
            jugador (Jugador): Objeto jugador con sus atributos actuales.
            pedidos_activos (list): Lista de pedidos activos.
            tiempo (float): Tiempo actual del juego.
        """
        estado = {
            'jugador_x': jugador.x,
            'jugador_y': jugador.y,
            'resistencia': jugador.resistencia,
            'puntaje': jugador.puntaje,
            'reputacion': jugador.reputacion,
            'inventario': list(jugador.inventario),
            'pedidos_activos': pedidos_activos.copy(),
            'timestamp': tiempo
        }

        self.historial.append(estado)

        if len(self.historial) > self.max_pasos:
            self.historial.pop(0)

    def deshacer(self, jugador, pedidos_activos):
        """Revierte el juego al estado previo guardado.

        Se requiere al menos 2 estados para poder deshacer.

        Args:
            jugador (Jugador): Instancia del jugador a modificar.
            pedidos_activos (list): Lista de pedidos activos a restaurar.

        Returns:
            bool: True si se revirtió correctamente, False si no hay suficientes estados.
        """
        if len(self.historial) < 2:
            return False

        self.historial.pop()
        estado_anterior = self.historial[-1]

        jugador.x = estado_anterior['jugador_x']
        jugador.y = estado_anterior['jugador_y']
        jugador.resistencia = estado_anterior['resistencia']
        jugador.puntaje = estado_anterior['puntaje']
        jugador.reputacion = estado_anterior['reputacion']
        jugador.inventario = estado_anterior['inventario'].copy()

        pedidos_activos.clear()
        pedidos_activos.extend(estado_anterior['pedidos_activos'])

        print("Movimiento deshecho")
        return True

    def puede_deshacer(self):
        """Indica si existe un estado previo que pueda revertirse.

        Returns:
            bool: True si el historial contiene al menos 2 estados.
        """
        return len(self.historial) >= 2

    def limpiar_historial(self):
        """Elimina todos los estados almacenados en el historial."""
        self.historial.clear()
        print("Historial de movimientos limpiado")