"""
Wall Display: Interactive digital signage system using pygame.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

import sys
import csv
import logging
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional, Any
import pygame

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


@dataclass
class MenuItem:
    """
    Represents a menu category and its associated images for Wall Display.
    """

    id: int
    directory: Path
    menu_name: str
    description: str
    images: List[Tuple[str, pygame.Surface, pygame.Surface]] = field(
        default_factory=list
    )
    menu_surface: Optional[pygame.Surface] = None


class WallDisplayApp:
    """
    Main application class for the Wall Display program.
    Handles UI rendering, data loading, and event processing logic.
    """

    # Constants
    MENU_WIDTH = 205
    AUTO_FRAME_DELAY_MS = 15000  # 15 seconds
    AUTO_START_DELAY_MS = 20000  # 20 seconds
    FONT_COLOR_ACTIVE = (255, 255, 255)
    FONT_COLOR_INACTIVE = (150, 150, 150)
    BG_COLOR = (0, 0, 0)

    def __init__(self, menu_data_dir: str = "menu-data"):
        """
        Initializes the application, Pygame, and display settings.

        Args:
            menu_data_dir (str): Path to the directory containing menu.data and images.
        """
        pygame.init()
        pygame.mouse.set_visible(False)

        # UI Layout
        self.disp_info = pygame.display.Info()
        self.disp_w = self.disp_info.current_w
        self.disp_h = self.disp_info.current_h
        self.menu_height = self.disp_h

        # State
        self.screen: Optional[pygame.Surface] = None
        self.menu_data_path = Path(menu_data_dir)
        self.verbose_line_y = 0
        self.menu_items: List[MenuItem] = []
        self.current_item_index = 0
        self.auto_image_list: List[Tuple[str, pygame.Surface, pygame.Surface]] = []
        self.right_frame_previous: Optional[pygame.Surface] = None

        self.current_item = None  # Ensure attribute is always defined in __init__
        self._setup_display()

    def _setup_display(self) -> None:
        """Sets up the display surface and loads initial data."""
        try:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self._verbose_msg(f"Initializing display: ({self.disp_w}x{self.disp_h})")

            self.menu_items = self._load_menu()
            if not self.menu_items:
                logging.error("No menu items loaded.")
                sys.exit(0)

            # Initialize state with first item
            self.current_item = self.menu_items[0]
            self.auto_image_list = self.current_item.images

            if self.auto_image_list:
                self.right_frame_previous = self.auto_image_list[0][2]

        except pygame.error as e:
            self._fatal_error(1, f"Pygame initialization failed: {e}")
        except (IOError, ValueError, KeyError) as e:
            self._fatal_error(
                1, f"Unexpected error during setup: {e.__class__.__name__}: {e}"
            )

        self._clear_verbose_screen()
        self._draw_menu()
        self._start_auto_timer()

    def _verbose_msg(self, msg: str) -> None:
        """Renders a status message directly to the screen during loading."""
        logging.info(msg)
        if not self.screen:
            return

        font = pygame.font.Font(None, 32)
        font_height = font.get_height()
        surface = font.render(msg, True, (50, 50, 50))

        self.screen.blit(surface, (10, self.verbose_line_y))
        self.verbose_line_y += font_height
        pygame.display.flip()

    def _clear_verbose_screen(self) -> None:
        """Clears the loading/verbose text."""
        self.verbose_line_y = 0
        background = pygame.Surface(self.screen.get_size()).convert()
        background.fill(self.BG_COLOR)
        self.screen.blit(background, (0, 0))

    def _fatal_error(self, status: int, msg: str) -> None:
        """Logs a fatal error and exits the application."""
        logging.critical(msg)
        pygame.quit()
        sys.exit(status)

    def _draw_menu(self) -> None:
        """Draws the current menu sidebar."""
        current = self.menu_items[self.current_item_index]
        if current.menu_surface:
            self.screen.blit(current.menu_surface, (0, 0))
            pygame.display.flip()

    def _load_menu_data_file(self) -> List[Dict[str, Any]]:
        """Parses the menu.data CSV file."""
        file_path = self.menu_data_path / "menu.data"
        entries = []

        if not file_path.exists():
            self._fatal_error(1, f"Menu data file not found: {file_path}")

        try:
            with file_path.open("r", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter=":")
                for row in reader:
                    # Format: ID:DIR:ENABLED:NAME:DESC
                    if len(row) > 3 and int(row[2]) == 1:
                        entries.append(
                            {
                                "id": int(row[0].strip()),
                                "dir": row[1].strip(),
                                "name": row[3].strip(),
                                "desc": row[4].strip() if len(row) > 4 else "",
                            }
                        )
        except IOError as e:
            self._fatal_error(1, f"Could not read menu file: {e}")

        return entries

    def _load_menu(self) -> List[MenuItem]:
        """Loads images and generates surfaces for all menu items."""
        self._verbose_msg("Loading menu configuration...")
        raw_data = self._load_menu_data_file()

        loaded_items = []

        for entry in raw_data:
            self._verbose_msg(f"Processing category: {entry['name']}")

            # Resolve image directory relative to menu_data_path
            img_dir = self.menu_data_path / entry["dir"]
            images = self._load_images_from_dir(img_dir)

            menu_item = MenuItem(
                id=entry["id"],
                directory=img_dir,
                menu_name=entry["name"],
                description=entry["desc"],
                images=images,
            )

            # Pre-render the menu sidebar for this state
            menu_item.menu_surface = self._generate_menu_surface(entry["id"], raw_data)
            loaded_items.append(menu_item)

        self._verbose_msg("Loading complete.")
        return loaded_items

    def _generate_menu_surface(
        self, active_id: int, all_entries: List[Dict]
    ) -> pygame.Surface:
        """Generates the static sidebar surface for a specific active state."""
        surface = pygame.Surface((self.MENU_WIDTH, self.menu_height)).convert()
        surface.fill(self.BG_COLOR)

        font = pygame.font.SysFont("gillsansmt", 20, bold=False)
        font_height = font.get_height()

        y_pos = 40
        left_margin = 10
        vertical_padding = 40

        for entry in all_entries:
            color = (
                self.FONT_COLOR_ACTIVE
                if entry["id"] == active_id
                else self.FONT_COLOR_INACTIVE
            )
            text_surf = font.render(entry["name"], True, color)
            surface.blit(text_surf, (left_margin, y_pos))
            y_pos += font_height + vertical_padding

        return surface

    def _load_images_from_dir(
        self, directory: Path
    ) -> List[Tuple[str, pygame.Surface, pygame.Surface]]:
        """Loads valid JPG images from a directory."""
        img_list = []
        if not directory.exists():
            logging.warning("Directory not found: %s", directory)
            return img_list

        files = sorted(
            [f for f in directory.iterdir() if f.suffix.lower() in (".jpg", ".jpeg")]
        )

        for file_path in files:
            try:
                img = pygame.image.load(str(file_path)).convert()
                background = pygame.Surface(img.get_size()).convert()
                background.blit(img, (0, 0))
                img_list.append((file_path.name, img, background))
            except pygame.error:
                logging.warning("Skipping invalid image: %s", file_path.name)

        return img_list

    def _fade_transition(
        self, img_surface: pygame.Surface, fade_in: bool = True
    ) -> None:
        """Handles fade in/out animations."""
        alpha_range = range(0, 255, 25) if fade_in else range(255, -1, -25)

        for alpha in alpha_range:
            bg = pygame.Surface(self.screen.get_size()).convert()
            bg.fill(self.BG_COLOR)

            img_surface.set_alpha(alpha)
            self.screen.blit(img_surface, (self.MENU_WIDTH, 0))

            pygame.display.flip()
            pygame.time.delay(20)

    def _update_display_image(
        self, img_tuple: Tuple[str, pygame.Surface, pygame.Surface]
    ) -> None:
        """Updates the main display area with a new image."""
        if self.right_frame_previous:
            self._fade_transition(self.right_frame_previous, fade_in=False)

        self.right_frame_previous = img_tuple[2]  # Use the background surface
        self._fade_transition(self.right_frame_previous, fade_in=True)

    def _rotate_list(self, lst: list, direction: str = "left") -> None:
        """Rotates a list in place."""
        if not lst:
            return
        if direction == "left":
            lst.append(lst.pop(0))
        else:
            lst.insert(0, lst.pop())

    def _start_auto_timer(self) -> None:
        """Resets the auto-slideshow timer."""
        pygame.time.set_timer(pygame.USEREVENT, self.AUTO_START_DELAY_MS)

    def run(self) -> None:
        """Main event loop."""
        running = True
        while running:
            event = pygame.event.wait()
            reset_timer = False

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.USEREVENT:
                # Auto slideshow tick
                pygame.time.set_timer(pygame.USEREVENT, self.AUTO_FRAME_DELAY_MS)
                self._rotate_list(self.auto_image_list, "left")
                if self.auto_image_list:
                    self._update_display_image(self.auto_image_list[0])

            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_ESCAPE, pygame.K_q]:
                    running = False

                elif event.key == pygame.K_p:
                    logging.info("Auto-mode paused.")
                    pygame.time.set_timer(pygame.USEREVENT, 0)  # Stop timer

                # Menu Navigation (Up/Down)
                elif event.key in [pygame.K_UP, pygame.K_KP8]:
                    self.current_item_index = (self.current_item_index + 1) % len(
                        self.menu_items
                    )
                    self._change_category()
                    reset_timer = True

                elif event.key in [pygame.K_DOWN, pygame.K_KP2]:
                    self.current_item_index = (self.current_item_index - 1) % len(
                        self.menu_items
                    )
                    self._change_category()
                    reset_timer = True

                # Image Navigation (Left/Right)
                elif event.key in [pygame.K_LEFT, pygame.K_KP4]:
                    self._rotate_list(self.auto_image_list, "right")
                    if self.auto_image_list:
                        self._update_display_image(self.auto_image_list[0])
                    reset_timer = True

                elif event.key in [pygame.K_RIGHT, pygame.K_KP6]:
                    self._rotate_list(self.auto_image_list, "left")
                    if self.auto_image_list:
                        self._update_display_image(self.auto_image_list[0])
                    reset_timer = True

            if reset_timer:
                self._start_auto_timer()

        pygame.quit()
        sys.exit(0)

    def _change_category(self):
        """Helper to switch the active menu category."""
        self.current_item = self.menu_items[self.current_item_index]
        self.auto_image_list = self.current_item.images
        self._draw_menu()
        if self.auto_image_list:
            self._update_display_image(self.auto_image_list[0])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Python Wall Display Application")
    parser.add_argument(
        "--dir", default="menu-data", help="Directory containing menu.data and images"
    )
    args = parser.parse_args()

    app = WallDisplayApp(menu_data_dir=args.dir)
    app.run()
