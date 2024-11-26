from numba import jit
import pygame
import numpy as np


from win32con import ENUM_CURRENT_SETTINGS
from win32api import EnumDisplaySettings


class Engine:

    # units_scale = 10**10

    win_aspect_ratio = 16/10
    window_height = 720
    wh = window_height
    window_width = window_height * win_aspect_ratio
    window_size = (window_width, window_height)

    # font1 = pygame.font.SysFont(None, 20)

    UI_COLORS = [
        (255, 255, 255),  # Blanco (alto)
        (255, 165, 0),    # Naranja (intermedio-alto)
        (255, 0, 0),    # Rojo (intermedio)
        (128, 0, 32),   # Bordó (intermedio-bajo)
        (0, 0, 0),      # Negro (bajo)
    ]

    def set_up():

        dev_mode = EnumDisplaySettings(None, ENUM_CURRENT_SETTINGS)  # get the OS's fps setting
        Engine.fps = dev_mode.DisplayFrequency
        Engine.timer = pygame.time.Clock()

        Engine.screen = pygame.display.set_mode(Engine.window_size)

        # Engine.alpha_surface = pygame.Surface((Engine.window_width, Engine.window_height), pygame.SRCALPHA)  # SRCALPHA permite usar alpha

        pygame.display.set_caption("Ventana Básica de Pygame")

        Engine.font1 = pygame.font.SysFont("Times New Roman", Engine.wh//34)

    def calcular_color(valor, minimo, maximo):
        # Definir los colores por los que quieres que pase la interpolación
        colores = [
            (0, 0, 0),      # Negro (bajo)
            (128, 0, 32),   # Bordó (intermedio-bajo)
            (255, 0, 0),    # Rojo (intermedio)
            (255, 165, 0),  # Naranja (intermedio-alto)
            (255, 255, 255)  # Blanco (alto)
        ]
        colores = colores[::-1]  # esto se usa para invertir los colores

        # Normalizar el valor entre 0 y 1
        valor_normalizado = (valor - minimo) / (maximo - minimo)

        # Determinar en qué tramo está el valor
        num_tramos = len(colores) - 1
        indice_tramo = int(valor_normalizado * num_tramos)
        indice_tramo = max(0, min(indice_tramo, num_tramos - 1))  # Asegurar que esté dentro de los límites

        # Calcular el porcentaje dentro de ese tramo
        tramo_inicio = indice_tramo / num_tramos
        tramo_fin = (indice_tramo + 1) / num_tramos
        factor_interpolacion = (valor_normalizado - tramo_inicio) / (tramo_fin - tramo_inicio)

        # Interpolar entre el color del tramo actual y el siguiente
        color_inicio = colores[indice_tramo]
        color_fin = colores[indice_tramo + 1]

        color_resultante = [
            int(min(255, max(0, color_inicio[i] + (color_fin[i] - color_inicio[i]) * factor_interpolacion)))
            for i in range(3)
        ]

        return tuple(color_resultante)
