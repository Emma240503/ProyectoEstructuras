"""
mapa.py.

Se encarga de cargar el mapa directamente
de la API, y dibujarlo en la pantalla.
"""

import pygame


def cargar_mapa(api):
    """Carga el mapa desde la API y devuelve la matriz de tiles.

    Args:
        api: Objeto que expone el método `obtener_mapa()`, el cual
            debe retornar un diccionario con la estructura.

    Returns:
        list[list[str]]: Matriz de tiles que representa el mapa
        completo de la ciudad.
    """
    ciudad_data = api.obtener_mapa()["data"]
    return ciudad_data["tiles"]


def dibujar_mapa(screen, tiles, colors, cam_x,
                 cam_y, tile_size, view_width,
                 view_height, imagenes=None):
    """Dibuja en pantalla la región visible del mapa.

    Recorre el área determinada por la cámara (cam_x, cam_y) y dibuja
    cada tile usando su color o su imagen correspondiente.

    Args:
        screen (pygame.Surface): Superficie donde se dibuja el mapa.
        tiles (list[list[str]]): Matriz que contiene los tipos de tile.
        colors (dict): Diccionario que asigna colores a cada tipo de tile.
        cam_x (int): Posición X de la cámara (tile inicial visible).
        cam_y (int): Posición Y de la cámara (tile inicial visible).
        tile_size (int): Tamaño en píxeles de cada tile.
        view_width (int): Cantidad de tiles visibles en el eje X.
        view_height (int): Cantidad de tiles visibles en el eje Y.
        imagenes (dict | None): Opcional. Diccionario que asigna
            imágenes (pygame.Surface) a tipos de tile.
    """
    for y in range(cam_y, cam_y + view_height):
        for x in range(cam_x, cam_x + view_width):
            tile = tiles[y][x]

            screen_x = (x - cam_x) * tile_size
            screen_y = (y - cam_y) * tile_size

            if imagenes and tile in imagenes:
                screen.blit(imagenes[tile], (screen_x, screen_y))
            else:
                pygame.draw.rect(
                    screen, colors.get(tile, (255, 0, 0)),
                    (screen_x, screen_y, tile_size, tile_size))
