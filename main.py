# main.py
# The foundational script for the Untitled Gothic Horror Roguelike.
# This initial implementation focuses on creating a robust, doctrine-driven
# main menu system.

import pygame
import sys
from enum import Enum, auto

# ==============================================================================
# I. Configuration and Constants (Principle: Change-Resilient)
# Centralized constants for easy modification of the game's appearance.
# ==============================================================================

# Screen Dimensions
# These are dynamic resolutions to accommodate larger screen sizes
resolutions = [(800, 600), (1024, 768), (1200, 900), (1600, 1200), (1920, 1080)]
current_resolution_index = 0
SCREEN_WIDTH, SCREEN_HEIGHT = resolutions[current_resolution_index]

# Internal Surface
# For consistent rendering and easy scaling
INTERNAL_WIDTH, INTERNAL_HEIGHT = 800, 600

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_NEAR_BLACK = (10, 10, 10)
COLOR_SLATE_GREY = (47, 79, 79)
COLOR_LIGHT_SLATE_GREY = (119, 136, 153)
COLOR_WHITE = (255, 255, 255)
COLOR_BLOOD_RED = (139, 0, 0)

# Fonts
FONT_NAME = 'Consolas'


# ==============================================================================
# II. State Management (Principle: Coherence)
# An Enum to manage the high-level state of the game.
# ==============================================================================
class GameState(Enum):
    QUIT = auto()
    MAIN_MENU = auto()
    OPTIONS_MENU = auto()
    GAME_RUNNING = auto()  # Placeholder for now


# ==============================================================================
# III. UI Classes (Principle: Modularity)
# Self-contained classes for different UI elements and menus.
# ==============================================================================
class Button:
    """Represents a single, selectable button."""

    def __init__(self, y, text, font, action):
        # We adjust the rect to be relative to the internal surface size
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
        title_text = "Gothic Rogue"
        title_surface = self.title_font.render(title_text, True, COLOR_WHITE)
        title_rect = title_surface.get_rect(center=(INTERNAL_WIDTH / 2, 150))
        surface.blit(title_surface, title_rect)

        for button in self.buttons:
            button.draw(surface)


class OptionsMenu:
    """Manages the options screen for changing game settings like resolution."""

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
# IV. Main Game Class (Principle: The craft of writing code)
# This is the central hub. It manages the main loop and transitions
# between different game states based on user actions.
# ==============================================================================
class Game:
    def __init__(self):
        global SCREEN_WIDTH, SCREEN_HEIGHT
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.internal_surface = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))

        pygame.display.set_caption("Untitled Gothic Horror Roguelike")
        self.clock = pygame.time.Clock()
        self.game_state = GameState.MAIN_MENU

        self.menu = Menu()
        self.options_menu = OptionsMenu()

    def run(self):
        while self.game_state != GameState.QUIT:
            self.handle_events()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

    def change_resolution(self, index):
        """Changes the window size."""
        global SCREEN_WIDTH, SCREEN_HEIGHT, current_resolution_index
        current_resolution_index = index
        SCREEN_WIDTH, SCREEN_HEIGHT = resolutions[current_resolution_index]
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_state = GameState.QUIT

            if self.game_state == GameState.MAIN_MENU:
                action = self.menu.handle_input(event)
                if action:
                    self.game_state = action

            elif self.game_state == GameState.OPTIONS_MENU:
                action = self.options_menu.handle_input(event)
                if action:
                    if action["type"] == "resolution":
                        self.change_resolution(action["index"])
                    elif action["type"] == "back":
                        self.game_state = GameState.MAIN_MENU

    def draw(self):
        self.internal_surface.fill(COLOR_NEAR_BLACK)

        if self.game_state == GameState.MAIN_MENU:
            self.menu.draw(self.internal_surface)
        elif self.game_state == GameState.OPTIONS_MENU:
            self.options_menu.draw(self.internal_surface)

        scaled_surface = pygame.transform.scale(self.internal_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(scaled_surface, (0, 0))

        pygame.display.flip()


# ==============================================================================
# V. Entry Point
# ==============================================================================
if __name__ == "__main__":
    game = Game()
    game.run()