### IMPORTING MODULES ###

import pygame
import sys
import win32api
import time
import random

from Engine import Engine
from Universe import Universe
from Body import Body


### SET UP###

pygame.init()
Engine.set_up()


### PROGRAM VARIABLES ###


global follow_mouse_body
follow_mouse_body = False
global follow_mouse_camera
follow_mouse_camera = (False, None)

global selected_body
selected_body = None


global bodies
"""bodies = {
    "0": Body(5.972 * (10**24), (1.5*10**11, 5*10**10), (-1, 2)),
    "1": Body(5.972 * (10**24), (1*10**10, -2*10**10), (1, 2)),
    "2": Body(5.972 * (10**24), (-9*10**10, 6*10**10), (1, 2)),
    "8": Body(5.972 * (10**24), (random.uniform(-9.9, 9.9)*10**10, random.uniform(-9.9, 9.9)*10**10), (1, 2)),

}"""
bodies = {}
"""
for i in range(3):
    bodies[str(i)] = Body(
        mass=(1*10**24),
        pos=(
            random.uniform(-9.9, 9.9) * 10**10,
            random.uniform(-9.9, 9.9) * 10**10
        ),
        vel=(1, 2)
    )
Universe.set_px_m_ratio_based_on_bodies(bodies)
bodies = {body.id: body for body in bodies.values()}
for body in bodies.values():
    body.update_radius_px()"""


### FUNCTIONS ###

def draw():
    Engine.screen.fill(Universe.universe_color)

    Universe.draw_axis(Engine.screen)

    for body in bodies.values():
        body.draw(Engine.screen)

    pygame.display.flip()


def calculations(time_interval):

    for body in bodies.values():

        overlaps = body.check_overlap_by_brute_force(bodies)

        if len(overlaps) > 1 and bodies[str(overlaps[1])] is not body:

            Body.inelastic_collision(bodies[str(overlaps[0])], bodies[str(overlaps[1])], 0.4)

        if body.id != selected_body:

            fx, fy = body.calculate_force(bodies)
            body.update_a_v_pos_based_on_force(fx, fy, time_interval*Universe.time_scale)
            # print(fx)

        body.update_px_based_on_pos()


global last_iteration_time
last_iteration_time = time.perf_counter()

### MAIN PYGAME LOOP ###

while True:

    for event in pygame.event.get():

        if event.type == pygame.MOUSEMOTION:
            if follow_mouse_body:  # si el selected_body esta seleccionado, cliqueado y se mueve el mouse, se lo mueve tambien siguiendo al mouse.
                bodies[selected_body].move(event.pos)

            if follow_mouse_camera[0]:  # actualizar la posicion de la camara
                if event.pos[0] < 0 or event.pos[0] > Engine.window_width or event.pos[1] < 0 or event.pos[1] > Engine.window_height:
                    continue
                Universe.camera_x += abs(event.pos[0])-follow_mouse_camera[1][0]
                Universe.camera_y += abs(event.pos[1])-follow_mouse_camera[1][1]

                follow_mouse_camera = (True, event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if not follow_mouse_body:  # chequea si un cuerpo se clickea y si guarda su id en selected_body para identificarlo despues
                    for body in bodies.values():
                        if body.is_clicked(event.pos):
                            selected_body = body.id
                            follow_mouse_body = True

            elif event.button == 2:
                Universe.camera_x = Engine.window_width/2
                Universe.camera_y = Engine.window_height/2

            elif event.button == 3:  # si se clickea con el boton derecho se habilita el movimiento de camara
                follow_mouse_camera = (True, event.pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if follow_mouse_body:
                    bodies[selected_body].vel_x, bodies[selected_body].vel_y = (0, 0)  # si se suelta el mouse, el cuerpo seleccionado se detiene y deja de seguir al mouse
                    selected_body = None
                    follow_mouse_body = False

            elif event.button == 3:  # si se suelta el boton derecho se deshabilita el movimiento de camara
                follow_mouse_camera = (False, None)

        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:  # Rueda hacia arriba
                Universe.zoom += Universe.zoom*0.05
            else:
                Universe.zoom -= Universe.zoom*0.05
            Universe.set_px_m_ratio_based_on_bodies(None, False)
            for body in bodies.values():
                body.update_radius_px()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_SPACE:
                bodies["new"] = Body(1*10**24, (100000000000, 100000000000), (0, 0))

                Universe.set_px_m_ratio_based_on_bodies(bodies)
                bodies["new"].x, bodies["new"].y = Universe.pixels_to_meters(pygame.mouse.get_pos())
                bodies = {body.id: body for body in bodies.values()}

                for body in bodies.values():
                    body.update_radius_px()

        elif event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    last_iteration_time = time.perf_counter() - last_iteration_time  # lets calculate preciosely the time between iterations to make the calculations more accurate

    calculations(last_iteration_time)  # calling the calculations main function

    draw()  # calling the draw main function

    Engine.timer.tick(Engine.fps)  # set the fps to the maximun possible
