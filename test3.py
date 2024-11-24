import numpy as np
from scipy.ndimage import zoom
import matplotlib.pyplot as plt

# Constantes
G = 6.67430e-11  # Constante gravitacional
screen_width_m = 1920  # Ancho del área de simulación en metros
screen_height_m = 1080  # Alto del área de simulación en metros
high_res = 20  # Alta resolución para el cálculo del campo (por ejemplo, 500 puntos)

# Generar grid de puntos en alta resolución
dx_high_res = screen_width_m / high_res
dy_high_res = screen_height_m / (high_res * (9 / 16))  # Mantener proporción 16:9

x_high_res = np.arange(0, screen_width_m, dx_high_res)
y_high_res = np.arange(0, screen_height_m, dy_high_res)
grid_x, grid_y = np.meshgrid(x_high_res, y_high_res)

# Coordenadas de las masas (puedes agregar más cuerpos)
masses = [
    {"mass": 5.972e24, "pos": (screen_width_m / 2, screen_height_m / 2)},  # Tierra en el centro
]

# Inicializar el arreglo de intensidad gravitatoria (en alta resolución)
gravity_field_high_res = np.zeros_like(grid_x, dtype=np.float64)

# Calcular el campo gravitatorio en cada punto del grid de alta resolución
for mass in masses:
    mass_x, mass_y = mass["pos"]
    m = mass["mass"]
    # Distancia al punto (evitar división por cero)
    dx = grid_x - mass_x
    dy = grid_y - mass_y
    r = np.sqrt(dx**2 + dy**2) + 1e-9  # Añadir un pequeño valor para evitar 0
    # Intensidad gravitatoria
    gravity_field_high_res += G * m / r**2

# Ahora ajustamos la resolución visual sin cambiar los valores del campo
resolution = 50  # Número de puntos para la visualización

# Calcular la nueva separación entre puntos para la resolución visual
dx_visual = screen_width_m / resolution
dy_visual = screen_height_m / (resolution * (9 / 16))

# Realizamos el redimensionamiento para ajustarlo a la resolución visual
gravity_field_visual = zoom(gravity_field_high_res, (screen_height_m / len(y_high_res), screen_width_m / len(x_high_res)))

# Opcional: Visualización del campo gravitatorio
plt.imshow(gravity_field_visual, cmap="inferno", extent=(0, screen_width_m, 0, screen_height_m))
plt.colorbar(label="Intensidad del campo gravitatorio (m/s²)")
plt.title("Campo gravitatorio")
plt.xlabel("X (m)")
plt.ylabel("Y (m)")
plt.show()
