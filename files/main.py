### IMPORTING MODULES ###

from Body import Body
from Universe import Universe
from Engine import Engine
from UI import UI_MANAGER, Simulation_Ui, Help_Ui
import pygame
import sys
import win32api
import time
import random
import numpy as np
import webbrowser
import os


os.chdir(os.path.dirname(os.path.abspath(__file__)))  # sets the current directory to the file's directory # noqa

pygame.init()


### SET UP###


Engine.set_up()
ui_manager = UI_MANAGER()

ui_manager.load_resoruces()
ui_manager.resize()


### PROGRAM VARIABLES ###

global active_uis
active_uis = {
    "simulation": True,
    "help": False,
}

global pause_simulation
pause_simulation = False

global follow_mouse_body
follow_mouse_body = False
global follow_mouse_camera
follow_mouse_camera = (False, None)

global body_creation_mode
body_creation_mode = (False, None)

global selected_body
selected_body = None


global bodies
bodies = {}


### FUNCTIONS ###

def check_ui_allowance(element_in_media_rect_list):

    use_in = element_in_media_rect_list["use_rect_in"]

    if type(use_in) == tuple:
        for possible_use in use_in:
            if active_uis[possible_use] == True:
                return True
    else:
        if use_in == "all" or active_uis[use_in] == True:
            return True
    return False


def collidepoint(rect, point_pos):
    if rect.collidepoint(point_pos):
        return True
    return False


def draw():
    # Engine.screen.fill(Universe.universe_color)

    if active_uis["simulation"]:

        Universe.draw_field(bodies)

        Universe.draw_axis()

        for body in bodies.values():
            body.draw()

        if body_creation_mode[0]:
            Body.creation_draw(body_creation_mode[1], event.pos)

        Simulation_Ui.draw()

    if active_uis["help"]:

        Help_Ui.draw()

    pygame.display.flip()


def calculations(time_interval):
    global selected_body, follow_mouse_body
    popit = False

    processed = []

    for body in bodies.values():

        if body.id in processed:
            continue

        overlaps = body.check_overlap_by_brute_force(bodies)

        if overlaps:

            print(overlaps)
            processed.append(overlaps[0])
            processed.append(body.id)

            """

            m1 = body.mass
            v1 = (body.vel_x, body.vel_y)
            m2 = bodies[str(overlaps[0])].mass  # masa del cuerpo 1
            v2 = (bodies[str(overlaps[0])].vel_x, bodies[str(overlaps[0])].vel_y)  # velocidad inicial del cuerpo 1

            e = 0.8               # coeficiente de restitución

            pos1 = (body.x, body.y)
            pos2 = (bodies[str(overlaps[0])].x, bodies[str(overlaps[0])].y)

            v1_final, v2_final = Body.inelastic_collision_2d(m1, v1, m2, v2, e, pos1, pos2)

            body.vel_x, body.vel_y = v1_final
            bodies[str(overlaps[0])].vel_x, bodies[str(overlaps[0])].vel_y = v2_final  

            overlap_distance = (body.radius + bodies[str(overlaps[0])].radius) - np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
            if overlap_distance > 0:
                correction = overlap_distance / 2
                direction = np.array([pos1[0] - pos2[0], pos1[1] - pos2[1]]) / np.linalg.norm([pos1[0] - pos2[0], pos1[1] - pos2[1]])
                body.x += correction * direction[0]
                body.y += correction * direction[1]
                bodies[str(overlaps[0])].x -= correction * direction[0]
                bodies[str(overlaps[0])].y -= correction * direction[1]"""

            mass = (body.mass + bodies[str(overlaps[0])].mass)*0.707

            position = (body.x+bodies[str(overlaps[0])].x)/2, (body.y+bodies[str(overlaps[0])].y)/2

            velocidadx = (body.vel_x * body.mass + bodies[str(overlaps[0])].vel_x * bodies[str(overlaps[0])].mass) / (body.mass + bodies[str(overlaps[0])].mass)
            velocidady = (body.vel_y * body.mass + bodies[str(overlaps[0])].vel_y * bodies[str(overlaps[0])].mass) / (body.mass + bodies[str(overlaps[0])].mass)
            vel = velocidadx, velocidady

            ids = body.id, overlaps[0]

            popit = True

            break

        if body.id != selected_body:

            fx, fy = body.calculate_force(bodies.values())
            body.update_a_v_pos_based_on_force(fx, fy, time_interval*Universe.time_scale)
            # print(fx)

        body.update_px_based_on_pos()

    if popit:

        bodies["new"] = Body(mass, position, vel)

        id = bodies["new"].id
        bodies[id] = bodies.pop("new")

        bodies.pop(ids[0])
        bodies.pop(ids[1])

        # Universe.set_px_m_ratio(bodies)

        selected_body = None
        follow_mouse_body = False

        for body in bodies.values():
            body.update_radius_px()
        pass


global last_iteration_time
last_iteration_time = time.perf_counter()

### MAIN PYGAME LOOP ###

while True:

    for event in pygame.event.get():

        if event.type == pygame.MOUSEMOTION:

            if follow_mouse_camera[0]:  # actualizar la posicion de la camara
                if event.pos[0] < 0 or event.pos[0] > Engine.window_width or event.pos[1] < 0 or event.pos[1] > Engine.window_height:  # si el mouse sale de la pantalla, no actualices
                    continue
                Universe.camera_x += abs(event.pos[0])-follow_mouse_camera[1][0]
                Universe.camera_y += abs(event.pos[1])-follow_mouse_camera[1][1]

                follow_mouse_camera = (True, event.pos)  # actualizar la posicion del mouse para la proxima iteracion asi se calcula en base a la dif entre esta iteracion

            elif follow_mouse_body:  # si el selected_body esta seleccionado, cliqueado y se mueve el mouse, se lo mueve tambien siguiendo al mouse.
                bodies[selected_body].move(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # si se cliquea el boton izq del mouse
                # if not follow_mouse_body:  # si ya no
                for body in bodies.values():  # chequea entre todos los cuerpos si alguno fue clickeado y si es asi:
                    if body.is_clicked(event.pos):
                        selected_body = body.id  # se guarda su id en selected_body para identificarlo despues
                        follow_mouse_body = True  # se activa el seguimiento de mouse para cuerpoo

                if check_ui_allowance(UI_MANAGER.rects["help_btn"]) and collidepoint(UI_MANAGER.rects["help_btn"]["rect"], event.pos):  # check if btn was clicked

                    active_uis["help"] = not active_uis["help"]
                    if active_uis["help"]:
                        pause_simulation = True
                    else:
                        pause_simulation = False

                elif check_ui_allowance(UI_MANAGER.rects["github_btn"]) and collidepoint(UI_MANAGER.rects["github_btn"]["rect"], event.pos):  # check if btn was clicked
                    webbrowser.open("https://github.com/emilioreato/Gravitum")

            elif event.button == 2:  # si se cliquea el boton del medio centramos la camara

                clicked_on_smth = False

                for body in bodies.values():  # chequea entre todos los cuerpos si alguno fue clickeado y si es asi:
                    if body.is_clicked(event.pos):
                        clicked_on_smth = True
                        selected_body = body.id

                if clicked_on_smth:
                    bodies.pop(selected_body)

                else:
                    body_creation_mode = (True, event.pos)

            elif event.button == 3:  # si se clickea con el boton derecho se habilita el movimiento de camara
                follow_mouse_camera = (True, event.pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # si se suelta el boton izq del mouse
                if follow_mouse_body:  # si veniamos siguiendo el movimiento del mouse para un cuerpo
                    bodies[selected_body].vel_x, bodies[selected_body].vel_y = (0, 0)  # el cuerpo seleccionado se detiene(velocidad en 0) y deja de seguir al mouse
                    selected_body = None  # ya no tenemos un objeto seleccionado
                    follow_mouse_body = False  # dejamos de seguir el mouse para el mov de un cuerpo

            elif event.button == 2:
                if body_creation_mode[0]:  # si veniamos creando un cuerpo

                    mass, color = Body.creation_draw(body_creation_mode[1], event.pos, True)
                    x, y = Universe.pixels_to_meters(pygame.mouse.get_pos())
                    bodies["new"] = Body(mass, (x, y), (0, 0), color)
                    id = bodies["new"].id
                    bodies[id] = bodies.pop("new")

                    if len(bodies) < 2:
                        Universe.set_px_m_ratio(bodies)

                    for body in bodies.values():
                        body.update_radius_px()

                    body_creation_mode = False, None

            elif event.button == 3:  # si se suelta el boton derecho se deshabilita el movimiento de camara
                follow_mouse_camera = (False, None)  # dejamos de seguir el movimiento del mouse para la camara

        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:  # si rueda hacia arriba
                Universe.zoom += Universe.zoom*0.06  # aumentamos el zoom en un 6%
            else:
                Universe.zoom -= Universe.zoom*0.06  # sino lo reducimos en un 6%
            Universe.set_px_m_ratio(None, False, pygame.mouse.get_pos())  # actualizamos la proporcion de pixeles_metros en base al nuevo zoom y a la posicion del mouse
            for body in bodies.values():  # actualizamos el radio de cada cuerpo en pixeles en base a la nueva proporcion px_m
                body.update_radius_px()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_SPACE:
                Universe.time_scale = Universe.time_scale*4  # si presionas el espacio se multiplica el time_scale por 4 asi va mas rapido

            elif event.key == pygame.K_c:
                Universe.camera_x = Engine.window_width/2
                Universe.camera_y = Engine.window_height/2

            elif event.key == pygame.K_k:
                Universe.camera_x = Engine.window_width/2
                Universe.camera_y = Engine.window_height/2

                bodies = {}

        elif event.type == pygame.KEYUP:  # si se suelta una tecla
            if event.key == pygame.K_SPACE:  # si se suelta es espacio entonces restauremos el time_scale al antiguo
                Universe.time_scale = Universe.time_scale/4

        elif event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    last_iteration_time = time.perf_counter() - last_iteration_time  # lets calculate preciosely the time between iterations to make the calculations more accurate

    if not pause_simulation:
        calculations(last_iteration_time)  # calling the calculations main function

    draw()  # calling the draw main function

    Engine.timer.tick(Engine.fps)  # set the fps to the maximun possible
