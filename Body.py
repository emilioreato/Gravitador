from numba import jit
import string
import random
import pygame
from Engine import Engine
from Universe import Universe
import numpy as np
import math


class Body:

    COLORS = [(30, 50, 70),
              (70, 80, 20),
              (110, 30, 20),
              (50, 10, 150),
              ]

    def __init__(self, mass, pos, vel):

        self.id = Body.generate_id()

        self.mass = mass

        self.radius = 10**9.5  # self.mass ** 0.434

        self.color = Body.COLORS[0]

        self.x, self.y = pos
        self.x_px, self.y_px = (5, 5)

        self.vel_x,  self.vel_y = vel  # this should be a tuple with x and y axis velocity

    def draw(self, screen):

        print(self.x_px, self.y_px,  self.radius_px)

        pygame.draw.circle(screen, self.color, (self.x_px, self.y_px), self.radius_px)

    def move(self, pos):
        self.x, self.y = Universe.pixels_to_meters(pos)

    import numpy as np

    def calculate_force(self, other_bodies, G=Universe.G):
        """
        Calcula la fuerza gravitacional resultante ejercida sobre este cuerpo
        por todos los demás cuerpos en el diccionario.

        Args:
            other_bodies (dict): Diccionario de cuerpos {id: body}, donde cada body tiene propiedades x, y y mass.
            G (float): Constante gravitacional. Por defecto, 6.67430e-11 N·m²/kg².

        Returns:
            tuple: Fuerza resultante en forma de (Fx, Fy).
        """
        Fx, Fy = 0.0, 0.0  # Componentes iniciales de la fuerza

        for other_body in other_bodies.values():

            if other_body is self:  # Evitar calcular la fuerza sobre sí mismo
                continue

            dx = other_body.x - self.x  # separacion en eje x
            dy = other_body.y - self.y  # separacion en eje y
            distance = math.sqrt(dx**2 + dy**2)  # np.sqrt(dx**2 + dy**2)  # modulo de distancia

            if distance == 0:
                continue  # Evitar division por cero

            # Magnitud de la fuerza gravitacional
            force = G * self.mass * other_body.mass / distance**2  # no va negativa porque el vector dx dy ya se encarga a continuacion

            # Descomponer la fuerza en componentes x e y
            Fx += force * (dx / distance)  # esto ya esta considerando la direccion sobre el eje x con el q la fuerza actua al incluir dx
            Fy += force * (dy / distance)

        return Fx, Fy

    def update_a_v_pos_based_on_force(self, Fx, Fy, dt):
        # Aceleración
        ax = Fx / self.mass
        ay = Fy / self.mass

        # Actualizar velocidad
        self.vel_x += ax * dt
        self.vel_y += ay * dt

        # Actualizar posición
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt

    def update_px_based_on_pos(self):
        self.x_px, self.y_px = Universe.meters_to_pixels((self.x, self.y))

    def update_radius_px(self):
        self.radius_px = Universe.scalar_meters_to_pixels(self.radius)

    def is_clicked(self, mouse_pos):
        return (mouse_pos[0]-self.x_px)**2 + (mouse_pos[1]-self.y_px)**2 <= self.radius_px**2

    def generate_id(length=5):
        chars = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(chars) for _ in range(length))
