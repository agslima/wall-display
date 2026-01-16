"""
Wall Display: Interactive digital signage system using pygame.
Architecture: MVC + SRP + Multithreading (Non-blocking I/O).
"""

import sys
import csv
import json
import logging
import argparse
import threading
import math
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
    """Model representing a menu category."""

    menu_id: int
    directory: Path
    menu_name: str
    description: str
    image_paths: List[Path] = field(default_factory=list)
    

class ConfigManager:
    """Responsibility: Load, validate and provide configuration settings."""

    DEFAULT_CONFIG = {
        "window": {"fullscreen": True, "menu_width": 205, "fps": 30},
        "slideshow": {
            "image_delay_ms": 15000,
            "start_delay_ms": 20000,
            "fade_speed_ms": 20,
        },
        "colors": {
            "background": [0, 0, 0],
            "font_active": [255, 255, 255],
            "font_inactive": [100, 100, 100],
            "loading_text": [255, 255, 0],
            "spinner": [0, 200, 255],
        },
    }

    def __init__(self, config_path: str):
        self.data = self._load_config(config_path)

    def _load_config(self, path: str) -> Dict[str, Any]:
        path_obj = Path(path)
        if not path_obj.exists():
            logging.warning("Config file %s not found. Using defaults.", path)
            return self.DEFAULT_CONFIG.copy()

        try:
            with path_obj.open("r", encoding="utf-8") as file_handle:
                user_config = json.load(file_handle)
                final_config = self.DEFAULT_CONFIG.copy()
                final_config.update(user_config)
                return final_config
        except json.JSONDecodeError as error:
            logging.error("Config error: %s. Using defaults.", error)
            return self.DEFAULT_CONFIG.copy()

    def get(self, section: str, key: str) -> Any:
        """Safe getter for config values."""
        return self.data.get(section, {}).get(key)


class AssetManager:
    """Responsibility: Handle File I/O and Image Processing."""

    def __init__(self, menu_data_dir: Path):
        self.root_dir = menu_data_dir

    def load_menu_structure(self) -> List[MenuItem]:
        """Scans CSV and directories to build the Menu Model (Metadata only)."""
        csv_path = self.root_dir / "menu.data"
        if not csv_path.exists():
            logging.error("Menu data file not found: %s", csv_path)
            return []

        items = []
        try:
            with csv_path.open("r", encoding="utf-8") as file_handle:
                reader = csv.reader(file_handle, delimiter=":")
                for row in reader:
                    if len(row) > 3 and int(row[2]) == 1:
                        img_dir = self.root_dir / row[1].strip()
                        paths = self._scan_images(img_dir)

                        items.append(
                            MenuItem(
                                menu_id=int(row[0].strip()),
                                directory=img_dir,
                                menu_name=row[3].strip(),
                                description=row[4].strip() if len(row) > 4 else "",
                                image_paths=paths,
                            )
                        )
        except (IOError, ValueError) as error:
            logging.error("Error reading menu data: %s", error)

        return items

    def _scan_images(self, directory: Path) -> List[Path]:
        if not directory.exists():
            return []
        return sorted(
            [f for f in directory.iterdir() if f.suffix.lower() in (".jpg", ".jpeg")]
        )

    def load_images_threaded(
        self, paths: List[Path]
    ) -> List[Tuple[str, pygame.Surface, pygame.Surface]]:
        """
        Loads images from disk. Designed to run in a worker thread.
        Returns a list of loaded resources.
        """
        loaded_buffer = []
        for path in paths:
            try:
                # Load image
                img = pygame.image.load(str(path))

                img = img.convert()

                bg_surface = pygame.Surface(img.get_size()).convert()
                bg_surface.blit(img, (0, 0))

                loaded_buffer.append((path.name, img, bg_surface))
            except (pygame.error, OSError):
                logging.warning("Invalid image skipped: %s", path.name)

        return loaded_buffer


class ViewRenderer:
    """Responsibility: Draw everything on screen (UI, Images, Transitions, Spinner)."""

    def __init__(self, screen: pygame.Surface, config: ConfigManager):
        self.screen = screen
        self.config = config
        try:
            size = screen.get_size()
            if isinstance(size, (tuple, list)) and len(size) == 2:
                self.width, self.height = size
            else:
                # Attempt to read display info
                try:
                    display_info = pygame.display.Info()
                    self.width = getattr(display_info, "current_w", 800)
                    self.height = getattr(display_info, "current_h", 600)
                except (AttributeError, TypeError, pygame.error):
                    self.width, self.height = 800, 600
        except (AttributeError, TypeError):
            try:
                display_info = pygame.display.Info()
                self.width = getattr(display_info, "current_w", 800)
                self.height = getattr(display_info, "current_h", 600)
            except (AttributeError, TypeError, pygame.error):
                self.width, self.height = 800, 600

        self.menu_width = config.get("window", "menu_width")

        # UI State
        self.scroll_y = 0
        self.font = pygame.font.SysFont("gillsansmt", 22, bold=False)
        self.item_height = 50
        self.spinner_angle = 0

    def draw_menu_sidebar(self, items: List[MenuItem], active_index: int) -> None:
        """Draws the sidebar menu with scrolling logic."""
        colors = self.config.data["colors"]

        # Background
        sidebar_rect = pygame.Rect(0, 0, self.menu_width, self.height)
        pygame.draw.rect(self.screen, colors["background"], sidebar_rect)

        # Scroll Logic
        center_screen_y = self.height // 2
        active_item_y = active_index * self.item_height
        target = center_screen_y - active_item_y
        self.scroll_y += (target - self.scroll_y) * 0.1  # Smooth lerp

        # Draw Items
        left_margin = 20
        for i, item in enumerate(items):
            y_pos = int(self.scroll_y + (i * self.item_height))

            # Culling
            if y_pos < -self.item_height or y_pos > self.height:
                continue

            color = (
                colors["font_active"] if i == active_index else colors["font_inactive"]
            )
            text_surf = self.font.render(item.menu_name, True, color)
            self.screen.blit(text_surf, (left_margin, y_pos))

    def draw_static_image(self, surface: pygame.Surface) -> None:
        """Draws the current image without transition."""
        self.screen.blit(surface, (self.menu_width, 0))

    def draw_spinner(self) -> None:
        """Draws a rotating loading circle."""
        colors = self.config.data["colors"]
        center_x = self.menu_width + (self.width - self.menu_width) // 2
        center_y = self.height // 2
        radius = 40
        thickness = 5

        self.spinner_angle = (self.spinner_angle + 10) % 360

        # Draw arc
        rect = pygame.Rect(center_x - radius, center_y - radius, radius * 2, radius * 2)
        start_angle = math.radians(self.spinner_angle)
        end_angle = math.radians(self.spinner_angle + 270)

        pygame.draw.arc(
            self.screen,
            colors.get("spinner", (0, 200, 255)),
            rect,
            start_angle,
            end_angle,
            thickness,
        )

        # Loading Text
        font = pygame.font.Font(None, 30)
        text = font.render("Loading...", True, colors["font_active"])
        text_rect = text.get_rect(center=(center_x, center_y + radius + 30))
        self.screen.blit(text, text_rect)

    def fade_image_transition(
        self, old_surface: Optional[pygame.Surface], new_surface: pygame.Surface
    ) -> None:
        """Handles cross-fade transition between images."""
        speed = self.config.get("slideshow", "fade_speed_ms")
        colors = self.config.data["colors"]
        display_area = pygame.Rect(
            self.menu_width, 0, self.width - self.menu_width, self.height
        )

        for alpha in range(0, 256, 40):  # Faster steps
            pygame.draw.rect(self.screen, colors["background"], display_area)

            if old_surface:
                old_surface.set_alpha(255 - alpha)
                self.screen.blit(old_surface, (self.menu_width, 0))

            new_surface.set_alpha(alpha)
            self.screen.blit(new_surface, (self.menu_width, 0))

            pygame.display.update(display_area)
            pygame.time.delay(speed)


class WallDisplayApp:
    """Controller: Handles Main Loop, Input, and Thread Management."""

    def __init__(self, menu_dir: str, config_path: str):
        self.config_mgr = ConfigManager(config_path)
        self.asset_mgr = AssetManager(Path(menu_dir))

        pygame.init()
        pygame.mouse.set_visible(False)

        flags = pygame.FULLSCREEN if self.config_mgr.get("window", "fullscreen") else 0
        screen = pygame.display.set_mode((0, 0), flags)

        self.renderer = ViewRenderer(screen, self.config_mgr)
        self.clock = pygame.time.Clock()
        self.fps = self.config_mgr.get("window", "fps") or 30

        # Data State
        self.menu_items: List[MenuItem] = []
        self.current_index = 0
        self.current_img_list: list = []
        self.current_img_bg: Optional[pygame.Surface] = None

        # Threading State
        self.is_loading = False
        self.load_request_id = 0  # To handle rapid key presses (race conditions)
        self.loaded_result_queue: List = []  # Shared variable to pass data from thread

        self._initialize_content()

    def _initialize_content(self):
        """Loads initial menu structure and first category."""
        self.menu_items = self.asset_mgr.load_menu_structure()
        if not self.menu_items:
            sys.exit("No menu data found")

        # Initial load
        self.current_img_list = self.asset_mgr.load_images_threaded(
            self.menu_items[0].image_paths
        )
        if self.current_img_list:
            self.current_img_bg = self.current_img_list[0][2]

        self._reset_slideshow_timer(is_start=True)

    def _trigger_category_load(self, new_index: int):
        """Initiates the background thread loading."""
        self.current_index = new_index
        self.is_loading = True
        self.loaded_result_queue = []  # Clear previous results
        self.load_request_id += 1
        current_req_id = self.load_request_id

        item = self.menu_items[self.current_index]

        # Worker Function
        def worker(req_id, paths):
            logging.info("Thread started for: %s", item.menu_name)
            results = self.asset_mgr.load_images_threaded(paths)

            # Post results safely
            if req_id == self.load_request_id:
                self.loaded_result_queue.append(results)

        # Start Thread
        loader_thread = threading.Thread(
            target=worker, args=(current_req_id, item.image_paths)
        )
        loader_thread.daemon = True
        loader_thread.start()

    def _check_loading_complete(self):
        """Called every frame to check if thread finished."""
        if self.loaded_result_queue:
            # Thread finished!
            new_images = self.loaded_result_queue.pop(0)
            self.current_img_list = new_images
            self.is_loading = False

            # Show first image
            if self.current_img_list:
                new_bg = self.current_img_list[0][2]
                self.renderer.fade_image_transition(self.current_img_bg, new_bg)
                self.current_img_bg = new_bg

            self._reset_slideshow_timer(is_start=True)

    def _rotate_images(self, direction="left"):
        """Rotates the image list and updates the display."""
        if not self.current_img_list or self.is_loading:
            return

        if direction == "left":
            self.current_img_list.append(self.current_img_list.pop(0))
        else:
            self.current_img_list.insert(0, self.current_img_list.pop())

        new_bg = self.current_img_list[0][2]
        self.renderer.fade_image_transition(self.current_img_bg, new_bg)
        self.current_img_bg = new_bg

    def _reset_slideshow_timer(self, is_start=False):
        """Resets the timer for the next slide."""
        section = "slideshow"
        delay = self.config_mgr.get(
            section, "start_delay_ms" if is_start else "image_delay_ms"
        )
        pygame.time.set_timer(pygame.USEREVENT, delay)

    def run(self):
        """Main Loop."""
        running = True
        slide_delay = self.config_mgr.get("slideshow", "image_delay_ms")
        colors = self.config_mgr.data["colors"]

        while running:
            self.clock.tick(self.fps)

            # 1. Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.USEREVENT:
                    if not self.is_loading:
                        pygame.time.set_timer(pygame.USEREVENT, slide_delay)
                        self._rotate_images("left")

                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_q]:
                        running = False

                    elif event.key == pygame.K_p:
                        pygame.time.set_timer(pygame.USEREVENT, 0)

                    # Navigation
                    elif event.key in [pygame.K_UP, pygame.K_KP8]:
                        new_idx = (self.current_index + 1) % len(self.menu_items)
                        self._trigger_category_load(new_idx)

                    elif event.key in [pygame.K_DOWN, pygame.K_KP2]:
                        new_idx = (self.current_index - 1) % len(self.menu_items)
                        self._trigger_category_load(new_idx)

                    elif event.key in [pygame.K_LEFT, pygame.K_KP4]:
                        self._rotate_images("right")
                        self._reset_slideshow_timer(is_start=True)

                    elif event.key in [pygame.K_RIGHT, pygame.K_KP6]:
                        self._rotate_images("left")
                        self._reset_slideshow_timer(is_start=True)

            # 2. Logic Update
            if self.is_loading:
                self._check_loading_complete()

            # 3. Drawing
            # Draw Sidebar
            self.renderer.draw_menu_sidebar(self.menu_items, self.current_index)

            # Draw Main Content
            if self.is_loading:
                # Clear content area
                bg_rect = pygame.Rect(
                    self.renderer.menu_width,
                    0,
                    self.renderer.width,
                    self.renderer.height,
                )
                pygame.draw.rect(self.renderer.screen, colors["background"], bg_rect)
                self.renderer.draw_spinner()
            else:
                # Keep drawing current image if not loading
                if self.current_img_bg:
                    self.renderer.draw_static_image(self.current_img_bg)

            pygame.display.flip()

        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wall Display Pro - Multithreaded")
    parser.add_argument("--dir", default="menu-data", help="Data directory")
    parser.add_argument("--config", default="config.json", help="Config file")
    args = parser.parse_args()

    try:
        app_instance = WallDisplayApp(args.dir, args.config)
        app_instance.run()
    # pylint: disable=broad-except
    except Exception as main_error:
        logging.critical("Application crashed: %s", main_error)
        pygame.quit()
        sys.exit(1)
