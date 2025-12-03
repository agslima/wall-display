# Copilot Instructions for AI Agents

## Project Overview
- **Wall Display** is a Python 3.8+ application for digital signage, optimized for Raspberry Pi and embedded Linux/macOS devices.
- Main entry point: `wall-display.py` (uses `pygame` for UI and transitions).
- Content and menu structure are loaded dynamically from the `menu-data/` directory, especially `menu.data` and subfolders with images.

## Architecture & Data Flow
- **UI/Rendering:** All display logic is handled in `wall-display.py` using `pygame`.
- **Content Loading:** Reads menu structure and image paths from `menu-data/menu.data` and subfolders (e.g., `events/`, `notices/`).
- **Modes:**
  - *Auto/Slideshow:* Cycles images automatically.
  - *Interactive:* Keyboard/keypad navigation (see controls below).

## Developer Workflows
- **Run:** `python wall-display.py`
- **Install dependencies:** `pip install pygame` (see `requirements.txt` for more).
- **Configuration:**
  - Place images in `menu-data/<category>/`.
  - Edit `menu-data/menu.data` for menu structure.
- **Controls:**
  - Arrow keys or numpad for navigation.
  - `P` to pause/resume slideshow.
  - `ESC`/`Q` to quit.

## Project-Specific Patterns
- **Zero-config UI:** App auto-detects fullscreen and adapts layout.
- **Menu/data decoupling:** No hardcoded menu/image paths; all content is externalized in `menu-data/`.
- **Optimized for low-resource hardware:** Avoid heavy dependencies; keep code efficient.

## Integration Points
- **External:** Only `pygame` and Python stdlib (CSV, pathlib).
- **No network or cloud dependencies.**

## Key Files & Directories
- `wall-display.py`: Main logic, UI, event loop.
- `menu-data/`: All content and menu configuration.
- `requirements.txt`: Python dependencies.
- `README.md`: Usage, setup, and controls.

## Example Patterns
- To add a new category, create a subfolder in `menu-data/` and update `menu.data`.
- To update images, drop `.jpg` files in the relevant category folder.

---

**For AI agents:**
- Always read `menu-data/menu.data` and subfolders for dynamic content.
- Avoid hardcoding menu/image paths.
- Use `pygame` for all UI changes.
- Follow keyboard control conventions for navigation.

---

*Update this file as project conventions evolve. Ask maintainers if any workflow or pattern is unclear.*
