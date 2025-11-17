---Proyecto de Estructuras de Datos---
-
Juego: Courier Quest - Parte 1 y 2

Integrantes: 

- Justin Briones Sequeira

- Emmanuel Rodriguez Picado

- Josué Vargas Gutiérrez

-Instrucciones de uso-
-
Al ejecutar el código en el Main.py aparecerá un menú principal
donde se puede seleccionar la dificultad de la IA:

- Presionar "0" para jugar sin IA (solo jugador)
- Presionar "1" para IA Fácil (movimiento aleatorio)
- Presionar "2" para IA Media (Expectimax)
- Presionar "3" para IA Difícil (A* con estrategia)

Una vez seleccionada la dificultad, el juego comenzará directamente,
cargando imágenes, la ventana y la información obtenida de la API.

El personaje es capaz de moverse utilizando las teclas 
de dirección del teclado, también cuenta con otras acciones
que se mostrarán en la parte de abajo a la derecha de la 
pantalla junto con su respectiva tecla para accionar:

- Flechas: Movimiento
- Q: Cancelar último pedido
- U: Deshacer movimiento
- I: Mostrar/ocultar inventario detallado
- T: Mostrar/ocultar estadísticas
- O: Ordenar inventario por dinero
- P: Pausar juego
- Ctrl+S: Guardar partida manualmente
- Ctrl+L: Cargar partida guardada

Para recoger pedidos y entregarlos el jugador debe
posicionarse en la casilla con la imagen del paquete o
del punto de entrega.

El juego terminará cuando se llegue a la cantidad de dinero
indicada en la meta (victoria), cuando el CPU alcance la meta
primero (derrota), cuando se acabe el tiempo (derrota) 
o cuando la reputación baje del 20% (derrota).

El juego se guarda automáticamente cada 2 minutos, incluyendo
el estado del jugador, del CPU, pedidos y clima.

-Estructuras de datos utilizadas - PARTE 1-
-
Se hizo uso de heapq para hacer manejo de los pedidos
que el jugador se encarga de recoger y que estos se vayan
ordenando por orden de prioridad. 
Al recoger los pedidos estos son guardados con ayuda de
colas (deque) y el método sorted(), también se agregó
una segunda opción para que se ordenaran los pedidos por
dinero haciendo uso del "Insertion sort".

Por otro lado se usaron listas [] como "pedidos_activos" que son pedidos
que estan en el mapa y pueden recogerse, "jugador.inventario", que es la cantidad 
de espacio que tiene el jugador en la mochila. Por otro lado se usaron set( ), que
sirven para evitar duplicados dentro del juego, es decir que todos los pedidos seran
diferentes siempre, en este caso estan: pedidos_vistos=set( ), que su funcion es ver si
un pedido ya fue extraido de la API para asi no volver a llamar el mismo pedido y llamar a 
otro diferente. Asi mismo, esta ocupadas = set( ) que sirve para verificar si un pedido
esta en (x, y) posicion y asi mandarlo para otra casilla. Se utilizo set ( ) ya que
es muy eficente para verificar si un elemento existe O(1). Ademas a la hora de agregar 
elementos en set ( ) solo acepta elementos que no se pueden cambiar, por eso se usan tuples
para poder agregar a los set y es la manera mas efeciente O(1):
ocupadas.add(tuple(ped.pickup))
ocupadas.add(tuple(ped.dropoff)) 
En este caso las tuples se usan nada mas para guardar las coordenadas.

Para el manejo de pedidos con el heapq obtenemos una
complejidad de O(n log n) sin importar el orden en el
que aparezcan los pedidos con diferentes prioridades.

Para el ordenamiento "Insertion sort" al ordenar los
pedidos con ayuda de una cola estos reciben una complejidad
de O(n) en el mejor de los casos, es decir si los pedidos
se van recogiendo en un orden en el que no haya necesidad de
ordenarlos no se hacen intercambios y solo habrán 
comparaciones, sin embargo en el caso promedio y en el
peor de los casos (desordenados según dinero), habrá una
complejidad de O(n^2).

-Estructuras de datos utilizadas - PARTE 2 (IA)-
-

---IA NIVEL FÁCIL---

Para la IA fácil se utilizó movimiento aleatorio con un sistema
anti-bucles para evitar que el CPU se quede atrapado.

Estructuras utilizadas:

- Lista: historial_posiciones (últimas 10 posiciones del CPU)
  - Se usa para detectar si el CPU está en un bucle
  - Complejidad: O(1) para agregar, O(n) para contar repeticiones
  
El algoritmo funciona así:
- Si el CPU repite la misma posición 3 o más veces en las últimas
  6 posiciones, entra en "modo escape" por 2 segundos
- Durante el modo escape, solo se mueve aleatoriamente
- Fuera del modo escape: 70% se mueve hacia el objetivo, 30% aleatorio

Código ejemplo:
if len(self.historial_posiciones) >= 6:
    repeticiones = self.historial_posiciones[-6:].count(posicion_actual)
    if repeticiones >= 3:
        self.modo_escape = True

Complejidad: O(1) en promedio para cada movimiento

---IA NIVEL MEDIO (Expectimax)---

Para la IA media se implementó el algoritmo Expectimax que evalúa
movimientos futuros considerando incertidumbre.

Estructuras utilizadas:

- Árboles de decisión con profundidad 2-3 niveles
  - Nodos MAX: cuando es turno del CPU (elige el mejor movimiento)
  - Nodos CHANCE: modelan la incertidumbre (sacan promedio)

Complejidad: O(b^d) donde:
- b = factor de ramificación (4 direcciones posibles)
- d = profundidad de búsqueda (2-3)
- Total: O(4^2) = O(16) o O(4^3) = O(64) evaluaciones por movimiento

El algoritmo evalúa cada movimiento con una función heurística:

valor = (prioridad_pedido * 10) - distancia_manhattan

Esto hace que el CPU prefiera:
- Pedidos de alta prioridad
- Pedidos cercanos
- Maximizar ganancia vs distancia

Código del algoritmo:
def _expectimax_valor(self, mapa, x, y, profundidad, es_turno_cpu):
    if es_turno_cpu:
        # Nodo MAX: elegir mejor movimiento
        return max(valores_vecinos)
    else:
        # Nodo CHANCE: promedio de posibilidades
        return sum(valores_vecinos) / count

---IA NIVEL DIFÍCIL (A* con estrategia)---

Para la IA difícil se implementó el algoritmo A* (A-Star) para encontrar
rutas óptimas y una estrategia compleja para elegir pedidos.

Estructuras utilizadas:

1. Heap (heapq): Cola de prioridad "frontera"
   - Almacena nodos a explorar ordenados por f(n) = g(n) + h(n)
   - Complejidad: O(log n) por inserción/extracción

2. Diccionarios:
   - g_score: costo real desde inicio hasta cada nodo - O(1) acceso
   - f_score: g_score + heurística - O(1) acceso
   - vino_de: para reconstruir el camino - O(1) acceso

3. Set: visitados
   - Evita explorar el mismo nodo dos veces - O(1) verificación

Complejidad total de A*: O(E log V) donde:
- E = número de aristas (aproximadamente 4 por casilla)
- V = número de vértices/casillas en el mapa
- Para un mapa de 20x15: O(300 log 300) ≈ O(750) operaciones

Heurística utilizada (Manhattan):
h(n) = |x_actual - x_destino| + |y_actual - y_destino|

Esta heurística es admisible (nunca sobreestima el costo real)
lo que garantiza que A* encuentra el camino óptimo.

Función de costo de arista (considera múltiples factores):

costo = 1.0
costo /= surface_weight           # Parque = más rápido (0.95)
costo *= (2.0 - clima_mult)       # Lluvia = más lento
costo *= (1.0 + consumo_extra)    # Tormenta = mayor costo
if resistencia < 30:
    costo *= 1.5                  # Evita rutas largas si está cansado

Estrategia de selección de pedidos:

El CPU evalúa TODOS los pedidos disponibles y calcula un "valor"
para cada uno:

valor = pago_pedido / (distancia + 1)

Y aplica modificadores:
- Si prioridad >= 1: valor *= 1.5 (bonus)
- Si clima malo (mult < 0.85): valor *= 0.8 (penalización)
- Si resistencia > 70: valor *= 1.1 (puede ir lejos)
- Si resistencia < 30 y distancia > 10: valor *= 0.5 (evita lejanos)

El pedido con mayor valor es seleccionado, y A* calcula
la ruta óptima hacia él.

Replanificación:
- Cada 10 segundos
- Al recoger o entregar un pedido
- Si el clima cambia más del 10%

Código del algoritmo A*:
def _a_star(self, mapa, inicio, destino):
    frontera = []  # Heap
    heappush(frontera, (f_score[inicio], contador, inicio))
    
    while frontera:
        _, _, actual = heappop(frontera)
        
        if actual == destino:
            return self._reconstruir_camino(vino_de, actual)
        
        for vecino in vecinos_validos(actual):
            costo = calcular_costo_arista(actual, vecino)
            tentativo_g = g_score[actual] + costo
            
            if tentativo_g < g_score[vecino]:
                g_score[vecino] = tentativo_g
                f_score[vecino] = tentativo_g + heuristica(vecino, destino)
                heappush(frontera, (f_score[vecino], contador, vecino))

-Resumen de complejidades-
-

Estructura/Algoritmo          | Operación         | Complejidad
------------------------------|-------------------|-------------
Heap (ColaPedidos)            | Insert/Extract    | O(log n)
Deque (Inventario)            | Append/Pop        | O(1)
Set (pedidos_vistos)          | Search/Insert     | O(1)
Insertion Sort                | Ordenar           | O(n²)
IA Fácil (Random)             | Movimiento        | O(1)
IA Media (Expectimax)         | Evaluación árbol  | O(b^d)
IA Difícil (A*)               | Búsqueda camino   | O(E log V)
BFS (reubicación pedidos)     | Buscar cercano    | O(V + E)

-Archivos del proyecto-
-

Main.py          - Bucle principal del juego
jugador.py       - Clase Jugador (humano)
jugador_cpu.py   - Clase JugadorCPU con 3 niveles de IA
clases.py        - Pedido y ColaPedidos (heap)
mapa.py          - Carga y dibujo del mapa
clima.py         - Sistema climático (cadena de Markov)
pedidos.py       - Generación y reubicación de pedidos
persistencia.py  - Guardado/carga y puntajes
menu.py          - Menús principal y de pausa
api.py           - Conexión con API y modo offline

data/
  ciudad.json    - Mapa local
  pedidos.json   - Pedidos locales
  clima.json     - Configuración del clima
  puntajes.json  - Tabla de mejores puntajes

saves/           - Archivos de guardado (.sav)
assets/          - Imágenes del juego

-Diferencias entre niveles de IA-
-

FÁCIL:
- Elige pedidos al azar
- Se mueve mayormente aleatorio (30% random, 70% hacia objetivo)
- Tiene sistema anti-bucles
- No planifica rutas, solo direcciones generales
- Competitivo para jugadores nuevos

MEDIA:
- Evalúa 2-3 movimientos por adelantado
- Usa función heurística para elegir mejor pedido
- Considera prioridad y distancia
- Más estratégico pero no perfecto
- Desafío medio

DIFÍCIL:
- Calcula rutas óptimas con A*
- Evalúa TODOS los pedidos disponibles
- Considera clima, resistencia, superficie
- Replanifica dinámicamente
- Muy difícil de vencer

-Conceptos de estructuras de datos aplicados-
-

✓ Grafos ponderados (el mapa se trata como grafo)
✓ Árboles de decisión (Expectimax)
✓ Colas de prioridad (Heap en A* y ColaPedidos)
✓ Heurísticas (Manhattan para A*)
✓ Algoritmos de búsqueda (A*, BFS, Expectimax)
✓ Cadenas de Markov (sistema de clima)
✓ Ordenamiento (Insertion Sort)
✓ Estructuras lineales (listas, colas, pilas)
✓ Estructuras no lineales (árboles, grafos)

-Notas adicionales-
-

El auto-guardado se ejecuta cada 2 minutos e incluye el estado
completo del juego: posición del jugador, posición del CPU,
inventarios de ambos, pedidos activos, estado del clima y tiempo.

La detección de bucles en IA fácil revisa las últimas 10 posiciones
y si detecta que el CPU está en la misma casilla 3 o más veces
en los últimos 6 movimientos, activa el modo escape por 2 segundos
donde solo se mueve random.

La IA difícil replanifica su ruta cada 10 segundos, cada vez que
recoge o entrega un pedido, y cuando el clima cambia más del 10%
en su multiplicador de velocidad.

Todos los algoritmos de IA consideran el peso en el inventario,
la resistencia actual, el clima y el tipo de superficie para
tomar decisiones.
