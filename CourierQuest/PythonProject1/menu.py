"""
menu.py.

Sistema de menú principal y pausa del juego.
"""

import pygame


class Menu:
    """Maneja el menú principal y selección de dificultad."""

    def __init__(self, screen):
        """Construye el menú principal.

        Args:
            screen (pygame.Surface): Superficie donde se dibuja el menú.
        """
        self.screen = screen
        self.font_titulo = pygame.font.SysFont(None, 72)
        self.font_opcion = pygame.font.SysFont(None, 48)
        self.font_info = pygame.font.SysFont(None, 32)

        # Opciones del menú
        self.opciones = [
            "1. IA Fácil",
            "2. IA Media",
            "3. IA Difícil",
            "0. Sin IA (Solo Jugador)"
        ]

        self.dificultad_seleccionada = None

    def mostrar(self):
        """Muestra el menú y retorna la dificultad seleccionada."""
        self.screen.fill((30, 30, 30))  # Fondo oscuro

        # Título
        titulo = self.font_titulo.render("COURIER QUEST", True, (255, 215, 0))
        titulo_rect = (titulo.get_rect
                       (center=(self.screen.get_width() // 2, 100)))
        self.screen.blit(titulo, titulo_rect)

        # Subtítulo
        subtitulo = self.font_info.render("Seleccione dificultad:",
                                          True, (255, 255, 255))
        subtitulo_rect = subtitulo.get_rect(center=(self.screen.get_width()
                                                    // 2, 180))
        self.screen.blit(subtitulo, subtitulo_rect)

        # Opciones
        y_offset = 250
        for i, opcion in enumerate(self.opciones):
            color = (100, 255, 100) if i < 3 else (255, 255, 255)
            texto = self.font_opcion.render(opcion, True, color)
            texto_rect = (
                texto.get_rect(center=(self.screen.get_width()
                                       // 2, y_offset + i * 60)))
            self.screen.blit(texto, texto_rect)

        # Instrucciones
        instruccion = (self.font_info.render
                       ("Presione el número correspondiente",
                        True, (200, 200, 200)))
        instruccion_rect = (instruccion.get_rect
                            (center=(self.screen.get_width() // 2, 550)))
        self.screen.blit(instruccion, instruccion_rect)

        pygame.display.flip()

    def procesar_input(self, event):
        """Procesa la entrada del usuario.

        Además determina la dificultad seleccionada.

        Args:
            event (pygame.event.Event): Evento detectado por pygame.

        Returns:
            str | None: Cadena con la dificultad seleccionada
            ('facil', 'media', 'dificil', 'sin_ia'),
            o None si no se seleccionó nada.
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                return 'facil'
            elif event.key == pygame.K_2:
                return 'media'
            elif event.key == pygame.K_3:
                return 'dificil'
            elif event.key == pygame.K_0:
                return 'sin_ia'
        return None


class MenuPausa:
    """Representa el menú de pausa.

    Se muestra durante el juego.
    """

    def __init__(self, screen):
        """Inicializa el menú de pausa.

        Args:
            screen (pygame.Surface):
            Superficie donde se dibuja el menú de pausa.
        """
        self.screen = screen
        self.font = pygame.font.SysFont(None, 64)
        self.font_small = pygame.font.SysFont(None, 36)

    def mostrar(self):
        """Dibuja el menú de pausa sobre el juego."""
        # Overlay semi-transparente
        overlay = (pygame.Surface
                   ((self.screen.get_width(),
                     self.screen.get_height())))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Texto PAUSA
        texto = self.font.render("PAUSA", True, (255, 255, 0))
        texto_rect = texto.get_rect(center=(self.screen.get_width() // 2, 250))
        self.screen.blit(texto, texto_rect)

        # Instrucciones
        instrucciones = [
            "P - Continuar",
            "ESC - Salir al menú"
        ]

        y_offset = 350
        for i, inst in enumerate(instrucciones):
            rendered = self.font_small.render(inst, True, (255, 255, 255))
            rendered_rect = (rendered.get_rect
                             (center=(self.screen.get_width()
                                      // 2, y_offset + i * 50)))
            self.screen.blit(rendered, rendered_rect)

        pygame.display.flip()
