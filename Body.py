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
              (220, 190, 35),
              (110, 30, 20),
              (50, 10, 150),
              ]

    def __init__(self, mass, pos, vel):

        self.id = Body.generate_id()

        self.mass = mass

        self.radius = 10**9.5  # self.mass ** 0.434

        self.color = Body.COLORS[1]

        self.x, self.y = pos
        self.x_px, self.y_px = (5, 5)

        self.vel_x,  self.vel_y = vel  # this should be a tuple with x and y axis velocity

    def draw(self, screen):

        # print(self.x_px, self.y_px,  self.radius_px)

        pygame.draw.circle(screen, self.color, (self.x_px, self.y_px), self.radius_px)

    def move(self, pos):
        self.x, self.y = Universe.pixels_to_meters(pos)

    import numpy as np

    def calculate_force(self, other_bodies, G=Universe.G):

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

    def check_overlap_by_brute_force(self, bodies):
        overlaps = []
        for id, body in bodies.items():
            distance = math.sqrt((body.x - self.x)**2 + (body.y - self.y)**2)
            if distance <= self.radius + body.radius:
                overlaps.append(id)  # Guardar el índice del cuerpo que se superpone
        return overlaps

    import numpy as np

    import numpy as np

    def inelastic_collision(body1, body2, e):
        # Calculamos el vector normal entre los dos cuerpos
        dx = body2.x - body1.x
        dy = body2.y - body1.y
        distance = np.sqrt(dx**2 + dy**2)

        if distance == 0:  # Evitar división por cero
            return

        normal = np.array([dx / distance, dy / distance])  # Vector unitario normal

        # Componentes de la velocidad en la dirección normal y tangencial
        velocity1 = np.array([body1.vel_x, body1.vel_y])
        velocity2 = np.array([body2.vel_x, body2.vel_y])

        # Proyección de las velocidades sobre la dirección normal
        normal_velocity1 = np.dot(velocity1, normal)
        normal_velocity2 = np.dot(velocity2, normal)

        # Componentes tangenciales (no se modifican en una colisión inelástica parcial)
        tangent_velocity1 = velocity1 - normal * normal_velocity1
        tangent_velocity2 = velocity2 - normal * normal_velocity2

        # Cálculo de las nuevas velocidades normales, usando el coeficiente de restitución
        new_normal_velocity1 = (normal_velocity1 * (body1.mass - body2.mass) + 2 * body2.mass * normal_velocity2) / (body1.mass + body2.mass)
        new_normal_velocity2 = (normal_velocity2 * (body2.mass - body1.mass) + 2 * body1.mass * normal_velocity1) / (body1.mass + body2.mass)

        # Aplicamos el coeficiente de restitución solo a la velocidad normal (no modificamos la tangencial)
        normal_velocity1 = (1 - e) * normal_velocity1 + e * new_normal_velocity1
        normal_velocity2 = (1 - e) * normal_velocity2 + e * new_normal_velocity2

        # Actualizamos las velocidades con las nuevas velocidades normales y manteniendo las tangenciales
        body1.vel_x = normal_velocity1 * normal[0] + tangent_velocity1[0]
        body1.vel_y = normal_velocity1 * normal[1] + tangent_velocity1[1]
        body2.vel_x = normal_velocity2 * normal[0] + tangent_velocity2[0]
        body2.vel_y = normal_velocity2 * normal[1] + tangent_velocity2[1]

        # Separar ligeramente los cuerpos si están superpuestos (opcional)
        overlap = body1.radius + body2.radius - distance
        if overlap > 0:
            separation_distance = overlap * 0.5
            body1.x -= separation_distance * normal[0]
            body1.y -= separation_distance * normal[1]
            body2.x += separation_distance * normal[0]
            body2.y += separation_distance * normal[1]

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
