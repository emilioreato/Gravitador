from numba import jit
import pygame
import numpy as np
import os
from win32con import ENUM_CURRENT_SETTINGS
from win32api import EnumDisplaySettings


os.chdir(os.path.dirname(os.path.abspath(__file__)))  # sets the current directory to the file's directory # noqa


class Engine:

    @staticmethod
    def read_line_in_txt(file_path, text_to_search):  # specific function to save user data and preferences in a txt file

        if not os.path.exists(file_path):  # creates the file if it doesnt exist
            with open(file_path, 'w') as file:
                file.write("fps: system \nshow_grid: yes\nshow_axis: yes\nfield_resolution: 40\nwindow_height(px): 720")  # writes the default values

        else:
            with open(file_path, 'r') as file:
                lines = file.readlines()

            for line in lines:
                if text_to_search in line:
                    # print("".join(line.split(": ")[1:]).strip())
                    return "".join(line.split(": ")[1:]).strip()  # this returns the exact information i want. not the whole line

    # units_scale = 10**10

    win_aspect_ratio = 16/10
    window_height = int(read_line_in_txt("../settings.txt", "window_height(px)"))
    wh = window_height
    window_width = int(window_height * win_aspect_ratio)
    window_size = (window_width, window_height)

    # font1 = pygame.font.SysFont(None, 20)

    UI_COLORS = [
        (140, 140, 140),  # Blanco (alto)
        (255, 165, 0),    # Naranja (intermedio-alto)
        (255, 0, 0),    # Rojo (intermedio)
        (128, 0, 32),   # Bordó (intermedio-bajo)
        (0, 0, 0),      # Negro (bajo)
    ]

    def set_up():

        dev_mode = EnumDisplaySettings(None, ENUM_CURRENT_SETTINGS)  # get the OS's fps setting
        fps_config = Engine.read_line_in_txt("../settings.txt", "fps")
        if fps_config == "system":  # si los fps estan para que sean default entonces obtenemos los fps del sistema
            Engine.fps = dev_mode.DisplayFrequency
        else:  # si se especificaron unos fps especificos en el archivo de configuracion entonces usamos ese valor
            Engine.fps = int(fps_config)

        Engine.timer = pygame.time.Clock()

        Engine.screen = pygame.display.set_mode(Engine.window_size)

        # Engine.alpha_surface = pygame.Surface((Engine.window_width, Engine.window_height), pygame.SRCALPHA)  # SRCALPHA permite usar alpha

        pygame.display.set_caption("Gravitum: Simulador de gravitación 2D [by: Aaron, Javier & Emilio]")

        pygame.display.set_icon(pygame.image.load("media\\icon.png").convert_alpha())  # sets window icon

        Engine.font1 = pygame.font.SysFont("Times New Roman", Engine.wh//38)

    @jit(nopython=True)
    def calcular_color(valor, minimo, maximo, colores):
        # colores = colores[::-1]  # esto se usa para invertir los colores

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

        return color_resultante
