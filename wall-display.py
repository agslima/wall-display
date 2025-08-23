# ***************************************************************************
# * *
# * This program is free software; you can redistribute it and/or modify  *
# * it under the terms of the GNU General Public License as published by  *
# * the Free Software Foundation; either version 2 of the License, or     *
# * (at your option) any later version.                                   *
# * *
# * This program is distributed in the hope that it will be useful,       *
# * but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# * GNU General Public License for more details.                          *
# * *
# * You should have received a copy of the GNU General Public License     *
# * along with this program; if not, write to the                         *
# * Free Software Foundation, Inc.,                                       *
# * 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             *
# ***************************************************************************

import pygame
import sys
import os
import csv
from time import sleep

class WallDisplayApp:
    """
    Main application class for the wall display program.
    Handles all UI, data loading, and event processing.
    """
    def __init__(self, menu_data_dir="menu-data"):
        """Initializes the application and Pygame."""
        pygame.init()
        pygame.mouse.set_visible(0)

        # UI constants
        self.DISP_INFO = pygame.display.Info()
        self.DISP_W = self.DISP_INFO.current_w
        self.DISP_H = self.DISP_INFO.current_h
        self.MENU_WIDTH = 205
        self.MENU_HEIGHT = self.DISP_H

        # Application state variables
        self.screen = None
        self.menu_data_dir = menu_data_dir
        self.verbln = 0
        self.menu = []
        self.current_menu_item = {}
        self.auto_list = []
        self.right_frame_previous = None
        
        # Auto mode timings (in milliseconds)
        self.AUTO_FRAME_DELAY = 15000  # 15s
        self.AUTO_START_DELAY = 20000  # 20s

        self.setup_display()

    def setup_display(self):
        """Sets up the display and loads initial data."""
        try:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self._verbose_msg(f"Setting screen mode: ({self.DISP_W},{self.DISP_H})")
            
            self.menu = self._load_menu()
            if not self.menu:
                self._verbose_msg("No menu items found.")
                sys.exit(0)
            
            self.current_menu_item = self.menu[0]
            self.auto_list = self.current_menu_item["imgs"]
            self.right_frame_previous = self.auto_list[0][2]
        
        except (IOError, pygame.error) as e:
            self.fatal(1, f"Error setting up wall display: {e}")
        except Exception as e:
            self.fatal(1, f"An unexpected error occurred during setup: {e}")
            
        self.verbose_clean()
        self.update_menu()
        self.start_auto_mode()

    def _verbose_msg(self, msg):
        """Prints a verbose message on the screen."""
        f32 = pygame.font.Font(None, 32)
        font_height = f32.get_height()
        left_margin = 10
        surf_msg = f32.render(msg, True, (50, 50, 50))
        self.screen.blit(surf_msg, (left_margin, self.verbln))
        self.verbln += font_height
        pygame.display.flip()

    def fatal(self, status, msg):
        """Prints a fatal error message and exits."""
        sys.stderr.write(f"FATAL: {msg}\n")
        pygame.quit()
        sys.exit(status)

    def verbose_clean(self):
        """Clears the verbose message area."""
        self.verbln = 0
        backgnd = pygame.Surface(self.screen.get_size()).convert()
        backgnd.fill((0, 0, 0))
        self.screen.blit(backgnd, (0, 0))

    def update_menu(self):
        """Redraws the menu on the screen."""
        if self.menu and self.menu[0]["menuimg"]:
            self.screen.blit(self.menu[0]["menuimg"], (0, 0))
            pygame.display.flip()

    def _load_menu_data(self):
        """Loads menu entries from the menu.data file."""
        fn = os.path.join(self.menu_data_dir, "menu.data")
        menu_entries = []
        try:
            with open(fn, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile, delimiter=':')
                for row in reader:
                    if len(row) > 3 and int(row[2]) == 1:
                        d = {
                            "id": int(row[0].strip()),
                            "dir": row[1].strip(),
                            "menu": row[3].strip(),
                            "desc": row[4].strip()
                        }
                        menu_entries.append(d)
        except IOError as e:
            self.fatal(1, f"Could not open menu data file: {e}")
        return menu_entries

    def _load_menu(self):
        """Loads all menu data, including images and menu visuals."""
        self._verbose_msg("Reading menu info...")
        menu_entries = self._load_menu_data()
        self._verbose_msg("Reading menu info... [Done]")
        
        menu_list_data = [(item["id"], item["menu"]) for item in menu_entries]
        
        loaded_menu = []
        for menu_item in menu_entries:
            self._verbose_msg(f"Reading image files for menu entry: {menu_item['menu']}")
            img_list = self._read_jpg_files(menu_item["dir"])
            self._verbose_msg(f"Reading image files for menu entry: {menu_item['menu']} [Done]")
            menu_item["imgs"] = img_list
            
            menu_img = pygame.Surface((self.MENU_WIDTH, self.MENU_HEIGHT)).convert()
            menu_img.fill((0, 0, 0))
            
            menu_font = pygame.font.SysFont("gillsansmt", 20, bold=False)
            font_height = menu_font.get_height()
            left_margin = 10
            vertical_padding = 40
            line_pos = vertical_padding
            
            for menu_id, name in menu_list_data:
                font_color = (255, 255, 255) if menu_id == menu_item["id"] else (150, 150, 150)
                surf_msg = menu_font.render(name, True, font_color)
                menu_img.blit(surf_msg, (left_margin, line_pos))
                line_pos += font_height + vertical_padding
            
            menu_item["menuimg"] = menu_img
            loaded_menu.append(menu_item)
            
        return loaded_menu

    def _read_jpg_files(self, dirname):
        """Reads JPG files from a directory and converts them to Pygame surfaces."""
        print(f"listing dir: [{dirname}]")
        img_list = []
        try:
            fn_lst = sorted(os.listdir(dirname))
            for fn in fn_lst:
                if fn.lower().endswith(('.jpg', '.jpeg')):
                    try:
                        img = pygame.image.load(os.path.join(dirname, fn)).convert()
                        back = self._img_to_back(img)
                        img_list.append((fn, img, back))
                    except pygame.error:
                        print(f"Warning: Could not load image file {fn}")
        except FileNotFoundError:
            print(f"Warning: Directory not found: {dirname}")
        except Exception as e:
            print(f"An error occurred while reading images from '{dirname}': {e}")
        return img_list

    def _img_to_back(self, img):
        """Creates a background surface from an image."""
        back = pygame.Surface(img.get_size()).convert()
        back.blit(img, (0, 0))
        return back

    def _fade_out(self, img):
        """Fades out a Pygame surface."""
        for i in range(250, -1, -25):
            backgnd = pygame.Surface(self.screen.get_size()).convert()
            backgnd.fill((0, 0, 0))
            img.set_alpha(i)
            self.screen.blit(img, (self.MENU_WIDTH, 0))
            pygame.display.flip()
            pygame.time.delay(20)

    def _fade_in(self, img):
        """Fades in a Pygame surface."""
        for i in range(0, 250, 25):
            backgnd = pygame.Surface(self.screen.get_size()).convert()
            backgnd.fill((0, 0, 0))
            img.set_alpha(i)
            self.screen.blit(img, (self.MENU_WIDTH, 0))
            pygame.display.flip()
            pygame.time.delay(20)

    def _rotate_left(self, lst):
        """Rotates a list to the left."""
        if lst:
            i = lst.pop(0)
            lst.append(i)

    def _rotate_right(self, lst):
        """Rotates a list to the right."""
        if lst:
            i = lst.pop()
            lst.insert(0, i)

    def _update_right_frame(self, img):
        """Updates the right-side image frame with a fade effect."""
        self._fade_out(self.right_frame_previous)
        self.right_frame_previous = img[2]
        self._fade_in(self.right_frame_previous)

    def start_auto_mode(self):
        """Starts the auto mode timer."""
        pygame.time.set_timer(pygame.USEREVENT, self.AUTO_START_DELAY)

    def run(self):
        """Main event loop for the application."""
        done = False
        while not done:
            event = pygame.event.wait()
            
            reset_timer = False

            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.USEREVENT:
                # Auto mode: advance to the next slide
                pygame.time.set_timer(pygame.USEREVENT, self.AUTO_FRAME_DELAY)
                self._rotate_left(self.auto_list)
                self._update_right_frame(self.auto_list[0])
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_ESCAPE, pygame.K_q]:
                    done = True
                elif event.key == pygame.K_p:
                    # Pause auto mode
                    pygame.time.set_timer(pygame.USEREVENT, 0)
                elif event.key in [pygame.K_UP, pygame.K_KP8]:
                    self._rotate_left(self.menu)
                    self.current_menu_item = self.menu[0]
                    self.auto_list = self.current_menu_item["imgs"]
                    self.update_menu()
                    self._update_right_frame(self.auto_list[0])
                    reset_timer = True
                elif event.key in [pygame.K_DOWN, pygame.K_KP2]:
                    self._rotate_right(self.menu)
                    self.current_menu_item = self.menu[0]
                    self.auto_list = self.current_menu_item["imgs"]
                    self.update_menu()
                    self._update_right_frame(self.auto_list[0])
                    reset_timer = True
                elif event.key in [pygame.K_LEFT, pygame.K_KP4]:
                    self._rotate_right(self.auto_list)
                    self._update_right_frame(self.auto_list[0])
                    reset_timer = True
                elif event.key in [pygame.K_RIGHT, pygame.K_KP6]:
                    self._rotate_left(self.auto_list)
                    self._update_right_frame(self.auto_list[0])
                    reset_timer = True
            
            if reset_timer:
                self.start_auto_mode()
        
        pygame.quit()
        sys.exit(0)

if __name__ == "__main__":
    # You can pass the menu data directory as a command-line argument if needed
    # parser = argparse.ArgumentParser(description="Wall Display App")
    # parser.add_argument("--menu-dir", default="menu-data", help="Directory containing menu data and image folders.")
    # args = parser.parse_args()
    # app = WallDisplayApp(args.menu_dir)
    
    # Or, run with the default directory
    app = WallDisplayApp()
    app.run()

