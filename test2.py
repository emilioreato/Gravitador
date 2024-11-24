import pygame
import math

# Configuraciones iniciales
WIDTH, HEIGHT = 800, 600
BACKGROUND_COLOR = (30, 30, 30)
FPS = 60

# Inicializar Pygame
pygame.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulador de colisiones inelásticas")
clock = pygame.time.Clock()

# Clases


class Ball:
    def __init__(self, x, y, radius, mass, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.mass = mass
        self.color = color
        self.vx = 0
        self.vy = 0

    def draw(self, window):
        pygame.draw.circle(window, self.color, (int(self.x), int(self.y)), self.radius)

    def move(self):
        self.x += self.vx
        self.y += self.vy

    def check_wall_collision(self):
        if self.x - self.radius < 0 or self.x + self.radius > WIDTH:
            self.vx *= -0.8  # Coeficiente de restitución para paredes
        if self.y - self.radius < 0 or self.y + self.radius > HEIGHT:
            self.vy *= -0.8

        # Ajustar posición para evitar salir de la pantalla
        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))

# Funciones auxiliares


def detect_collision(ball1, ball2):
    dx = ball2.x - ball1.x
    dy = ball2.y - ball1.y
    distance = math.sqrt(dx**2 + dy**2)
    return distance < ball1.radius + ball2.radius


def resolve_collision(ball1, ball2, restitution=0.8):
    # Vector normal
    dx = ball2.x - ball1.x
    dy = ball2.y - ball1.y
    distance = math.sqrt(dx**2 + dy**2)
    if distance == 0:
        return  # Evitar divisiones por cero

    overlap = ball1.radius + ball2.radius - distance
    nx = dx / distance
    ny = dy / distance

    # Separar las bolas para evitar superposición
    ball1.x -= nx * overlap / 2
    ball1.y -= ny * overlap / 2
    ball2.x += nx * overlap / 2
    ball2.y += ny * overlap / 2

    # Velocidades relativas en la dirección normal
    dvx = ball2.vx - ball1.vx
    dvy = ball2.vy - ball1.vy
    rel_velocity = dvx * nx + dvy * ny

    if rel_velocity > 0:
        return

    # Impulso ajustado por inelasticidad
    impulse = (-(1 + restitution) * rel_velocity) / (1 / ball1.mass + 1 / ball2.mass)

    # Actualizar velocidades
    ball1.vx += (impulse * nx / ball1.mass)
    ball1.vy += (impulse * ny / ball1.mass)
    ball2.vx -= (impulse * nx / ball2.mass)
    ball2.vy -= (impulse * ny / ball2.mass)


# Lista de bolas
balls = []

# Loop principal
running = True
selected_ball = None
while running:
    window.fill(BACKGROUND_COLOR)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Crear bolas con clic derecho
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            x, y = pygame.mouse.get_pos()
            new_ball = Ball(x, y, radius=20, mass=1, color=(0, 255, 0))
            balls.append(new_ball)

        # Seleccionar bolas con clic izquierdo
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = pygame.mouse.get_pos()
            for ball in balls:
                if math.hypot(ball.x - x, ball.y - y) <= ball.radius:
                    selected_ball = ball

        # Soltar bola seleccionada
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if selected_ball:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                selected_ball.vx = (mouse_x - selected_ball.x) / 10
                selected_ball.vy = (mouse_y - selected_ball.y) / 10
                selected_ball = None

    # Dibujar y mover bolas
    for ball in balls:
        ball.move()
        ball.check_wall_collision()
        ball.draw(window)

    # Detectar y resolver colisiones
    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            if detect_collision(balls[i], balls[j]):
                resolve_collision(balls[i], balls[j])

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
