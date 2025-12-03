import sys
import pytest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path

# Importa a classe do seu arquivo (assumindo que o arquivo se chama wall_display.py)
from wall_display import WallDisplayApp, MenuItem

# --- Global Fixtures and Mocks ---

@pytest.fixture
def mock_pygame():
    """
    Complete pygame mock to avoid video/audio driver errors
    during tests in CI/CD or headless environments.
    """
    with patch('wall_display.pygame') as mock_pg:
        # Configura mocks comuns que o __init__ chama
        mock_pg.display.Info.return_value.current_w = 1920
        mock_pg.display.Info.return_value.current_h = 1080
        mock_pg.font.SysFont.return_value.get_height.return_value = 20
        mock_pg.font.Font.return_value.get_height.return_value = 20
        yield mock_pg

@pytest.fixture
def sample_menu_data():
    """Simulates the contents of the menu.data file"""
    return "1:images_dir:1:Nature:Landscape photos\n2:city_dir:1:City:Urban photos"

# --- Pure Logic Tests ---

def test_rotate_list_left():
    """Tests the logic of rotating a list to the left."""
    app = MagicMock(spec=WallDisplayApp)  # Partial mock to access static/helper method
    lista = [1, 2, 3]
    
    # Injects the actual method into the mocked instance if not static,
    # or we test by instantiating the class if possible.
    # Since _rotate_list does not depend on self, we can test it directly if extracted,
    # but here we instantiate the class with mocks.
    with patch('wall_display.pygame'):
        app = WallDisplayApp.__new__(WallDisplayApp)  # Creates instance without running __init__
        
        # Test left
        app._rotate_list(lista, "left")
        assert lista == [2, 3, 1]

def test_rotate_list_right():
    """Tests the logic of rotating a list to the right."""
    with patch('wall_display.pygame'):
        app = WallDisplayApp.__new__(WallDisplayApp)
        lista = [1, 2, 3]
        app._rotate_list(lista, "right")
        assert lista == [3, 1, 2]

# --- Integration Tests with Mocks (IO and Pygame) ---

def test_app_initialization_success(mock_pygame, sample_menu_data):
    """
    Verifies that the app initializes correctly:
    1. Reads the data file.
    2. Creates MenuItem objects.
    3. Configures the screen.
    """
    # Mock the file system for menu.data
    mock_file_path = Path("menu-data/menu.data")
    
    with patch("pathlib.Path.exists", return_value=True), \
         patch("pathlib.Path.open", mock_open(read_data=sample_menu_data)), \
         patch("pathlib.Path.iterdir", return_value=[Path("img1.jpg")]), \
         patch("wall_display.WallDisplayApp._generate_menu_surface") as mock_gen_surf:
        
        app = WallDisplayApp(menu_data_dir="menu-data")
        
        # Assertions
        assert mock_pygame.init.called
        assert app.disp_w == 1920
        assert len(app.menu_items) == 2
        assert app.menu_items[0].menu_name == "Nature"
        assert app.current_item_index == 0
        
        # Checks if images were loaded (iterdir mocked)
        # Since iterdir returned 1 file, images should have size 1
        assert len(app.menu_items[0].images) == 1

def test_app_initialization_no_menu_file(mock_pygame):
    """Tests if the app exits (sys.exit) when the menu file does not exist."""
    with patch("pathlib.Path.exists", return_value=False):
        # We expect the app to call sys.exit(1)
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            WallDisplayApp()
        
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1

def test_load_images_ignores_non_jpg(mock_pygame):
    """Tests if the image loader ignores files that are not JPG."""
    with patch('wall_display.pygame'):
        app = WallDisplayApp.__new__(WallDisplayApp)
        app.menu_data_path = Path("dummy")

        # Simulates a directory with 1 jpg and 1 txt
        files = [Path("photo.jpg"), Path("note.txt")]
        
        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.iterdir", return_value=files), \
             patch("wall_display.pygame.image.load") as mock_load:
            
            # Execute
            images = app._load_images_from_dir(Path("dummy/dir"))
            
            # Should only attempt to load the jpg
            assert mock_load.call_count == 1
            args, _ = mock_load.call_args
            assert str(args[0]) == "photo.jpg"
            # The TXT should be ignored, so the images list should have size 1
            assert len(images) == 1

def test_navigation_logic(mock_pygame, sample_menu_data):
    """Tests the menu index change (UP/DOWN)."""
    with patch("pathlib.Path.exists", return_value=True), \
         patch("pathlib.Path.open", mock_open(read_data=sample_menu_data)), \
         patch("pathlib.Path.iterdir", return_value=[]), \
         patch("wall_display.WallDisplayApp._generate_menu_surface"):
         
        app = WallDisplayApp()
        
        # Initially index 0
        assert app.current_item_index == 0
        
        # Simulates the logic of pressing DOWN (increments index)
        # Copying the run() logic: index = (index + 1) % len
        app.current_item_index = (app.current_item_index + 1) % len(app.menu_items)
        app._change_category()
        
        assert app.current_item_index == 1
        assert app.current_item.menu_name == "City"
        
        # Simulates pressing DOWN again (returns to 0 - loop)
        app.current_item_index = (app.current_item_index + 1) % len(app.menu_items)
        assert app.current_item_index == 0