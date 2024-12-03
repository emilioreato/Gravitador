from Engine import Engine
from UI import UI_MANAGER

import pygame
import numpy as np
import cv2
import math
from scipy.ndimage import zoom
from numba import jit


class Universe:

    G = 4300  # constante gravitacional universal ajustada para trabajar con valores pequeños. no usamos 6.674*10**(-18) por eficiencia

    px_to_m_ratio = 2  # esto no se toca a no se ser q sepas lo q estas haciendo. esta calibrado y se cambia constantemente con el zoom

    arrow_vel_mult = 3.8  # mientras mas alto mas velocidad se le dara a un cuerpo con una flecha del mismo tamaño

    restitution_coefficient = 0.4  # coeficiente de restitución (% de conservacion de la energía mecanica en el choque)

    time_scale = 0.00000000262  # 0.000000005 simboliza q tan rapido avanza el tiempo en el simulador. es el multiplicador de los nanosegundos entre iteraciones q se usa luego como dt

    universe_color = (5, 5, 7)  # colores de algunos elementos del sistema
    axis_color = (118, 118, 118)
    grid_color = (70, 70, 70)

    selected_field_color = 0
    field_colors = (
        (
            (5, 5, 6),      # Negro (bajo)
            (180, 15, 15),   # Rojo (intermedio)
            (255, 170, 18),  # Naranja (intermedio-alto)
            (255, 255, 255)  # Blanco (alto)
        ),

        (
            (255, 255, 255),  # Blanco (alto)
            (255, 170, 15),  # Naranja (intermedio-alto)
            (180, 15, 15),   # Rojo (intermedio)
            (128, 0, 32),   # Bordó (intermedio-bajo)
            (6, 5, 7)     # Negro (bajo)
        ),

        (
            (15, 0, 25),      # Violeta oscuro (bajo)
            (50, 20, 80),     # Morado intenso (intermedio-bajo)
            (100, 50, 160),   # Azul-violeta (intermedio)
            (150, 200, 250),  # Azul hielo (intermedio-alto)
            (220, 240, 255)   # Azul pastel (alto)
        ),

        (
            (10, 10, 40),    # Azul noche (bajo)
            (20, 60, 120),   # Azul medio (intermedio-bajo)
            (100, 150, 200),  # Azul cielo claro (intermedio)
            (200, 180, 100),  # Amarillo cálido (intermedio-alto)
            (255, 230, 180)  # Crema suave (alto)
        ),


    )

    body_creation_colors = ((136, 82, 62),
                            (238, 172, 47))

    zoom = 0.5  # el zoom

    grid_spacing_in_meters = 220
    grid_spacing = 110
    actual_grid_mult = 1

    max_x = 1
    max_y = 1

    field_render_res_x = int(Engine.read_line_in_txt("../settings.txt", "field_resolution"))
    field_render_res_y = int(field_render_res_x/(Engine.win_aspect_ratio))

    camera_x = Engine.window_width / 2
    camera_y = Engine.window_height / 2

    min_g = 5
    max_g = 10_000_000

    def gravitational_intensity_at_point(bodies, px, py):
        # Inicializamos la intensidad gravitacional total
        g_total = 0

        # Iteramos sobre todos los cuerpos para calcular el campo gravitacional en el punto (px, py)
        for body in bodies.values():
            # Acumulamos la magnitud total
            g_total += Universe.intensity_operation(Universe.G, body.mass, body.x, px, body.y, py)  # le sumamos la Magnitud de la intensidad gravitacional de este cuerpo

        return g_total

    @staticmethod
    @jit(nopython=True)
    def intensity_operation(G, mass, x, x1, y, y1):
        return G * mass / ((x - x1)**2 + (y - y1)**2)

    @staticmethod
    def draw_field(bodies):

        x_ref, y_ref = Universe.pixels_to_meters((0, 0))

        distance_x_meters = Universe.scalar_pixels_to_meters(Engine.window_width/Universe.field_render_res_x)
        distance_y_meters = Universe.scalar_pixels_to_meters(Engine.window_height/Universe.field_render_res_y)

        dots = np.zeros((Universe.field_render_res_x, Universe.field_render_res_y, 3), dtype=np.uint8)

        for i in range(Universe.field_render_res_x):
            for j in range(Universe.field_render_res_y):

                g_module = Universe.gravitational_intensity_at_point(bodies, x_ref + i * distance_x_meters, y_ref + j * distance_y_meters)*10

                if g_module < Universe.min_g*18000:
                    dots[i, j] = (Universe.field_colors[Universe.selected_field_color][0])
                else:
                    dots[i, j] = Engine.calcular_color(g_module, Universe.min_g, Universe.max_g, Universe.field_colors[Universe.selected_field_color])  # Universe.value_to_rgb(g_module, min_g, max_g)

        resized_image = cv2.resize(dots, (Engine.window_height, Engine.window_width), interpolation=cv2.INTER_LINEAR)  # cv2.INTER_CUBIC  INTER_LINEAR

        surface = pygame.surfarray.make_surface(resized_image)

        Engine.screen.blit(surface, (0, 0))  # Mostrar la superficie en la pantalla

    def draw_axis_and_grid():

        if UI_MANAGER.show_grid:

            for x_offset in range(int(Universe.camera_x % Universe.grid_spacing), Engine.window_width, Universe.grid_spacing):  # Líneas horizontales
                pygame.draw.line(Engine.screen, Universe.grid_color, (x_offset, 0), (x_offset, Engine.window_height), 1)

            for y_offset in range(int(Universe.camera_y % Universe.grid_spacing), Engine.window_height, Universe.grid_spacing):  # Líneas verticales
                pygame.draw.line(Engine.screen, Universe.grid_color, (0, y_offset), (Engine.window_width, y_offset), 1)

            if UI_MANAGER.show_details:
                text = Engine.font1.render(f"cell value: {Universe.grid_spacing_in_meters/Universe.actual_grid_mult:.1f} m", True, Engine.UI_COLORS[0])
                Engine.screen.blit(text, (Engine.window_width / 1.18, Engine.window_height / 50))

        if UI_MANAGER.show_axis:

            if UI_MANAGER.show_grid:
                w = 2
            else:
                w = 1

            pygame.draw.line(Engine.screen, Universe.axis_color, (0, Universe.camera_y), (Engine.window_width, Universe.camera_y), w)  # Línea hacia abajo
            pygame.draw.line(Engine.screen,  Universe.axis_color, (Universe.camera_x, 0), (Universe.camera_x, Engine.window_height),  w)  # Línea hacia la izquierda

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

        Universe.update_grid_spacing()

    @staticmethod
    def pixels_to_meters(pos):
        return ((pos[0]-Universe.camera_x)*Universe.px_to_m_ratio, (pos[1]-Universe.camera_y)*Universe.px_to_m_ratio)

    @staticmethod
    def meters_to_pixels(pos):
        return (pos[0]/Universe.px_to_m_ratio+Universe.camera_x, pos[1]/Universe.px_to_m_ratio+Universe.camera_y)

    @staticmethod
    def scalar_pixels_to_meters(pixels):
        return pixels*Universe.px_to_m_ratio

    @staticmethod
    def scalar_meters_to_pixels(distance_module):
        return distance_module/Universe.px_to_m_ratio

    @staticmethod
    def update_grid_spacing():

        grid_spacing = int(Universe.scalar_meters_to_pixels(Universe.grid_spacing_in_meters))

        value = grid_spacing / (Universe.grid_spacing_in_meters/2)

        if not value == 0:
            Universe.actual_grid_mult = 2**round(math.log2(value))

        Universe.grid_spacing = int(grid_spacing/Universe.actual_grid_mult)

        if Universe.grid_spacing < 32:
            Universe.grid_spacing = 10000
