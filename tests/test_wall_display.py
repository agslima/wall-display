# pylint: disable=redefined-outer-name, protected-access
"""
Unit tests for the Wall Display application.
Tests configuration loading, asset parsing, and multithreading logic.
"""

import sys
import json
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path
import pytest

# Add the parent directory to sys.path to import the main module
sys.path.append(".")

# pylint: disable=wrong-import-position
from wall_display import ConfigManager, AssetManager, WallDisplayApp, MenuItem

# --- Global Fixtures ---


@pytest.fixture
def mock_pygame(mocker):
    """Mocks Pygame to allow testing in headless environments (CI/CD)."""
    mock = mocker.patch("wall_display.pygame")
    # Mock display info
    mock.display.Info.return_value.current_w = 1920
    mock.display.Info.return_value.current_h = 1080
    # Mock font rendering
    mock.font.SysFont.return_value.render.return_value = MagicMock()
    mock.font.SysFont.return_value.get_height.return_value = 20
    return mock


@pytest.fixture
def sample_config_json():
    """Provides a valid JSON configuration sample for testing."""
    return json.dumps(
        {
            "window": {"fullscreen": False, "menu_width": 200, "fps": 60},
            "colors": {"background": [10, 10, 10]},
        }
    )


@pytest.fixture
def sample_csv_data():
    """Provides a sample menu.data CSV content."""
    # ID:DIR:ENABLED:NAME:DESC
    return "1:nature:1:Nature:Beautiful trees\n2:city:0:City:Ignored item"


# --- Tests: ConfigManager ---


def test_config_load_valid(tmp_path, sample_config_json):
    """Ensure it loads valid JSON values correctly."""
    config_file = tmp_path / "config.json"
    config_file.write_text(sample_config_json)

    manager = ConfigManager(str(config_file))

    assert manager.get("window", "fps") == 60
    assert manager.get("window", "fullscreen") is False


def test_config_load_missing_file_defaults():
    """Ensure it falls back to DEFAULT_CONFIG if file doesn't exist."""
    manager = ConfigManager("non_existent.json")

    # Check a default value known to exist in the class
    assert manager.get("window", "menu_width") == 205
    assert manager.get("slideshow", "image_delay_ms") == 15000


def test_config_load_corrupt_json(tmp_path):
    """Ensure it handles broken JSON gracefully."""
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{broken_json: ]")

    manager = ConfigManager(str(bad_file))
    # Should load defaults instead of crashing
    assert manager.get("window", "menu_width") == 205


# --- Tests: AssetManager ---


def test_asset_manager_csv_parsing(sample_csv_data):
    """Test if AssetManager correctly parses CSV and ignores disabled items."""

    # Mock file system interactions
    with patch("pathlib.Path.exists", return_value=True), patch(
        "pathlib.Path.open", mock_open(read_data=sample_csv_data)
    ), patch("wall_display.AssetManager._scan_images", return_value=[Path("img1.jpg")]):

        manager = AssetManager(Path("dummy_dir"))
        items = manager.load_menu_structure()

        # Should only have 1 item (ID 1), because ID 2 has '0' in enabled column
        assert len(items) == 1
        assert items[0].menu_name == "Nature"
        assert items[0].menu_id == 1
        assert items[0].image_paths == [Path("img1.jpg")]


def test_asset_manager_load_images_threaded(mock_pygame):
    """Test the worker method that loads images."""
    manager = AssetManager(Path("."))

    # Create fake image paths
    paths = [Path("test1.jpg"), Path("test2.jpg")]

    # Mock pygame.image.load to avoid disk error
    mock_surf = MagicMock()
    mock_pygame.image.load.return_value = mock_surf
    # Mock convert (essential as it might fail without video mode)
    mock_surf.convert.return_value = mock_surf

    results = manager.load_images_threaded(paths)

    assert len(results) == 2
    assert results[0][0] == "test1.jpg"  # Check filename
    assert mock_pygame.image.load.call_count == 2


# --- Tests: WallDisplayApp (Controller & Threading) ---


def test_app_initialization(mock_pygame):
    """Test if the app initializes state correctly."""

    # We need to mock AssetManager to return at least one item
    mock_item = MenuItem(1, Path("."), "Test", "Desc", [])

    with patch(
        "wall_display.AssetManager.load_menu_structure", return_value=[mock_item]
    ), patch("wall_display.AssetManager.load_images_threaded", return_value=[]):

        app = WallDisplayApp("dummy_dir", "dummy_config.json")

        assert app.fps == 30  # Default from ConfigManager
        assert len(app.menu_items) == 1
        assert app.current_index == 0
        # Verify pygame init was called (using the fixture)
        assert mock_pygame.init.called


def test_trigger_category_load_spawns_thread():
    """
    CRITICAL: Verify that switching categories spawns a thread
    and updates the Request ID (Race Condition Protection).
    """
    mock_item = MenuItem(1, Path("."), "Test", "Desc", [])

    with patch(
        "wall_display.AssetManager.load_menu_structure", return_value=[mock_item]
    ), patch("wall_display.AssetManager.load_images_threaded", return_value=[]), patch(
        "wall_display.pygame"
    ), patch(
        "threading.Thread"
    ) as mock_thread_class:

        app = WallDisplayApp("dummy_dir", "dummy_config.json")

        # Initial state
        initial_id = app.load_request_id
        assert app.is_loading is False

        # Trigger the switch
        app._trigger_category_load(0)

        # Assertions
        assert app.is_loading is True
        assert app.load_request_id == initial_id + 1

        # Verify a thread was created and started
        assert mock_thread_class.called
        mock_thread_instance = mock_thread_class.return_value
        assert mock_thread_instance.start.called
        assert mock_thread_instance.daemon is True


def test_loading_complete_logic():
    """Test if the app correctly consumes data coming back from the thread."""

    with patch(
        "wall_display.AssetManager.load_menu_structure",
        return_value=[MenuItem(1, Path("."), "A", "B")],
    ), patch("wall_display.AssetManager.load_images_threaded", return_value=[]), patch(
        "wall_display.pygame"
    ):

        app = WallDisplayApp(".", "conf.json")

        # Simulate state: Thread is running
        app.is_loading = True

        # Simulate state: Thread finished and put data in the queue
        fake_data = [("img.jpg", MagicMock(), MagicMock())]
        app.loaded_result_queue.append(fake_data)

        # Run the check method
        app._check_loading_complete()

        # Assertions
        assert app.is_loading is False  # Should stop loading
        assert app.current_img_list == fake_data  # Data should be updated
