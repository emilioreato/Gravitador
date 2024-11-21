from Engine import Engine
import pygame


class Universe:

    G = 6.674*10**(-11)

    px_to_m_ratio = None

    time_scale = (2)*10**2

    universe_color = (5, 5, 5)
    grid_color = (30, 30, 30)

    zoom = 0.5

    camera_x = Engine.window_width / 2
    camera_y = Engine.window_height / 2

    def draw_axis(screen):
        x, y = (Universe.camera_x, Universe.camera_y)
        pygame.draw.line(screen, Universe.grid_color, (0, y), (Engine.window_width, y), int(2*(Universe.zoom**0.5)))  # Línea hacia abajo
        pygame.draw.line(screen,  Universe.grid_color, (x, 0), (x, Engine.window_height),  int(2*Universe.zoom**0.5))  # Línea hacia la izquierda
        # pygame.draw.line(screen,  Universe.grid_color, (x, y), (x - length, y), 2)
        # pygame.draw.line(screen,  Universe.grid_color, (x, y), (x + length, y), 2)  # Línea hacia la derecha

    def set_px_m_ratio_based_on_bodies(bodies, re_check=True):  # this lets you set the bounders based on the particles in screen. zoom set as -20% (1.2)
        if re_check:
            Universe.max_x = max(abs(body.x) for body in bodies.values())
            Universe.max_y = max(abs(body.y) for body in bodies.values())

        if Universe.max_x/Engine.window_width >= Universe.max_y/Engine.window_height:
            Universe.px_to_m_ratio = (2*Universe.max_x)/(Engine.window_width*Universe.zoom)
        else:
            Universe.px_to_m_ratio = (2*Universe.max_y)/(Engine.window_height*Universe.zoom)

    @staticmethod
    def pixels_to_meters(pos):
        return ((pos[0]-Universe.camera_x)*Universe.px_to_m_ratio, (pos[1]-Universe.camera_y)*Universe.px_to_m_ratio)

    @staticmethod
    def meters_to_pixels(pos):
        print(Universe.camera_x)
        return (pos[0]/Universe.px_to_m_ratio+Universe.camera_x, pos[1]/Universe.px_to_m_ratio+Universe.camera_y)

    @staticmethod
    def scalar_pixels_to_meters(pixels):
        return pixels*Universe.px_to_m_ratio

    @staticmethod
    def scalar_meters_to_pixels(distance_module):
        return distance_module/Universe.px_to_m_ratio
