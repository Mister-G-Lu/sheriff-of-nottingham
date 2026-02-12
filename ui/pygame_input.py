"""
Pygame Input Handling
Handles user input, choice buttons, and text entry
"""

import sys
from typing import Optional

import pygame

from ui.pygame_window import TEXT_BOX_HEIGHT, TEXT_BOX_X, TEXT_BOX_Y

# Import constants
from ui.ui_constants import (
    DARK_GRAY,
    DARK_GREEN,
    FONT_SIZE_NORMAL,
    GRAY,
    GREEN,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WHITE,
)


class PygameInput:
    """Handles user input including text entry and choice buttons"""

    def __init__(self, window, text_display, price_menu=None):
        self.window = window
        self.text_display = text_display
        self.price_menu = price_menu

        # Input state
        self.input_prompt: Optional[str] = None
        self.user_input: str = ""
        self.waiting_for_input: bool = False
        self.input_submitted: bool = False
        self.choice_buttons: list[tuple[str, pygame.Rect]] = []

    def get_input(self, prompt: str = "") -> str:
        """Get text input from the user"""
        self.input_prompt = prompt
        self.user_input = ""
        self.waiting_for_input = True
        self.input_submitted = False

        self._render_with_input()

        while not self.input_submitted:
            self.window.clock.tick(60)  # 60 FPS

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Handle scrolling while waiting for input
                if event.type == pygame.MOUSEWHEEL:
                    self.text_display._handle_scroll(event.y)

                # Handle price menu clicks
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.price_menu and self.price_menu.handle_click(mouse_pos):
                        self._render_with_input()  # Re-render to show/hide menu

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # Submit input
                        self.input_submitted = True
                    elif event.key == pygame.K_BACKSPACE:
                        # Delete last character
                        self.user_input = self.user_input[:-1]
                    else:
                        # Add character to input
                        if event.unicode.isprintable():
                            self.user_input += event.unicode

                    self._render_with_input()

        self.waiting_for_input = False
        result = self.user_input.strip()

        # Display the submitted input in the text box
        self.text_display.display_text(
            f"> {result}", clear_previous=False, animate=False
        )

        return result

    def show_choices(self, prompt: str, choices: list[tuple[str, str]]) -> str:
        """
        Show multiple choice buttons and return the selected choice key
        choices: List of (key, display_text) tuples
        """
        if prompt:
            self.text_display.display_text(prompt, clear_previous=False, animate=False)

        # Create button rectangles - centered at bottom of screen
        self.choice_buttons = []
        button_width = 220
        button_height = 50
        button_spacing = 20

        # Calculate total width needed
        total_width = len(choices) * button_width + (len(choices) - 1) * button_spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = SCREEN_HEIGHT - button_height - 30

        for i, (_key, display_text) in enumerate(choices):
            x = start_x + i * (button_width + button_spacing)
            rect = pygame.Rect(x, start_y, button_width, button_height)
            self.choice_buttons.append((display_text, rect))

        self._render_with_buttons()

        # Wait for button click
        selected = None
        last_hover_button = None

        while selected is None:
            self.window.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Ignore scroll events when showing choice buttons
                # (no text to scroll on menu screen)
                if event.type == pygame.MOUSEWHEEL:
                    # Only allow scrolling if there's actual text content to scroll
                    # Check if we have more text lines than can fit in the display
                    max_lines = (TEXT_BOX_HEIGHT - 40) // (FONT_SIZE_NORMAL + 5)
                    if len(self.text_display.text_lines) > max_lines:
                        self.text_display._handle_scroll(event.y)
                    # Otherwise, ignore the scroll event

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    # Check if price menu button was clicked
                    if self.price_menu and self.price_menu.handle_click(mouse_pos):
                        self._render_with_buttons()  # Re-render to show/hide menu
                        continue

                    # Check if choice button was clicked
                    for i, (_choice_text, rect) in enumerate(self.choice_buttons):
                        if rect.collidepoint(mouse_pos):
                            selected = choices[i][0]
                            break

                if event.type == pygame.MOUSEMOTION:
                    # Only re-render if hover state changed
                    mouse_pos = pygame.mouse.get_pos()
                    current_hover = None
                    for i, (_choice_text, rect) in enumerate(self.choice_buttons):
                        if rect.collidepoint(mouse_pos):
                            current_hover = i
                            break

                    if current_hover != last_hover_button:
                        last_hover_button = current_hover
                        self._render_with_buttons()

        # Clear buttons and show selected choice
        self.choice_buttons = []
        selected_display = next(text for key, text in choices if key == selected)
        self.text_display.display_text(
            f"> {selected_display}", clear_previous=False, animate=False
        )

        return selected

    def wait_for_continue(self):
        """Wait for user to press any key or click to continue"""
        waiting = True

        # Show continue prompt in the UI
        self.text_display.display_text("", clear_previous=False, animate=False)
        self.text_display.display_text(
            "[Click anywhere or press any key to continue]",
            clear_previous=False,
            animate=False,
        )

        while waiting:
            self.window.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    # Check if price menu button was clicked
                    if self.price_menu and self.price_menu.handle_click(mouse_pos):
                        self.text_display.render()  # Re-render to show/hide menu
                        if self.price_menu:
                            self.price_menu.render()
                        self.window.update_display()
                        continue
                    # Otherwise, continue
                    waiting = False
                    break

                if event.type == pygame.KEYDOWN:
                    waiting = False
                    break

        # Clear the screen for next section
        self.text_display.clear_text()

    def _render_with_input(self):
        """Render the UI with text input prompt"""
        # Use text display's render method
        self.text_display.render()

        # Render input prompt and user input if waiting for input
        if self.waiting_for_input and self.input_prompt:
            y_offset = TEXT_BOX_Y + 20
            max_lines = (TEXT_BOX_HEIGHT - 40) // (FONT_SIZE_NORMAL + 5)

            # Calculate where to show input (after visible text)
            visible_lines = len(
                self.text_display.text_lines[self.text_display.text_scroll_offset :]
            )
            visible_lines = min(visible_lines, max_lines)
            y_offset += visible_lines * (FONT_SIZE_NORMAL + 5)

            if y_offset + 70 < TEXT_BOX_Y + TEXT_BOX_HEIGHT:
                prompt_surface = self.window.font_normal.render(
                    self.input_prompt, True, GREEN
                )
                self.window.screen.blit(
                    prompt_surface, (TEXT_BOX_X + 20, y_offset + 10)
                )

                # Render user input with cursor
                input_text = self.user_input + "_"
                input_surface = self.window.font_normal.render(input_text, True, WHITE)
                self.window.screen.blit(input_surface, (TEXT_BOX_X + 20, y_offset + 40))

        self.window.update_display()

    def _render_with_buttons(self):
        """Render the UI with choice buttons"""
        # Don't clear screen if text display is empty (preserve title screen)
        if self.text_display.text_lines:
            # Use text display's render method
            self.text_display.render()

        # Render choice buttons
        mouse_pos = pygame.mouse.get_pos()

        for _i, (choice_text, rect) in enumerate(self.choice_buttons):
            # Check if mouse is hovering
            is_hover = rect.collidepoint(mouse_pos)

            # Draw button
            button_color = DARK_GREEN if is_hover else DARK_GRAY
            pygame.draw.rect(self.window.screen, button_color, rect)
            pygame.draw.rect(self.window.screen, GREEN if is_hover else GRAY, rect, 2)

            # Draw button text
            text_surface = self.window.font_normal.render(choice_text, True, WHITE)
            text_rect = text_surface.get_rect(center=rect.center)
            self.window.screen.blit(text_surface, text_rect)

        self.window.update_display()
