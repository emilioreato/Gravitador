from numba import jit
import pygame


from win32con import ENUM_CURRENT_SETTINGS
from win32api import EnumDisplaySettings


class Engine:

    win_aspect_ratio = 16/12
    window_height = 640
    window_width = window_height * win_aspect_ratio
    window_size = (window_width, window_height)

    def set_up():

        dev_mode = EnumDisplaySettings(None, ENUM_CURRENT_SETTINGS)  # get the OS's fps setting
        Engine.fps = dev_mode.DisplayFrequency
        Engine.timer = pygame.time.Clock()

        Engine.screen = pygame.display.set_mode(Engine.window_size)
        pygame.display.set_caption("Ventana Básica de Pygame")
