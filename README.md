# Wall Display

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/platform-linux%20%7C%20rpi%20%7C%20mac-lightgrey?style=for-the-badge)
![License](https://img.shields.io/github/license/agslima/wall-display?style=for-the-badge)

**Wall Display** is a robust, lightweight Python application designed to turn any screen into an interactive digital signage system. Built with `pygame`, it is optimized for embedded devices like the **Raspberry Pi**.

It handles smooth visual transitions, dynamic content loading, and automated slideshows, making it perfect for events, information kiosks, or digital art galleries.


## Demo

![Wall Display Running](https://via.placeholder.com/800x400.png?text=Place+Your+Screenshot+or+GIF+Here)

> *The system is displaying the "Events" category with the sidebar menu active.*

## Features

* **Smooth Aesthetics:** Implements fade-in/fade-out transitions for a premium feel.
* **Zero-Config UI:** Automatically adapts to Fullscreen mode.
* **Dynamic Loader:** Reads menu structures and image paths from a simple configuration file (`menu.data`), allowing content updates without touching code.
* **Dual Mode:** * **Auto:** Cycles through images automatically (Slideshow mode).
* **Interactive:** Users can navigate categories and images via keyboard/keypad.
* **Hardware Efficient:** Optimized for low-resource environments (RPi).

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
    python wall_display.py
```

## Configuration

The application expects a directory (default: `menu-data/`) containing a `menu.data` file.

**File Structure:**

```text
/root
  ├── wall_display.py
  └── menu-data/
      ├── menu.data
      ├── events/      (contains .jpg files)
      └── notices/     (contains .jpg files)
```

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

## Tech Stack

* **Language:** Python 3
* **Graphics Engine:** Pygame - Handles rendering and window management.
* **Data Handling:** Native CSV and Pathlib libraries.

## License

This project is licensed under the GPLv2 License. See the LICENSE file for details.
