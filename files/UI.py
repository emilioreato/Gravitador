from Engine import Engine
import pygame


class UI_MANAGER:

    show_axis = True
    show_grid = True
    show_details = True
    show_circles = True
    show_field = True

    @staticmethod
    def load_resources():

        UI_MANAGER.metrics = {
            "help_btn": {"x": Engine.window_height//27, "y": Engine.window_height//25, "w": Engine.window_height//24, "h": Engine.window_height//24, "use_rect_in": "simulation"},
            "menu_ui": {"x": (Engine.window_width - (1920 / 1280) * Engine.window_height // 1.4) // 2, "y": (Engine.window_height - Engine.window_height // 1.4) // 2, "w": (1920/1280)*Engine.window_height//1.4, "h": Engine.window_height//1.4, "make_rect": False},
            "github_btn": {"x": Engine.window_height//1.04, "y": Engine.window_height//1.35, "w": (420/154)*Engine.window_height//16, "h": Engine.window_height//16, "use_rect_in": "help"},
        }

        UI_MANAGER.bare_imgs = {
            "help_btn": pygame.image.load("media\\help_btn.png").convert_alpha(),
            "menu_ui": pygame.image.load("media\\menu_ui.png").convert_alpha(),
            "github_btn": pygame.image.load("media\\github_btn.png").convert_alpha(),
        }

    @staticmethod
    def resize():

        UI_MANAGER.sized = {}
        for key in UI_MANAGER.bare_imgs.keys():
            UI_MANAGER.sized.update({key: UI_MANAGER.scale(UI_MANAGER.bare_imgs[key], UI_MANAGER.metrics[key]["w"], UI_MANAGER.metrics[key]["h"])})

        UI_MANAGER.rects = {}
        for key in UI_MANAGER.bare_imgs.keys():
            if not "make_rect" in UI_MANAGER.metrics[key].keys():
                UI_MANAGER.rects.update({key: {"rect": UI_MANAGER.sized[key].get_rect(), "use_rect_in": UI_MANAGER.metrics[key]["use_rect_in"]}})
                UI_MANAGER.rects[key]["rect"].topleft = (UI_MANAGER.metrics[key]["x"], UI_MANAGER.metrics[key]["y"])  # if "x" in Media.metrics[key].keys() else (0, 0)

    @staticmethod
    def scale(image, size_x, size_y):
        return pygame.transform.smoothscale(image, (size_x, size_y))

    def check_ui_allowance(active_uis, element_in_media_rect_list):

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


class Simulation_Ui:

    def draw():

        Engine.screen.blit(UI_MANAGER.sized["help_btn"], (UI_MANAGER.metrics["help_btn"]["x"], UI_MANAGER.metrics["help_btn"]["y"]))


class Orbit_Mode_UI:

    def render():
        Orbit_Mode_UI.text = Engine.font1.render(f"Seleccione un cuerpo con click izquierdo y luego otro más.", True, Engine.UI_COLORS[0])

    def draw():

        Engine.screen.blit(Orbit_Mode_UI.text, (Engine.window_width / 3.6, Engine.window_height / 25))


class Help_Ui:

    def draw():

        Engine.screen.blit(UI_MANAGER.sized["menu_ui"], (UI_MANAGER.metrics["menu_ui"]["x"], UI_MANAGER.metrics["menu_ui"]["y"]))

        Engine.screen.blit(UI_MANAGER.sized["github_btn"], (UI_MANAGER.metrics["github_btn"]["x"], UI_MANAGER.metrics["github_btn"]["y"]))
