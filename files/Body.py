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

    def __init__(self, mass, pos, vel, color=None):

        self.id = Body.generate_id()

        self.mass = mass

        self.radius = mass / (5*10**3)  # 294401.3 * math.log10(mass) - 1272006.5  # self.mass ** 0.434
        print(self.radius)

        if color == None:
            color = Engine.calcular_color(Universe.scalar_meters_to_pixels(self.radius), 1, Engine.window_height/4, colores=Universe.body_creation_colors)
        self.color = color  # Body.COLORS[1]

        self.x, self.y = pos
        self.x_px, self.y_px = (5, 5)

        self.vel_x,  self.vel_y = vel  # this should be a tuple with x and y axis velocity

    def draw(self):

        pygame.draw.circle(Engine.screen, self.color, (self.x_px, self.y_px), self.radius_px)  # self.color

    def move(self, pos):
        self.x, self.y = Universe.pixels_to_meters(pos)

    def calculate_force(self, other_bodies, G=Universe.G):

        Fx, Fy = 0.0, 0.0  # Componentes iniciales de la fuerza

        for other_body in other_bodies:

            if other_body is self:  # Evitar calcular la fuerza sobre sí mismo
                continue

            dx = other_body.x - self.x  # separacion en eje x
            dy = other_body.y - self.y  # separacion en eje y
            distance = (dx**2 + dy**2)**0.5  # math.sqrt(dx**2 + dy**2)  # np.sqrt(dx**2 + dy**2)  # modulo de distancia

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
            if body is self:  # No comprobar la superposición consigo mismo
                continue
            distance = ((body.x - self.x)**2 + (body.y - self.y)**2)**0.5  # math.sqrt((body.x - self.x)**2 + (body.y - self.y)**2)
            if distance <= self.radius + body.radius:
                overlaps.append(id)  # Guardar el índice del cuerpo que se superpone
        if overlaps == []:
            return None
        else:
            return overlaps

    @staticmethod
    def inelastic_collision_2d(m1, v1, m2, v2, e, pos1, pos2):
        # Vector normal (dirección de impacto)
        n = np.array(pos2) - np.array(pos1)
        n = n / np.linalg.norm(n)  # Normalizar

        # Vector tangencial (perpendicular al normal)
        t = np.array([-n[1], n[0]])

        # Proyecciones de las velocidades en los ejes normal y tangente
        v1n = np.dot(v1, n)
        v1t = np.dot(v1, t)
        v2n = np.dot(v2, n)
        v2t = np.dot(v2, t)

        # Nuevas velocidades normales tras la colisión
        v1n_post = ((m1 - e * m2) * v1n + (1 + e) * m2 * v2n) / (m1 + m2)
        v2n_post = ((m2 - e * m1) * v2n + (1 + e) * m1 * v1n) / (m1 + m2)

        # Velocidades finales (recomposición)
        v1_post = v1n_post * n + v1t * t
        v2_post = v2n_post * n + v2t * t

        return v1_post, v2_post

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

    @staticmethod
    def creation_draw(creation_pos, mouse_pos, returnn=False):

        radius_px = int(math.sqrt((mouse_pos[0]-creation_pos[0])**2 + (mouse_pos[1]-creation_pos[1])**2))

        color = Engine.calcular_color(radius_px, 1, Engine.window_height/4, colores=Universe.body_creation_colors)

        pygame.draw.circle(Engine.screen, color, creation_pos, radius_px)

        text = Engine.font1.render(f"{Universe.scalar_pixels_to_meters(radius_px):.1f}", True, Engine.UI_COLORS[0])

        Engine.screen.blit(text, (mouse_pos[0]+Engine.wh//30, mouse_pos[1]-Engine.wh//30))

        if returnn:
            print(radius_px)
            if radius_px == 0:
                radius_px = 2
            return Universe.scalar_pixels_to_meters(radius_px) * 5*10**3, color
            # return 10 ** ((Universe.scalar_pixels_to_meters(radius_px) + 1272006.5) / 294401.3)
