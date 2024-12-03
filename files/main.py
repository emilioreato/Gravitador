### IMPORTACIÓN DE LIBRERIAS ###

from Body import Body
from Universe import Universe
from Engine import Engine
from UI import UI_MANAGER, Simulation_Ui, Help_Ui, Orbit_Mode_UI

import pygame
import sys
import time
import numpy as np
import webbrowser
import os


os.chdir(os.path.dirname(os.path.abspath(__file__)))  # establece el directorio de trabajo al del propio archivo main

### CONFIGURACIÓN ###

pygame.init()

# saludo de bienvenida
os.system('cls')  # limpiar la consola
print(">>>Bienvenido a Gravitum. ¡Experimenta!\n\n>Código fuente: https://github.com/emilioreato/Gravitum")


Engine.set_up()  # configuramos Engine q maneja todo lo de la ventana y pygame
ui_manager = UI_MANAGER()  # configuramos UI_MANAGER q maneja todo lo de la interfaz de usuario

ui_manager.load_resources()  # cargamos los recursos de la interfaz de usuario como imagenes y les damosun tamaño adecuado
ui_manager.resize()


### CREACIÓN DE VARIABLES DE EJECUCIÓN ###

global active_uis  # variable usada para almacenar el estado de los menus activos (ui)
active_uis = {
    "simulation": True,
    "help": False,
}

global pause_simulation  # var usada para pausar/ despausar simualcion
pause_simulation = False

global follow_mouse_body  # para saber si cuando el cuerpo tiene q trackear al mouse
follow_mouse_body = False
global follow_mouse_camera  # para saber si la camara tiene q trackear al mouse
follow_mouse_camera = (False, None)

global arrow_velocity_mode  # guarda datos para cuando se le de velocidad al cuerpo con la flecha
arrow_velocity_mode = (False, None)

global body_creation_mode  # guarda datos para cuando se esta creando un cuerpo
body_creation_mode = (False, None)

global selected_body  # alamcena el id del cuerpo que se ha seleccionado haciandole un click sobre el
selected_body = None

global already_created_a_body  # se usa para saber si alguna vez ya se ha creado algun cuerpo
already_created_a_body = False

global zoom_register  # guarda informacion de los zooms hechos para poder hacer un zoom acelerado
zoom_register = [0, time.time()]

global orbit_register
orbit_register = [False, None]
Orbit_Mode_UI.render()

global bodies  # variable mas importante q guarda todos los cuerpos activos en el sistema
bodies = {}

global collitions_history  # variable que guarda todo el historial de colisiones entre los cuerpos e info sobre eso asi dps se puede manejar las fusiones
collitions_history = {}


### FUNCIONES  ###


def draw():  # funcion principal de dibujar, se encarga de mostrar en pantalla todo lo necesario

    if active_uis["simulation"]:  # si estamos con la simulacion activa

        if UI_MANAGER.show_field:  # si esta activado el showfield, calculamos y mostramos el campo
            Universe.draw_field(bodies)
        else:
            Engine.screen.fill(Universe.universe_color)  # si no, simplemente pintamos el fondo de negro

        Universe.draw_axis_and_grid()  # dibujamos el eje de coordenadas y la grilla

        for body in bodies.values():  # dibujamos todos los cuerpos
            body.draw()

        if arrow_velocity_mode[0]:  # si estamos en modo de dar velocidad con la flecha, dibujamos la flecha y el texto de la velocidad
            Body.draw_arrow((bodies[arrow_velocity_mode[1]].x_px, bodies[arrow_velocity_mode[1]].y_px), pygame.mouse.get_pos())

        if body_creation_mode[0]:  # si estamos en modo de creacion de cuerpo, dibujamos el cuerpo que se esta creando y el texto de la masa
            Body.creation_draw(body_creation_mode[1], pygame.mouse.get_pos())

        if orbit_register[0]:
            Orbit_Mode_UI.draw()

        Simulation_Ui.draw()  # dibujamos la interfaz de usuario de la simulacion

    if active_uis["help"]:  # si estamos en el menu de ayuda, dibujamos la interfaz de usuario de la ayuda

        Help_Ui.draw()

    pygame.display.flip()  # actualizamos el frame, la pantalla.


def calculations(time_interval):  # funcion donde se realizan todos los calculos de posicion, velocidad, colisiones, etc.
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
                    if overlap_distance > 0:  # esto es para corregir la posicion y no dejar q esten uno encima del otro. se los pone pegados

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

        bodies["new"] = Body(position, vel, mass=mass)
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

# BUCLE PRINCIPAL DE PYGAME ### (se ejecuta tantas veces por segundo como fps tengas)

while True:

    for event in pygame.event.get():  # si ha ocurrido algun evento

        if event.type == pygame.MOUSEMOTION:  # si se ha movido el mouse

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

                smth_got_clicked = False

                for body in bodies.values():  # chequea entre todos los cuerpos si alguno fue clickeado y si es asi:
                    if body.is_clicked(event.pos):
                        selected_body = body.id  # se guarda su id en selected_body para identificarlo despues
                        smth_got_clicked = True

                if smth_got_clicked:

                    if orbit_register[0]:
                        if orbit_register[1] is None:
                            orbit_register[1] = selected_body

                        else:
                            vx, vy = Body.calculate_orbit_velocity(bodies, orbit_register[1], selected_body)

                            print(vx, vy)

                            bodies[selected_body].vel_x = vx
                            bodies[selected_body].vel_y = vy

                            orbit_register = [False, None]

                    else:
                        follow_mouse_body = True  # se activa el seguimiento de mouse para cuerpoo

                else:
                    if UI_MANAGER.check_ui_allowance(active_uis, UI_MANAGER.rects["help_btn"]) and UI_MANAGER.collidepoint(UI_MANAGER.rects["help_btn"]["rect"], event.pos):  # check if btn was clicked

                        active_uis["help"] = not active_uis["help"]
                        if active_uis["help"]:
                            pause_simulation = True
                        else:
                            pause_simulation = False

                    elif UI_MANAGER.check_ui_allowance(active_uis, UI_MANAGER.rects["github_btn"]) and UI_MANAGER.collidepoint(UI_MANAGER.rects["github_btn"]["rect"], event.pos):  # check if btn was clicked
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

                    radius, color = Body.creation_draw(body_creation_mode[1], event.pos, True)
                    x, y = Universe.pixels_to_meters(pygame.mouse.get_pos())
                    bodies["new"] = Body((x, y), (0, 0), color, reference_radius=radius)
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

        elif event.type == pygame.MOUSEWHEEL:  # si se ha movido la rueda del mouse
            if already_created_a_body:  # si ha se ha creado alguna vez un cuerpo con lo cual se setearon ciertas medidas (max_x, max_y , etc)

                current_time = time.time()

                if current_time - zoom_register[1] < 0.2:  # si han pasado menos de 0.3 segundos desde el ultimo zoom
                    zoom_register[0] += 1  # sumamos al multiplicador de la aceleracion
                else:

                    zoom_register[0] = 0  # reiniciamos el multiplcador

                zoom_register[1] = current_time  # actualizamos el tiempo del ultimo zoom

                mult = 0.025 + zoom_register[0] * 0.00375  # obtenemos un multiplicador basado en q tanto hemos scrolleado seguido

                if event.y > 0:  # si rueda hacia arriba
                    Universe.zoom += Universe.zoom*mult  # aumentamos el zoom en un valor aprox a 2+ aceleracion%
                else:
                    Universe.zoom -= Universe.zoom*mult  # sino lo reducimos en un valor aprox a 2 + aceleracion%

                Universe.set_px_m_ratio(None, False, pygame.mouse.get_pos())  # actualizamos la proporcion de pixeles_metros en base al nuevo zoom y a la posicion del mouse
                for body in bodies.values():  # actualizamos el radio de cada cuerpo en pixeles en base a la nueva proporcion px_m
                    body.update_radius_px()

        elif event.type == pygame.KEYDOWN:  # si se ha presiona una tecla
            if event.key == pygame.K_ESCAPE:  # si se presiona escape se cierra el programa
                pygame.quit()
                sys.exit()

            elif event.key == pygame.K_SPACE:  # si presionas el espacio se multiplica el time_scale por 4 asi va mas rapido
                Universe.time_scale = Universe.time_scale*4

            elif event.key == pygame.K_TAB:  # si presionas el tab se multiplica el time_scale por 18 asi va mas rapido
                Universe.time_scale = Universe.time_scale*18

            elif event.key == pygame.K_b:  # si presionas la b se invierte el time_scale asi va en reversa la simulacion
                Universe.time_scale = Universe.time_scale*-1

            elif event.key == pygame.K_c:  # centra la camara
                Universe.camera_x = Engine.window_width/2
                Universe.camera_y = Engine.window_height/2

            elif event.key == pygame.K_k:  # reinicia la simulacion. vuelve todo a cero.
                Universe.camera_x = Engine.window_width/2
                Universe.camera_y = Engine.window_height/2
                Universe.px_to_m_ratio = (60/30)
                Universe.zoom = 0.5
                bodies = {}

            elif event.key == pygame.K_p:  # pausa y despausa la simulacion
                pause_simulation = not pause_simulation

            elif event.key == pygame.K_a:  # si se presiona la g se activa/desactiva el muestreo de los ejes
                UI_MANAGER.show_axis = not UI_MANAGER.show_axis

            elif event.key == pygame.K_g:  # si se presiona la g se activa/desactiva el muestreo de las celdas
                UI_MANAGER.show_grid = not UI_MANAGER.show_grid

            elif event.key == pygame.K_d:  # si se presiona la d se activa/desactiva el muestreo de datos de los cuerpos en pantalla
                UI_MANAGER.show_details = not UI_MANAGER.show_details

            elif event.key == pygame.K_h:  # si se presiona la h abrimos el menu de ayuda
                active_uis["help"] = not active_uis["help"]
                if active_uis["help"]:  # si se entra al menu entonces pausamos la simulacion, sino la despausamos
                    pause_simulation = True
                else:
                    pause_simulation = False

            elif event.key == pygame.K_s:
                UI_MANAGER.show_circles = not UI_MANAGER.show_circles

            elif event.key == pygame.K_f:  # si se presiona la f se activa y desactiva el muestreo del campo. tambien se modifica el timescale para q no de apariencia de q va mas lento/rapido. esto es debido a q el procesamiendo para dibujar el campo relentiza todo
                UI_MANAGER.show_field = not UI_MANAGER.show_field
                if UI_MANAGER.show_field:
                    Universe.time_scale = Universe.time_scale*4
                else:
                    Universe.time_scale = Universe.time_scale/4

            elif event.key == pygame.K_t:  # cuando se presiona la tecla t se pasa a la siguiente combinancion de color para el campo.
                Universe.selected_field_color += 1  # la eleccion es esta variable q representa q posicion del arrray de combinaciones de colores en Universe.field_colors
                if Universe.selected_field_color > len(Universe.field_colors)-1:
                    Universe.selected_field_color = 0

            elif event.key == pygame.K_r:  # si presiona la r, en base a los cuerpos existentes recalcula el px_m_ratio y el zoom para que se vean todos los cuerpos en pantalla
                Universe.zoom = 0.75
                Universe.set_px_m_ratio(bodies, True)
                for body in bodies.values():  # actualizamos el radio de cada cuerpo en pixeles en base a la nueva proporcion px_m
                    body.update_radius_px()

            elif event.key == pygame.K_o:  # cuando se presiona la tecla se activa el modo orbita
                orbit_register[0] = not orbit_register[0]

        elif event.type == pygame.KEYUP:  # si se suelta una tecla
            if event.key == pygame.K_SPACE:  # si se suelta es espacio entonces restauremos el time_scale al antiguo
                Universe.time_scale = Universe.time_scale/4

            elif event.key == pygame.K_TAB:  # si se suelta es espacio entonces restauremos el time_scale al antiguo
                Universe.time_scale = Universe.time_scale/18

            elif event.key == pygame.K_b:  # si se suelta la b entonces restauremos el time_scale al antiguo
                Universe.time_scale = Universe.time_scale*-1

        elif event.type == pygame.QUIT:  # si se cierra la ventana salimos del programa
            pygame.quit()
            sys.exit()

    if not pause_simulation:  # si la simulacion no esta pausada
        calculations(time.perf_counter())  # llamando a la funcion de calculos principal

    draw()  # llamando a la funcion draw principal

    Engine.timer.tick(Engine.fps)  # ajustando fps
