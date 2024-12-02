from numba import jit
import string
import random
import pygame
from Engine import Engine
from UI import UI_MANAGER
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

        self.radius = mass / (10*10**3)  # 294401.3 * math.log10(mass) - 1272006.5  # self.mass ** 0.434
        # print(self.radius)

        if color == None:
            color = Engine.calcular_color(Universe.scalar_meters_to_pixels(self.radius), 1, Engine.window_height/4, colores=Universe.body_creation_colors)
        self.color = color  # Body.COLORS[1]

        self.x, self.y = pos
        self.x_px, self.y_px = (5, 5)

        self.vel_x,  self.vel_y = vel  # this should be a tuple with x and y axis velocity

    def draw(self):
        if UI_MANAGER.show_circles:
            pygame.draw.circle(Engine.screen, self.color, (self.x_px, self.y_px), self.radius_px)  # self.color
        if UI_MANAGER.show_details:
            line1 = Engine.font1.render(f"{self.mass/1000:.0f} mil kg", True, Engine.UI_COLORS[5])
            line2 = Engine.font1.render(f"{(self.vel_x**2 + self.vel_y**2)**0.5:.1f} m/s", True, Engine.UI_COLORS[5])

            Engine.screen.blit(line1, (self.x_px - Engine.window_height/30, self.y_px - Engine.window_height/50))
            Engine.screen.blit(line2, (self.x_px - Engine.window_height/30, self.y_px - Engine.window_height/50 + line1.get_height()))

    def move(self, pos):  # se le pasa una pos en pixeles
        self.x_px, self.y_px = pos  # se actualiza la posicion en pixeles
        self.x, self.y = Universe.pixels_to_meters(pos)  # se convierte la pos en metros y se actualiza

    def calculate_force(self, other_bodies, G=Universe.G):

        Fx, Fy = 0.0, 0.0  # Componentes iniciales de la fuerza

        for other_body in other_bodies:

            if other_body is self:  # Evitar calcular la fuerza sobre sí mismo
                continue

            dx = other_body.x - self.x  # separacion en eje x
            dy = other_body.y - self.y  # separacion en eje y
            distance = dx**2 + dy**2  # math.sqrt(dx**2 + dy**2)  # np.sqrt(dx**2 + dy**2)  # modulo de distancia

            # Magnitud de la fuerza gravitacional
            force = G * self.mass * other_body.mass / distance  # no va negativa porque el vector dx dy ya se encarga a continuacion
            # tampoco va la distancia el cuadrado ya que no estamos haciendole la raiz cuadrada cuando calculalos la distancia

            squared_distance = math.sqrt(distance)

            # Descomponer la fuerza en componentes x e y
            Fx += force * (dx / squared_distance)  # esto ya esta considerando la direccion sobre el eje x con el q la fuerza actua al incluir dx
            Fy += force * (dy / squared_distance)

        return Fx, Fy

    def check_overlap_continuous(self, bodies, dt):
        overlaps = []
        start_pos = np.array([self.x, self.y])
        end_pos = start_pos + np.array([self.vel_x, self.vel_y]) * dt

        for id, body in bodies.items():
            if body is self:
                continue

            center = np.array([body.x, body.y])
            radius = self.radius + body.radius  # Radio efectivo de colisión

            # Vector de la trayectoria
            d = end_pos - start_pos
            f = start_pos - center

            # Resolver intersección usando ecuación cuadrática
            a = np.dot(d, d)
            b = 2 * np.dot(f, d)
            c = np.dot(f, f) - radius**2
            discriminant = b**2 - 4 * a * c

            if discriminant >= 0:  # Hay intersección
                discriminant = np.sqrt(discriminant)
                t1 = (-b - discriminant) / (2 * a)
                t2 = (-b + discriminant) / (2 * a)

                # Verificar si la intersección ocurre en el intervalo [0, 1]
                if 0 <= t1 <= 1 or 0 <= t2 <= 1:
                    overlaps.append(id)

        return overlaps if overlaps else None

    def check_overlap_by_brute_force(self, bodies):

        overlaps = set()
        for body in bodies.values():

            total_radius = self.radius + body.radius

            if body is self:  # No comprobar la superposición consigo mismo
                continue
            if abs(body.x - self.x) > total_radius:  # si esta
                continue
            if abs(body.y - self.y) > total_radius:
                continue

            distance = ((body.x - self.x)**2 + (body.y - self.y)**2)  # math.sqrt((body.x - self.x)**2 + (body.y - self.y)**2)
            if distance <= total_radius**2:
                overlaps.add(body.id)  # Guardar el índice del cuerpo que se superpone

        if not overlaps:  # si overlaps esta vacia
            return None
        else:
            return overlaps

    def inelastic_collision_2d(m1, v1, m2, v2, pos1, pos2):
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
        v1n_post = ((m1 - Universe.restitution_coefficient * m2) * v1n + (1 + Universe.restitution_coefficient) * m2 * v2n) / (m1 + m2)
        v2n_post = ((m2 - Universe.restitution_coefficient * m1) * v2n + (1 + Universe.restitution_coefficient) * m1 * v1n) / (m1 + m2)

        # Velocidades finales (recomposición)
        v1_post = v1n_post * n + v1t * t
        v2_post = v2n_post * n + v2t * t

        return v1_post, v2_post

    def update_a_v_based_on_force(self, Fx, Fy, dt):
        ax = Fx / self.mass  # Aceleración
        ay = Fy / self.mass

        self.vel_x += ax * dt  # Actualizar velocidad
        self.vel_y += ay * dt

    def update_pos_based_on_vel(self, dt):
        self.x += self.vel_x * dt  # actualizar la pos en metros
        self.y += self.vel_y * dt

        self.x_px, self.y_px = Universe.meters_to_pixels((self.x, self.y))  # Actualizar posición en píxeles

    def update_radius_px(self):
        self.radius_px = Universe.scalar_meters_to_pixels(self.radius)
        if self.radius_px < 1:
            self.radius_px = 1

    def is_clicked(self, mouse_pos):
        return (mouse_pos[0]-self.x_px)**2 + (mouse_pos[1]-self.y_px)**2 <= self.radius_px**2

    def generate_id(length=5):
        chars = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(chars) for _ in range(length))

    def draw_arrow(start, end, width=6, arrow_size=22):

        # Calcula el ángulo
        angle = math.atan2(end[1] - start[1], end[0] - start[0])

        # actualizamos el nuevo end para q no se dibuje encima del triangulo de la punta. (le restamos longitud)

        modified_end = (end[0]-arrow_size*0.5*math.cos(angle), end[1]-arrow_size*0.5*math.sin(angle))

        # Línea principal
        pygame.draw.line(Engine.screen, Body.COLORS[2], start, modified_end, width)

        # Coordenadas del triángulo de la punta
        arrow_tip = end
        left_wing = (
            end[0] - arrow_size * math.cos(angle - math.pi / 6),
            end[1] - arrow_size * math.sin(angle - math.pi / 6)
        )
        right_wing = (
            end[0] - arrow_size * math.cos(angle + math.pi / 6),
            end[1] - arrow_size * math.sin(angle + math.pi / 6)
        )

        # Dibuja el triángulo
        pygame.draw.polygon(Engine.screen, Body.COLORS[2], [arrow_tip, left_wing, right_wing])

        # dibujar el texto q dice la nueva velocidad

        vels = (((end[0]-start[0])*Universe.arrow_vel_mult)**2 + ((end[1]-start[1])*Universe.arrow_vel_mult)**2)**0.5

        text = Engine.font1.render(f"{vels:.1f} m/s", True, Engine.UI_COLORS[0])

        Engine.screen.blit(text, (end[0]+Engine.wh//30, end[1]-Engine.wh//30))

    @staticmethod
    def creation_draw(creation_pos, mouse_pos, returnn=False):

        radius_px = int(math.sqrt((mouse_pos[0]-creation_pos[0])**2 + (mouse_pos[1]-creation_pos[1])**2))

        color = Engine.calcular_color(radius_px, 1, Engine.window_height/4, colores=Universe.body_creation_colors)

        pygame.draw.circle(Engine.screen, color, creation_pos, radius_px)

        text = Engine.font1.render(f"{Universe.scalar_pixels_to_meters(radius_px) * 5:.0f} mil kg", True, Engine.UI_COLORS[0])

        Engine.screen.blit(text, (mouse_pos[0]+Engine.wh//30, mouse_pos[1]-Engine.wh//30))

        if returnn:
            # print(radius_px)
            if radius_px == 0:
                radius_px = 2
            return Universe.scalar_pixels_to_meters(radius_px) * 10*10**3, color  # ese numero es el q define la relacion entre masa - radio
            # return 10 ** ((Universe.scalar_pixels_to_meters(radius_px) + 1272006.5) / 294401.3)
