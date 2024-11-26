from Engine import Engine
import pygame
import numpy as np
from scipy.ndimage import zoom
import cv2


class Universe:

    G = 3500  # 6.674*10**(-18)

    px_to_m_ratio = (60/30)

    time_scale = 0.000000005

    universe_color = (5, 5, 7)
    grid_color = (120, 120, 120)

    field_colors = (
        (6, 5, 6),      # Negro (bajo)
        (128, 0, 32),   # Bordó (intermedio-bajo)
        (255, 15, 5),    # Rojo (intermedio)
        (255, 170, 5),  # Naranja (intermedio-alto)
        (255, 255, 255)  # Blanco (alto)
    )

    body_creation_colors = ((147, 89, 68),
                            (227, 170, 57))

    zoom = 0.5

    field_render_res_x = 58
    field_render_res_y = int(field_render_res_x/(Engine.win_aspect_ratio))

    camera_x = Engine.window_width / 2
    camera_y = Engine.window_height / 2

    min_g = 500
    max_g = 10_000_000_000

    def gravitational_intensity_at_point(bodies, px, py):
        # Inicializamos la intensidad gravitacional total
        g_total = 0

        # Iteramos sobre todos los cuerpos para calcular el campo gravitacional en el punto (px, py)
        for body in bodies.values():
            # Calculamos la distancia entre el cuerpo y el punto (px, py)
            dx = body.x - px
            dy = body.y - py
            r_squared = dx**2 + dy**2

            if r_squared == 0:  # Evitar división por cero si el punto es exactamente sobre el cuerpo
                continue

            # Magnitud de la intensidad gravitacional de este cuerpo
            g_magnitude = Universe.G * body.mass / r_squared

            # Acumulamos la magnitud total
            g_total += g_magnitude

        return g_total

    @staticmethod
    def draw_field(bodies):

        x_ref, y_ref = Universe.pixels_to_meters((0, 0))

        distance_x_meters = Universe.scalar_pixels_to_meters(Engine.window_width/Universe.field_render_res_x)
        distance_y_meters = Universe.scalar_pixels_to_meters(Engine.window_height/Universe.field_render_res_y)

        # dots = np.zeros((Universe.field_render_res_x, Universe.field_render_res_y))
        dots = np.zeros((Universe.field_render_res_x, Universe.field_render_res_y, 3), dtype=np.uint8)

        for i in range(Universe.field_render_res_x):
            for j in range(Universe.field_render_res_y):
                px = x_ref + i * distance_x_meters
                py = y_ref + j * distance_y_meters

                g_module = Universe.gravitational_intensity_at_point(bodies, px, py)*10000
                # print(g_module)
                color = Engine.calcular_color(g_module, Universe.min_g, Universe.max_g, Universe.field_colors)

                dots[i, j] = color  # Universe.value_to_rgb(g_module, min_g, max_g)

                # if g_module < Universe.min_g:
                #    Universe.min_g = g_module
                # if g_module > Universe.max_g:
                #    Universe.max_g = g_module

        # dots = np.clip(dots, 0, 255)

        resized_image = cv2.resize(dots, (int(Engine.window_height), int(Engine.window_width)), interpolation=cv2.INTER_CUBIC)  # cv2.INTER_CUBIC  INTER_LINEAR

        # print(f"Forma de la imagen original: {dots.shape}", f"Forma de la imagen original: {resized_image.shape}")  # Esto debe ser (alto, ancho, 3)

        # resized_image = np.uint8(resized_image)

        surface = pygame.surfarray.make_surface(resized_image)

        # Mostrar la superficie en la pantalla
        Engine.screen.blit(surface, (0, 0))

        # for i in range(dots.shape[0]):
        # for j in range(dots.shape[1]):

        # color_arr[i, j] = Engine.value_to_rgb(dots[i, j], min_g, max_g)

        # Escalar el arreglo a una resolución más alta
        # scaled_arr = zoom(dots, (Engine.window_width/Universe.field_render_res_x, Engine.window_height/Universe.field_render_res_y), order=1)

        # Crear un arreglo donde cada valor es un color en función de la intensidad
        # color_arr = np.zeros((dots.shape[0], dots.shape[1], 3), dtype=np.uint8)  # Arreglo de colores

        # Convertir el arreglo de colores a una superficie de Pygame

    def draw_axis():
        x, y = (Universe.camera_x, Universe.camera_y)

        pygame.draw.line(Engine.screen, Universe.grid_color, (0, y), (Engine.window_width, y), int(2*(Universe.zoom**0.5)))  # Línea hacia abajo
        pygame.draw.line(Engine.screen,  Universe.grid_color, (x, 0), (x, Engine.window_height),  int(2*Universe.zoom**0.5))  # Línea hacia la izquierda

        # pygame.draw.line(screen,  Universe.grid_color, (x, y), (x - length, y), 2)
        # pygame.draw.line(screen,  Universe.grid_color, (x, y), (x + length, y), 2)  # Línea hacia la derecha

    def set_px_m_ratio(bodies=None, re_check=True, mouse_pos=None):  # this lets you set the bounders based on the particles in screen. zoom initially set as -20% (1.2)
        if re_check:  # si se pasa re_check tambien se tiene q pasar bodies para
            Universe.max_x = max(abs(body.x) for body in bodies.values())  # si esta activado el re_check se reposiciona la camara para mostrar todos los objetos en pantalla
            Universe.max_y = max(abs(body.y) for body in bodies.values())

        if mouse_pos is not None:
            coor_x, coor_y = Universe.pixels_to_meters(mouse_pos)  # si se pasa coordenadas (mouse_pos) se usaran para dirigir hacia donde ira el zoom

        # se elige el ratio basado en el eje q esta mas apretado con cuerpos en pantalla. osea q si tienes muchos cuerpos verticalmente alineados se calculara en base a la distancia entre el mas alto y el menos alto, no influira lo q tengas en el eje y a no ser q la distancia entre el mas a la izq y el mas a la der sea mayor a la distancia entre el mas alto y el mas bajo pero siempre aplicando la relacion de aspecto de la pantalla q es 16:9.
        if Universe.max_x/Engine.window_width >= Universe.max_y/Engine.window_height:
            Universe.px_to_m_ratio = (2*Universe.max_x)/(Engine.window_width*Universe.zoom)
        else:
            Universe.px_to_m_ratio = (2*Universe.max_y)/(Engine.window_height*Universe.zoom)

        if mouse_pos is not None:
            px_pos_x_new, px_pos_y_new = Universe.meters_to_pixels((coor_x, coor_y))

            offset_x = mouse_pos[0] - px_pos_x_new  # se obtiene la diferencia entre la coordenadas en pixeles en eje x de antes de modificar el ratio.
            offset_y = mouse_pos[1] - px_pos_y_new

            Universe.camera_x += offset_x  # ese desfase se le suma a la posicion de la camara para que el zoom se haga en la posicion del mouse
            Universe.camera_y += offset_y

    @staticmethod
    def pixels_to_meters(pos):
        return ((pos[0]-Universe.camera_x)*Universe.px_to_m_ratio, (pos[1]-Universe.camera_y)*Universe.px_to_m_ratio)

    @staticmethod
    def meters_to_pixels(pos):
        # print(Universe.camera_x)
        return (pos[0]/Universe.px_to_m_ratio+Universe.camera_x, pos[1]/Universe.px_to_m_ratio+Universe.camera_y)

    @staticmethod
    def scalar_pixels_to_meters(pixels):
        return pixels*Universe.px_to_m_ratio
    from numba import jit

    @staticmethod
    def scalar_meters_to_pixels(distance_module):
        return distance_module/Universe.px_to_m_ratio
