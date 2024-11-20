from numba import jit
import pygame
import math
import sys
import numpy as np

# Inicializar Pygame
pygame.init()

# Dimensiones de la pantalla
FPS = 60

screen_width = 1280
screen_height = 720

screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption("Simulador de Gravedad 2D - Emilio Reato, Aaron Rodriguez Aliata")


G = 0.5  # Constante gravitacional ajustada
MIN_DIST = 10  # Distancia mínima para evitar aceleración infinita


class Body:  # Clase que representa un cuerpo con masa
    def __init__(self, x, y, mass, radius, color):
        self.x = x
        self.y = y
        self.mass = mass
        self.radius = radius
        self.color = color
        self.vx = 0
        self.vy = 0
        self.trail = []  # Estela del cuerpo

    def apply_gravity(self, bodies):
        for other in bodies:
            if other != self:
                dx = other.x - self.x
                dy = other.y - self.y
                dist = math.sqrt(dx**2 + dy**2)
                if dist > MIN_DIST:  # Evitar aceleración infinita
                    # Calcular la fuerza gravitatoria
                    force = G * self.mass * other.mass / dist**2
                    angle = math.atan2(dy, dx)
                    fx = force * math.cos(angle)
                    fy = force * math.sin(angle)
                    # Actualizar la velocidad según la fuerza aplicada
                    self.vx += fx / self.mass
                    self.vy += fy / self.mass

    def update_position(self):
        # Actualizar la posición del cuerpo
        self.x += self.vx
        self.y += self.vy

        # Agregar la posición a la estela
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 50:  # Limitar el tamaño de la estela
            self.trail.pop(0)

        # Confinar el cuerpo dentro de los límites de la pantalla
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx *= -1
        elif self.x + self.radius > screen_width:
            self.x = screen_width - self.radius
            self.vx *= -1

        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy *= -1
        elif self.y + self.radius > screen_height:
            self.y = screen_height - self.radius
            self.vy *= -1

    def draw(self, screen):
        # Dibujar la estela
        for pos in self.trail:
            pygame.draw.circle(screen, (60, 40, 40), pos, 1)
        # Dibujar el cuerpo
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)


# Crear cuerpos (planetas/estrellas)
bodies = [Body(400, 350, 1900, 20, (255, 255, 0)),
          Body(600, 500, 1900, 20, (255, 255, 0)),
          Body(250, 1000, 1900, 20, (255, 255, 0)),


          ]
# for i in range(6):
#    bodies.append(Body(i+i*20, 100+i*9, 5+i/10, 5, (60+i*8, 50+i*10, 30)))

selected_body = None  # Cuerpo seleccionado para mover

# Función para calcular la intensidad del campo gravitacional en un punto (x, y)


@jit(nopython=True)
def calculate_gravity_intensity(x, y, bodies_x, bodies_y, bodies_mass):
    intensity = 0.0
    for i in range(len(bodies_x)):
        dx = bodies_x[i] - x
        dy = bodies_y[i] - y
        dist = math.sqrt(dx**2 + dy**2)
        if dist > MIN_DIST:
            intensity += G * bodies_mass[i] / dist**2
    return intensity

# Función para mapear la intensidad a un color
# Función para mapear la intensidad a un color (negro -> rojo -> blanco)


@jit(nopython=True)
def intensity_to_color(intensity):
    # Limitar la intensidad a un rango razonable basado en observación
    min_intensity = 0.02  # Ajuste de intensidad mínima
    max_intensity = 1  # Ajuste de intensidad máxima

    # Elevar la intensidad para asegurar que haya un valor mínimo visible
    intensity = max(intensity, min_intensity)
    intensity = min(intensity, max_intensity)

    # Mapear intensidad a colores (negro -> rojo -> blanco)
    if intensity < max_intensity / 2:
        # De negro a rojo
        red = int(255 * (intensity / (max_intensity / 2)))
        green = 10
        blue = 10
    else:
        # De rojo a blanco
        red = 255
        green = int(255 * ((intensity - (max_intensity / 2)) / (max_intensity / 2)))
        blue = int(255 * ((intensity - (max_intensity / 2)) / (max_intensity / 2)))

    return (red, green, blue)


# Bucle principal
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Seleccionar un cuerpo al hacer clic
            mx, my = pygame.mouse.get_pos()
            for body in bodies:
                dist = math.sqrt((body.x - mx) ** 2 + (body.y - my) ** 2)
                if dist <= body.radius:
                    selected_body = body
                    break
        elif event.type == pygame.MOUSEBUTTONUP:
            # Soltar el cuerpo al soltar el clic
            selected_body = None
        elif event.type == pygame.MOUSEMOTION:
            # Mover el cuerpo seleccionado
            if selected_body:
                selected_body.x, selected_body.y = pygame.mouse.get_pos()
                selected_body.vx, selected_body.vy = 0, 0  # Detener su velocidad

    # Calcular el fondo en base a la intensidad del campo gravitacional
    bodies_x = np.array([body.x for body in bodies])
    bodies_y = np.array([body.y for body in bodies])
    bodies_mass = np.array([body.mass for body in bodies])

    # Calcular la intensidad con la función optimizada por Numba

    for y in range(0, screen_height, 5):
        for x in range(0, screen_width, 5):
            intensity = calculate_gravity_intensity(x, y, bodies_x, bodies_y, bodies_mass)
            color = intensity_to_color(intensity)
            pygame.draw.rect(screen, color, (x, y, 5, 5))

    # Aplicar la gravedad y actualizar la posición de cada cuerpo
    for body in bodies:
        body.apply_gravity(bodies)
        body.update_position()

    # Dibujar los cuerpos
    for body in bodies:
        body.draw(screen)

    # Actualizar la pantalla
    pygame.display.flip()

    # Limitar la velocidad a 60 fotogramas por segundo
    clock = pygame.time.Clock()
    clock.tick(FPS)

# Salir del programa
pygame.quit()
sys.exit()
