# main.py
# The foundational script for the Untitled Gothic Horror Roguelike.
# This initial implementation focuses on creating a robust, doctrine-driven
# main menu system.

import pygame
import sys
from enum import Enum, auto
import json
import os
import math


# ==============================================================================
# I. Settings Manager (Principle: Preservation Axiom)
# ==============================================================================
class SettingsManager:
    """Manages loading and saving game settings to a JSON file."""

    def __init__(self):
        self.filepath = "gothic_rogue_settings.json"
        self.settings = self.load_settings()

    def load_settings(self):
        """Loads settings from the JSON file, or returns defaults."""
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r') as f:
                return json.load(f)
        return {
            "resolution_index": 0
        }

    def save_settings(self):
        """Saves the current settings to the JSON file."""
        with open(self.filepath, 'w') as f:
            json.dump(self.settings, f, indent=2)

    def get(self, key):
        return self.settings.get(key)

    def set(self, key, value):
        self.settings[key] = value


# ==============================================================================
# II. Configuration and Constants (Principle: Change-Resilient)
# ==============================================================================
settings_manager = SettingsManager()

resolutions = [(800, 600), (1024, 768), (1200, 900), (1600, 1200), (1920, 1080)]
current_resolution_index = settings_manager.get("resolution_index")
SCREEN_WIDTH, SCREEN_HEIGHT = resolutions[current_resolution_index]

INTERNAL_WIDTH, INTERNAL_HEIGHT = 800, 600

COLOR_NEAR_BLACK = (10, 10, 10)
COLOR_WHITE = (255, 255, 255)
COLOR_BLOOD_RED = (139, 0, 0)

FONT_NAME = 'Consolas'


# ==============================================================================
# III. State Management (Principle: Coherence)
# ==============================================================================
class GameState(Enum):
    QUIT = auto()
    MAIN_MENU = auto()
    OPTIONS_MENU = auto()
    GAME_RUNNING = auto()


# ==============================================================================
# IV. UI Classes (Principle: Modularity)
# ==============================================================================
class Button:
    """Represents a single, selectable button."""

    def __init__(self, y, text, font, action):
        self.rect = pygame.Rect(INTERNAL_WIDTH / 2 - 150, y, 300, 50)
        self.text = text
        self.font = font
        self.action = action
        self.is_selected = False

    def draw(self, surface):
        color = COLOR_BLOOD_RED if self.is_selected else COLOR_WHITE
        text_surface = self.font.render(self.text, True, color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)


class Menu:
    """Manages the main menu."""

    def __init__(self):
        self.title_font = pygame.font.Font(pygame.font.match_font(FONT_NAME), 50)
        self.button_font = pygame.font.Font(pygame.font.match_font(FONT_NAME), 30)

        self.buttons = [
            Button(250, "Start Game", self.button_font, GameState.GAME_RUNNING),
            Button(310, "Options", self.button_font, GameState.OPTIONS_MENU),
            Button(370, "Quit", self.button_font, GameState.QUIT)
        ]
        self.selected_index = 0
        self.buttons[self.selected_index].is_selected = True
        self.title_flicker_timer = 0.0

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.buttons[self.selected_index].is_selected = False
                self.selected_index = (self.selected_index - 1) % len(self.buttons)
                self.buttons[self.selected_index].is_selected = True
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.buttons[self.selected_index].is_selected = False
                self.selected_index = (self.selected_index + 1) % len(self.buttons)
                self.buttons[self.selected_index].is_selected = True
            elif event.key == pygame.K_RETURN:
                return self.buttons[self.selected_index].action
        return None

    def update(self, delta_time):
        self.title_flicker_timer += delta_time

    def draw(self, surface):
        flicker = 190 + 65 * math.sin(self.title_flicker_timer * 5)
        title_color = (int(flicker), int(flicker), int(flicker))

        title_text = "Gothic Rogue"
        title_surface = self.title_font.render(title_text, True, title_color)
        title_rect = title_surface.get_rect(center=(INTERNAL_WIDTH / 2, 150))
        surface.blit(title_surface, title_rect)

        for button in self.buttons:
            button.draw(surface)


class OptionsMenu:
    """Manages the options screen."""

    def __init__(self):
        self.title_font = pygame.font.Font(pygame.font.match_font(FONT_NAME), 40)
        self.button_font = pygame.font.Font(pygame.font.match_font(FONT_NAME), 28)

        self.buttons = []
        for i, (w, h) in enumerate(resolutions):
            action = {"type": "resolution", "index": i}
            button = Button(200 + i * 50, f"{w} x {h}", self.button_font, action)
            self.buttons.append(button)

        self.buttons.append(Button(200 + len(resolutions) * 50, "Back", self.button_font, {"type": "back"}))

        self.selected_index = 0
        self.buttons[self.selected_index].is_selected = True

    def update(self, delta_time):
        pass

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.buttons[self.selected_index].is_selected = False
                self.selected_index = (self.selected_index - 1) % len(self.buttons)
                self.buttons[self.selected_index].is_selected = True
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.buttons[self.selected_index].is_selected = False
                self.selected_index = (self.selected_index + 1) % len(self.buttons)
                self.buttons[self.selected_index].is_selected = True
            elif event.key == pygame.K_RETURN:
                return self.buttons[self.selected_index].action
        return None

    def draw(self, surface):
        title_surface = self.title_font.render("Screen Resolution", True, COLOR_WHITE)
        title_rect = title_surface.get_rect(center=(INTERNAL_WIDTH / 2, 100))
        surface.blit(title_surface, title_rect)

        for button in self.buttons:
            button.draw(surface)


# ==============================================================================
# V. Entity-Component System (ECS) (Principle: Modularity)
# ==============================================================================
class Component:
    """A base class for all components."""
    pass


class PositionComponent(Component):
    """Stores the x, y coordinates of an entity on the map."""

    def __init__(self, x, y):
        self.x = x
        self.y = y


class RenderComponent(Component):
    """Stores the visual representation of an entity."""

    def __init__(self, char, color):
        self.char = char
        self.color = color


class Entity:
    """A generic container for components."""

    def __init__(self):
        self.components = {}

    def add_component(self, component):
        self.components[type(component)] = component

    def get_component(self, component_type):
        return self.components.get(component_type)


# ==============================================================================
# VI. Main Game Class
# ==============================================================================
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.internal_surface = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))

        pygame.display.set_caption("Untitled Gothic Horror Roguelike")
        self.clock = pygame.time.Clock()
        self.game_state = GameState.MAIN_MENU

        self.menus = {
            GameState.MAIN_MENU: Menu(),
            GameState.OPTIONS_MENU: OptionsMenu()
        }
        self.game_font = pygame.font.Font(pygame.font.match_font(FONT_NAME), 16)

        # Player Creation
        self.player = Entity()
        self.player.add_component(PositionComponent(int(INTERNAL_WIDTH / 2), int(INTERNAL_HEIGHT / 2)))
        self.player.add_component(RenderComponent('@', COLOR_WHITE))

    def run(self):
        while self.game_state != GameState.QUIT:
            delta_time = self.clock.tick(60) / 1000.0

            self.handle_events()
            self.update(delta_time)
            self.draw()

        pygame.quit()
        sys.exit()

    def change_resolution(self, index):
        """Changes the window size and saves the setting."""
        global SCREEN_WIDTH, SCREEN_HEIGHT, current_resolution_index
        current_resolution_index = index
        SCREEN_WIDTH, SCREEN_HEIGHT = resolutions[current_resolution_index]
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        settings_manager.set("resolution_index", index)
        settings_manager.save_settings()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_state = GameState.QUIT
                return

            if self.game_state in self.menus:
                action = self.menus[self.game_state].handle_input(event)
                if action:
                    if isinstance(action, GameState):
                        self.game_state = action
                    elif isinstance(action, dict):
                        if action["type"] == "resolution":
                            self.change_resolution(action["index"])
                        elif action["type"] == "back":
                            self.game_state = GameState.MAIN_MENU

    def update(self, delta_time):
        if self.game_state in self.menus:
            self.menus[self.game_state].update(delta_time)

    def draw(self):
        self.internal_surface.fill(COLOR_NEAR_BLACK)

        if self.game_state in self.menus:
            self.menus[self.game_state].draw(self.internal_surface)
        elif self.game_state == GameState.GAME_RUNNING:
            # Render the player
            pos = self.player.get_component(PositionComponent)
            render = self.player.get_component(RenderComponent)
            if pos and render:
                text_surface = self.game_font.render(render.char, True, render.color)
                text_rect = text_surface.get_rect(center=(pos.x, pos.y))
                self.internal_surface.blit(text_surface, text_rect)

        scaled_surface = pygame.transform.scale(self.internal_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(scaled_surface, (0, 0))

        pygame.display.flip()


# ==============================================================================
# VII. Entry Point
# ==============================================================================
if __name__ == "__main__":
    game = Game()
    game.run()