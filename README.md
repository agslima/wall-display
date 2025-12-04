# Wall Display

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/platform-linux%20%7C%20rpi%20%7C%20mac-lightgrey?style=for-the-badge)
![License](https://img.shields.io/github/license/agslima/wall-display?style=for-the-badge)

**Wall Display** is a robust, lightweight Python application designed to turn any screen into an interactive digital signage system. Built with `pygame` and following a modern **MVC + SRP architecture with multithreading**, it is optimized for embedded devices like the **Raspberry Pi**.

It handles smooth visual transitions, dynamic content loading, non-blocking image loading, and automated slideshows, making it perfect for events, information kiosks, or digital art galleries.


## Demo

![Wall Display Running](https://via.placeholder.com/800x400.png?text=Place+Your+Screenshot+or+GIF+Here)

> *The system is displaying the "Events" category with the sidebar menu active.*

## Features

* **Smooth Aesthetics:** Implements fade-in/fade-out transitions and smooth menu scrolling for a premium feel.
* **Zero-Config UI:** Automatically adapts to fullscreen mode and responsive layouts.
* **Dynamic Content Loading:** Reads menu structures and image paths from a simple CSV configuration (`menu.data`), allowing content updates without touching code.
* **Non-Blocking I/O:** Images load in background worker threads, preventing UI freezes on large datasets.
* **Dual Mode:**
  - **Auto/Slideshow:** Cycles through images automatically with configurable delays.
  - **Interactive:** Users navigate categories and images via keyboard/keypad.
* **Thread-Safe:** Handles race conditions from rapid key presses using request IDs.
* **Configurable:** Supports custom JSON configuration for window settings, slideshow timings, colors, and spinner appearance.
* **Hardware Efficient:** Optimized for low-resource environments (Raspberry Pi, embedded Linux).

## Getting Started

### Prerequisites

* Python 3.8 or higher
* `pip` (Python package manager)

### Installation

1. **Clone the repository:**

```bash
    git clone [https://github.com/agslima/wall-display.git](https://github.com/agslima/wall-display.git)
    cd wall-display
```

2. **Install dependencies:**

```bash
    pip install pygame
```

3. **Run the application:**

```bash
    # Default run (uses menu-data/ directory and config.json)
    python wall_display.py
    
    # Custom menu directory
    python wall_display.py --dir /path/to/menu-data
    
    # Custom configuration file
    python wall_display.py --config /path/to/config.json
    
    # Combined options
    python wall_display.py --dir ./my-menu-data --config ./my-config.json
```

## Configuration

### Menu Structure (menu.data)

The application expects a directory (default: `menu-data/`) containing a `menu.data` CSV file.

**File Structure:**

```text
/root
  ├── wall_display.py
  ├── config.json                 (Optional)
  └── menu-data/
      ├── menu.data               (Required CSV file)
      ├── ic-research-education/  (contains .jpg files)
      └── research/               (contains .jpg files)
```

**menu.data Format** (CSV with `:` delimiter):

```csv
menu_id:folder_name:enabled:display_name:description
1:ic-research-education:1:IC Research & Education:Explore our research initiatives
2:research:1:Research Projects:Latest research developments
```

Fields:
- `menu_id`: Unique identifier for the menu category
- `folder_name`: Directory name under `menu-data/` containing images
- `enabled`: `1` to enable, `0` to disable category
- `display_name`: Display name shown in the sidebar menu
- `description`: Optional description (can be empty)

### Configuration File (config.json)

Create an optional `config.json` to customize behavior. If not provided, defaults are used.

**Example config.json:**

```json
{
  "window": {
    "fullscreen": true,
    "menu_width": 205,
    "fps": 30
  },
  "slideshow": {
    "image_delay_ms": 15000,
    "start_delay_ms": 20000,
    "fade_speed_ms": 20
  },
  "colors": {
    "background": [0, 0, 0],
    "font_active": [255, 255, 255],
    "font_inactive": [100, 100, 100],
    "loading_text": [255, 255, 0],
    "spinner": [0, 200, 255]
  }
}
```

**Configuration Options:**

| Section | Key | Type | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| window | fullscreen | boolean | true | Enable fullscreen mode |
| window | menu_width | integer | 205 | Width of sidebar menu in pixels |
| window | fps | integer | 30 | Target frames per second |
| slideshow | image_delay_ms | integer | 15000 | Delay between images (ms) |
| slideshow | start_delay_ms | integer | 20000 | Initial delay before first image (ms) |
| slideshow | fade_speed_ms | integer | 20 | Duration of fade transition (ms) |
| colors | background | [R, G, B] | [0, 0, 0] | Background color (black) |
| colors | font_active | [R, G, B] | [255, 255, 255] | Active menu text color (white) |
| colors | font_inactive | [R, G, B] | [100, 100, 100] | Inactive menu text color (gray) |
| colors | loading_text | [R, G, B] | [255, 255, 0] | Loading indicator text color (yellow) |
| colors | spinner | [R, G, B] | [0, 200, 255] | Spinner animation color (cyan) |

---

## Controls

The application is designed to be controlled via a standard keyboard or a mapped numeric keypad.

| Key | Action |
| :--- | :--- |
| **UP / Numpad 8** | Previous Menu Category |
| **DOWN / Numpad 2** | Next Menu Category |
| **LEFT / Numpad 4** | Previous Image |
| **RIGHT / Numpad 6** | Next Image |
| **P** | Pause/Resume Auto-Slideshow |
| **ESC / Q** | Quit Application |

## Architecture

Wall Display follows a **Model-View-Controller (MVC)** pattern with **Single Responsibility Principle (SRP)** and **Multithreading** for non-blocking I/O:

- **ConfigManager:** Loads and manages configuration settings with JSON fallback to defaults.
- **MenuItem (Model):** Represents menu categories with metadata and image paths.
- **AssetManager:** Handles file I/O, CSV parsing, and threaded image loading.
- **ViewRenderer:** Manages all rendering logic including transitions, menu scrolling, and spinner animations.
- **WallDisplayApp (Controller):** Main event loop, input handling, and thread coordination.

**Threading Model:**
- Images load in background worker threads to prevent UI blocking.
- Race condition handling via `load_request_id` prevents stale results.
- Thread-safe communication via `loaded_result_queue`.
- All pygame drawing occurs on the main thread.

## Tech Stack

* **Language:** Python 3.8+
* **Graphics Engine:** Pygame 2.0.0+ - Handles rendering and window management.
* **Data Handling:** Native CSV, JSON, and Pathlib libraries.
* **Threading:** Python threading module for non-blocking I/O.
* **Testing:** Pytest with code quality tools (Pylint, Flake8, Black).

## Version Management

This project uses **Git Tags** to manage versions and track the evolution of the codebase:

### Current Versions

* **v3.0.0 (Current):** New architecture with MVC pattern, multithreading, and non-blocking I/O.
* **v2.0.0:** Original implementation updated to modern Python 3.8+.
* **v1.0.0:** Legacy version (Python 3.6 and earlier).

### Accessing Specific Versions

**View on GitHub:**
1. Go to the repository on GitHub
2. Click the "main" branch dropdown
3. Select "Tags" tab
4. Choose the desired version (v1.0.0, v2.0.0, or v3.0.0)

**Clone a Specific Version:**

```bash
# Clone the latest version (main branch)
git clone https://github.com/agslima/wall-display.git

# Clone a specific version tag
git clone --branch v3.0.0 https://github.com/agslima/wall-display.git

# Switch to a specific version in an existing clone
git checkout v2.0.0
```

### Version Release Notes

**v3.0.0 - New Architecture & Performance

* Implemented MVC + SRP architecture
* Added multithreading for non-blocking image loading
* Introduced race condition handling with request IDs
* Enhanced UI with smooth scrolling and fade transitions
* Added comprehensive JSON configuration support
* Improved performance on low-resource devices

**v2.0.0 - Python Modernization**

* Updated to Python 3.8+ compatibility
* Refactored codebase for better maintainability
* Added support for custom configuration files
* Improved error handling and logging

**v1.0.0 - Legacy Version**

* Original implementation
* Python 3.6 compatibility
* Basic slideshow functionality

## License

This project is licensed under the GPLv2 License. See the LICENSE file for details.
