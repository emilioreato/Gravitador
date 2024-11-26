from Engine import Engine
import pygame


class UI_MANAGER:

    @staticmethod
    def load_resoruces():

        UI_MANAGER.metrics = {
            "help_btn": {"x": Engine.window_height//27, "y": Engine.window_height//21, "w": Engine.window_height//24, "h": Engine.window_height//24, "use_rect_in": "simulation"},
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


class Simulation_Ui:

    def draw():

        Engine.screen.blit(UI_MANAGER.sized["help_btn"], (UI_MANAGER.metrics["help_btn"]["x"], UI_MANAGER.metrics["help_btn"]["y"]))


class Help_Ui:

    def draw():

        Engine.screen.blit(UI_MANAGER.sized["menu_ui"], (UI_MANAGER.metrics["menu_ui"]["x"], UI_MANAGER.metrics["menu_ui"]["y"]))

        Engine.screen.blit(UI_MANAGER.sized["github_btn"], (UI_MANAGER.metrics["github_btn"]["x"], UI_MANAGER.metrics["github_btn"]["y"]))