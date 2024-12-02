### IMPORTING MODULES ###

from Body import Body
from Universe import Universe
from Engine import Engine
from UI import UI_MANAGER, Simulation_Ui, Help_Ui
import pygame
import sys
import time
import numpy as np
import webbrowser
import os


os.chdir(os.path.dirname(os.path.abspath(__file__)))  # sets the current directory to the file's directory # noqa

### SET UP###

pygame.init()

# saludo de bienvenida
os.system('cls')  # limpiar la consola
print(">>>Bienvenido a Gravitum. ¡Experimenta!\n\n>Código fuente: https://github.com/emilioreato/Gravitum")


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

global arrow_velocity_mode
arrow_velocity_mode = (False, None)

global body_creation_mode
body_creation_mode = (False, None)

global selected_body
selected_body = None

global already_created_a_body
already_created_a_body = False

global bodies
bodies = {}
global collitions_history
collitions_history = {}

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

    if active_uis["simulation"]:

        if UI_MANAGER.show_field:
            Universe.draw_field(bodies)
        else:
            Engine.screen.fill(Universe.universe_color)

        Universe.draw_axis()

        for body in bodies.values():
            body.draw()

        if arrow_velocity_mode[0]:
            Body.draw_arrow((bodies[arrow_velocity_mode[1]].x_px, bodies[arrow_velocity_mode[1]].y_px), pygame.mouse.get_pos())

        if body_creation_mode[0]:
            Body.creation_draw(body_creation_mode[1], event.pos)

        Simulation_Ui.draw()

    if active_uis["help"]:

        Help_Ui.draw()

    pygame.display.flip()


def calculations(time_interval):
    global selected_body, follow_mouse_body, arrow_velocity_mode
    delete_body = False

    processed = set()

    for body in bodies.values():

        if not body.id in processed:

            overlaps = body.check_overlap_by_brute_force(bodies)  # checkea si el cuerpo actual esta colisionando con algun otro cuerpo de la lista de cuerpos.

            if overlaps:  # ESTO SE EJECUTA SI HAY COLISIONES ENTRE CUERPOS

                m1 = body.mass

                processed.add(body.id)

                for body_overlaped_id in overlaps:

                    processed.add(body_overlaped_id)

                    v1 = (body.vel_x, body.vel_y)
                    m2 = bodies[body_overlaped_id].mass  # masa del cuerpo 1
                    v2 = (bodies[body_overlaped_id].vel_x, bodies[body_overlaped_id].vel_y)  # velocidad inicial del cuerpo 1

                    if v1[0]**2 + v1[1]**2 > v2[0]**2 + v2[1]**2:
                        biggest_vel = body.id
                    else:
                        biggest_vel = body_overlaped_id

                    overlap_distance = (body.radius + bodies[body_overlaped_id].radius) - np.sqrt((body.x - bodies[body_overlaped_id].x)**2 + (body.y - bodies[body_overlaped_id].y)**2)
                    if overlap_distance > 0:
                        # print("corrected")
                        direction = np.array([body.x - bodies[body_overlaped_id].x, body.y - bodies[body_overlaped_id].y]) / np.linalg.norm([body.x - bodies[body_overlaped_id].x, body.y - bodies[body_overlaped_id].y])
                        if biggest_vel == body.id:
                            body.x += overlap_distance * direction[0]
                            body.y += overlap_distance * direction[1]
                        else:
                            bodies[body_overlaped_id].x -= overlap_distance * direction[0]
                            bodies[body_overlaped_id].y -= overlap_distance * direction[1]

                    pos1 = (body.x, body.y)
                    pos2 = (bodies[body_overlaped_id].x, bodies[body_overlaped_id].y)

                    v1_final, v2_final = Body.inelastic_collision_2d(m1, v1, m2, v2, pos1, pos2)

                    body.vel_x, body.vel_y = v1_final
                    bodies[body_overlaped_id].vel_x, bodies[body_overlaped_id].vel_y = v2_final

                    # las siguientes lineas se usan para llevar un registro de las colisiones y el momento en que ocurrieron, para luego analizar si una colision volvio a ocurrir menos de 0.3 segundos despues de la anterior, y en caso de que sea asi, sumar a un conteo q si llega a 10 se fusionan los cuerpos. si el tiempo es mayor a esos 0.3 entonces se reinicia el timer

                    fuse = False
                    index = None

                    if body.id + body_overlaped_id in collitions_history:  # como depende de q cuerpo se analice primero puede estar registrada de dos maneras. str(body.id + body_overlaped_id) o invertido str(body_overlaped_id + body.id). por eso se checkea ambas opciones
                        index = body.id + body_overlaped_id
                    elif body_overlaped_id + body.id in collitions_history:
                        index = body_overlaped_id + body.id
                    else:  # si la colision no fue registrada, la registramos por primera vez, con tiempo actual y conteo de choques 0
                        collitions_history[body_overlaped_id + body.id] = [time.time(), 0]

                    if index != None:  # si esta registrada

                        if time.time() - collitions_history[index][0] < 0.4:  # si la ultima colision fue hace menos de 0.5 segundos
                            collitions_history[index][1] += 1  # sumamos a un contador de colisiones "continuas"
                            if collitions_history[index][1] > 20:  # si llevamos mas de 20 continuas vamos a eliminar el registro de las colisiones de estos dos cuerpos porque prontamente los fusionaremos
                                fuse = True

                        else:  # si la ultima colision fue hace mas de 0.5 segundos entonces reinicamos el contador de colisiones continuas y volvermos a contar
                            collitions_history[index][1] = 0
                        collitions_history[index][0] = time.time()  # volvemos a contar 0.5 segundos desde ahora para la proxima colision

                    if fuse:

                        collitions_history.pop(index)

                        mass = body.mass + bodies[body_overlaped_id].mass

                        largest_body = max((body, bodies[body_overlaped_id]), key=lambda body: body.mass)
                        position = (largest_body.x, largest_body.y)  # Creamos una nueva posición igual a la del cuerpo más masivo

                        velocidadx = (body.vel_x * body.mass + bodies[body_overlaped_id].vel_x * bodies[body_overlaped_id].mass) / (body.mass + bodies[body_overlaped_id].mass)
                        velocidady = (body.vel_y * body.mass + bodies[body_overlaped_id].vel_y * bodies[body_overlaped_id].mass) / (body.mass + bodies[body_overlaped_id].mass)
                        vel = velocidadx, velocidady

                        ids = body.id, body_overlaped_id

                        delete_body = True

                        break

        if not follow_mouse_body or body.id != selected_body:  # solo actualizamos la posicion del cuerpo basada en la atraccion grav q siente si no es el cuerpo seleccionado (no esta siendo movido con el mouse)
            fx, fy = body.calculate_force(bodies.values())
            body.update_a_v_based_on_force(fx, fy, time_interval*Universe.time_scale)
            body.update_pos_based_on_vel(time_interval*Universe.time_scale)

    if delete_body:  # mas q eliminar un cuerpo lo que hacemos es eliminar los dos pero crear otro q tenga la suma de masa de los dos y la posicion dle mas grande, etc

        bodies["new"] = Body(mass, position, vel)
        bodies["new"].x_px, bodies["new"].y_px = Universe.meters_to_pixels(position)
        bodies["new"].update_radius_px()

        id = bodies["new"].id
        bodies[id] = bodies.pop("new")

        bodies.pop(ids[0])
        bodies.pop(ids[1])

        if arrow_velocity_mode[0]:  # si estabamos modificando la velocidad de un cuerpo con el modo flecha, entonces actualizamos el id y selected body para q empiece a modificar el nuevo
            arrow_velocity_mode = (True, id)  # se desactiva el modo flechas si venia activado
            selected_body = id
        else:
            if selected_body in ids:  # si el cuerpo seleccionado es alguno de los q que se borro, entonces deseleccionamos el cuerpo seleccionado
                selected_body = None
                follow_mouse_body = False


time.perf_counter()

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

                if arrow_velocity_mode[0]:
                    arrow_velocity_mode = (False, None)

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

                if arrow_velocity_mode[0]:
                    arrow_velocity_mode = (False, None)

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

                clicked_on_smth = False
                for body in bodies.values():  # chequea entre todos los cuerpos si alguno fue clickeado y si es asi:
                    if body.is_clicked(event.pos):
                        clicked_on_smth = True
                        selected_body = body.id

                if len(bodies) > 0 and clicked_on_smth:  # si hay mas de un cuerpo y se clickeo en alguno, se habilita el modo flechas
                    arrow_velocity_mode = (True, selected_body)
                else:
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

                    if not already_created_a_body:
                        already_created_a_body = True
                        Universe.set_px_m_ratio(bodies)

                    for body in bodies.values():
                        body.update_radius_px()

                    body_creation_mode = False, None

            elif event.button == 3:  # si se suelta el boton derecho

                if arrow_velocity_mode[0]:  # si el modo flecha estaba activado

                    new_pos = Universe.pixels_to_meters(event.pos)
                    pre_pos = Universe.pixels_to_meters((bodies[arrow_velocity_mode[1]].x_px, bodies[arrow_velocity_mode[1]].y_px))

                    bodies[selected_body].vel_x, bodies[selected_body].vel_y = (new_pos[0]-pre_pos[0])*Universe.arrow_vel_mult, (new_pos[1]-pre_pos[1])*Universe.arrow_vel_mult

                    arrow_velocity_mode = (False, None)

                else:  # se deshabilita el movimiento de camara
                    follow_mouse_camera = (False, None)  # dejamos de seguir el movimiento del mouse para la camara

        elif event.type == pygame.MOUSEWHEEL:
            if already_created_a_body:  # si hay al menos un cuerpo en pantalla
                if event.y > 0:  # si rueda hacia arriba
                    Universe.zoom += Universe.zoom*0.035  # aumentamos el zoom en un 4%
                else:
                    Universe.zoom -= Universe.zoom*0.035  # sino lo reducimos en un 4%
                Universe.set_px_m_ratio(None, False, pygame.mouse.get_pos())  # actualizamos la proporcion de pixeles_metros en base al nuevo zoom y a la posicion del mouse
                for body in bodies.values():  # actualizamos el radio de cada cuerpo en pixeles en base a la nueva proporcion px_m
                    body.update_radius_px()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # cierra el programa
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_SPACE:
                Universe.time_scale = Universe.time_scale*4  # si presionas el espacio se multiplica el time_scale por 4 asi va mas rapido
            elif event.key == pygame.K_b:
                Universe.time_scale = Universe.time_scale*-1  # si presionas la b se invierte el time_scale asi va en reversa la simulacion
            elif event.key == pygame.K_c:  # centra la camara
                Universe.camera_x = Engine.window_width/2
                Universe.camera_y = Engine.window_height/2
            elif event.key == pygame.K_k:  # reinicia la simulacion en pocas palabras
                Universe.camera_x = Engine.window_width/2
                Universe.camera_y = Engine.window_height/2
                Universe.px_to_m_ratio = (60/30)
                Universe.zoom = 0.5
                bodies = {}
            elif event.key == pygame.K_p:  # pausa y despausa la simulacion
                pause_simulation = not pause_simulation
            elif event.key == pygame.K_a:
                UI_MANAGER.show_axis = not UI_MANAGER.show_axis
            elif event.key == pygame.K_g:
                UI_MANAGER.show_grid = not UI_MANAGER.show_grid
            elif event.key == pygame.K_d:
                UI_MANAGER.show_details = not UI_MANAGER.show_details
            elif event.key == pygame.K_h:
                active_uis["help"] = not active_uis["help"]
                if active_uis["help"]:
                    pause_simulation = True
                else:
                    pause_simulation = False
            elif event.key == pygame.K_s:
                UI_MANAGER.show_circles = not UI_MANAGER.show_circles
            elif event.key == pygame.K_f:
                UI_MANAGER.show_field = not UI_MANAGER.show_field
                if UI_MANAGER.show_field:
                    Universe.time_scale = Universe.time_scale*3
                else:
                    Universe.time_scale = Universe.time_scale/3

            elif event.key == pygame.K_r:  # en base a los cuerpos existentes recalcula el px_m_ratio y el zoom para que se vean todos los cuerpos en pantalla
                Universe.zoom = 0.75
                Universe.set_px_m_ratio(bodies, True)
                for body in bodies.values():  # actualizamos el radio de cada cuerpo en pixeles en base a la nueva proporcion px_m
                    body.update_radius_px()

        elif event.type == pygame.KEYUP:  # si se suelta una tecla
            if event.key == pygame.K_SPACE:  # si se suelta es espacio entonces restauremos el time_scale al antiguo
                Universe.time_scale = Universe.time_scale/4
            elif event.key == pygame.K_b:  # si se suelta la b entonces restauremos el time_scale al antiguo
                Universe.time_scale = Universe.time_scale*-1

        elif event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if not pause_simulation:
        calculations(time.perf_counter())  # llamando a la funcion de calculos principal

    draw()  # llamando a la funcion draw principal

    Engine.timer.tick(Engine.fps)  # ajustando fps
