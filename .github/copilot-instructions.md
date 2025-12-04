# Copilot Instructions for AI Agents

## Project Overview
- **Wall Display** is a Python 3.8+ application for digital signage, optimized for Raspberry Pi and embedded Linux/macOS devices.
- Main entry point: `wall_display.py` (uses `pygame` for UI and transitions).
- Content and menu structure are loaded dynamically from the `menu-data/` directory, especially `menu.data` and subfolders with images.

## Architecture & Data Flow
- **Architecture:** MVC + SRP + Multithreading (Non-blocking I/O)
- **UI/Rendering:** All display logic is handled in `wall_display.py` using `pygame`.
- **Content Loading:** Reads menu structure and image paths from `menu-data/menu.data` and subfolders (e.g., `events/`, `notices/`).
- **Modes:**
  - *Auto/Slideshow:* Cycles images automatically via timer events.
  - *Interactive:* Keyboard/keypad navigation (see controls below).

## Core Components

### 1. `ConfigManager`
- **Responsibility:** Load, validate and provide configuration settings.
- Supports JSON config files with defaults fallback.
- Manages window settings (fullscreen, menu width, FPS), slideshow timings, colors, and spinner appearance.
- Safe getter method for accessing nested config values.

### 2. `MenuItem` (Model)
- **Attributes:** `menu_id`, `directory`, `menu_name`, `description`, `image_paths`
- Stores metadata only (images are managed by runtime state to avoid threading conflicts).
- Loaded from `menu.data` CSV file with delimiter `:`.

### 3. `AssetManager`
- **Responsibility:** Handle File I/O and Image Processing.
- Loads menu structure from CSV file.
- Scans directories for `.jpg`/`.jpeg` images.
- **Key Method:** `load_images_threaded()` - Loads images in worker threads to avoid blocking the main loop.
- Converts images to optimized pygame surfaces for fast rendering.

### 4. `ViewRenderer`
- **Responsibility:** Draw everything on screen (UI, Images, Transitions, Spinner).
- Manages sidebar menu rendering with smooth scrolling/lerping.
- Implements smooth fade-in/fade-out transitions via `fade_image_transition()`.
- Draws animated loading spinner during background loading.
- Uses culling to optimize rendering performance.

### 5. `WallDisplayApp` (Controller)
- **Responsibility:** Handles Main Loop, Input, and Thread Management.
- Manages the pygame event loop with 30 FPS target.
- Handles keyboard/numpad navigation and slideshow control.
- Implements non-blocking image loading via background threads.
- Uses `load_request_id` to handle race conditions from rapid key presses.
- Manages `loaded_result_queue` for safe thread-to-main communication.

## Threading & Performance
- **Non-Blocking I/O:** Image loading runs in worker threads, preventing UI freezes.
- **Race Condition Handling:** Request IDs prevent stale image results from overwriting newer data.
- **Smooth Animation:** Uses `pygame.time.Clock.tick()` for frame-rate control and consistent animation.
- **Display Optimization:** Culling, alpha blending, and targeted display updates minimize rendering overhead.

## Developer Workflows
- **Run:** `python wall_display.py [--dir menu-data] [--config config.json]`
- **Install dependencies:** `pip install pygame` (see `requirements.txt` for more).
- **Code Quality Tools:** pylint, flake8, black, pytest.
- **Configuration:**
  - Place images in `menu-data/<category>/`.
  - Edit `menu-data/menu.data` for menu structure (CSV format with `:` delimiter).
  - Optional `config.json` for custom settings (window, slideshow timings, colors).
- **Controls:**
  - **UP / Numpad 8:** Previous Menu Category
  - **DOWN / Numpad 2:** Next Menu Category
  - **LEFT / Numpad 4:** Previous Image
  - **RIGHT / Numpad 6:** Next Image
  - **P:** Pause/Resume Auto-Slideshow
  - **ESC / Q:** Quit Application

## Project-Specific Patterns
- **Zero-config UI:** App auto-detects fullscreen and adapts layout with sensible defaults.
- **Menu/data decoupling:** No hardcoded menu/image paths; all content is externalized in `menu-data/`.
- **Optimized for low-resource hardware:** Minimal dependencies; efficient image handling and threading.
- **CSV-based menu structure:** Simple, human-readable configuration via `menu.data`.
- **State separation:** Images managed at runtime (controller state), not stored in model objects.
- **Smooth transitions:** All UI changes use fade/lerp animations for premium feel.

## Integration Points
- **External Dependencies:** Only `pygame` (v2.0.0+) and Python stdlib (csv, json, pathlib, logging, threading).
- **No network or cloud dependencies.**
- **Platform agnostic:** Supports Linux, Raspberry Pi, macOS with consistent behavior.

## Key Files & Directories
- `wall_display.py`: Main application with all core classes (ConfigManager, MenuItem, AssetManager, ViewRenderer, WallDisplayApp).
- `menu-data/menu.data`: CSV configuration file defining menu structure and image directories.
- `menu-data/<category>/`: Folders containing `.jpg` images for each category.
- `config.json`: Optional configuration file for customizing window, slideshow, colors (uses defaults if not provided).
- `requirements.txt`: Python dependencies (pygame, testing/linting tools).
- `README.md`: User-facing usage, setup, and control documentation.
- `tests/`: Unit tests using pytest.

## Example Patterns
- To add a new category:
  1. Create a subfolder `menu-data/<new-category>/`
  2. Add `.jpg` images to that folder
  3. Add a row to `menu-data/menu.data`: `<id>:<folder-name>:1:<display-name>:<description>`
- To update images: Drop `.jpg` files in the relevant category folder (auto-scanned on startup).
- To customize behavior: Create `config.json` with custom settings (window size, FPS, timings, colors).

## Threading Best Practices
- Never call `pygame` drawing functions from worker threads.
- Use `loaded_result_queue` for thread-safe communication (producer-consumer pattern).
- Always check `load_request_id` in worker thread to discard stale results.
- Keep I/O-bound operations in worker threads; draw only on main thread.

---

**For AI agents:**
- Always read `menu-data/menu.data` and subfolders for dynamic content understanding.
- Avoid hardcoding menu/image paths or category names.
- Use `pygame` for all UI changes and rendering.
- Follow MVC pattern: Model (MenuItem) → View (ViewRenderer) → Controller (WallDisplayApp).
- Respect threading boundaries: I/O in threads, drawing on main thread.
- Test changes with unit tests in `tests/` directory.

---

*Update this file as project conventions evolve. Ask maintainers if any workflow or pattern is unclear.*
