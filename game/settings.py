from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60
WINDOW_TITLE = "Space Platformer"
AUDIO_SAMPLE_RATE = 44100
AUDIO_VOLUME = 0.25

BACKGROUND_PATH = ASSETS_DIR / "Backgrounds" / "Nebula Aqua-Pink.png"
TILE_PATH = ASSETS_DIR / "Tile" / "Metal tile · 32×32.png"
TRAP_PATH = ASSETS_DIR / "Electric Trap 1.png"
LASER_PATH = ASSETS_DIR / "Laser.png"
PORTAL_PATH = ASSETS_DIR / "Portal · pixel rift.png"
CRYSTAL_FRAME_PATHS = tuple(
    ASSETS_DIR / "Crystal" / f"purple_crystal_{index:04d}.png"
    for index in range(4)
)
HUD_CRYSTAL_PATH = ASSETS_DIR / "Crystal" / "purple_crystal_0001.png"
CRYSTAL_COUNTER_HUD_PATH = ASSETS_DIR / "Crystal Counter.png"
LEVEL_LABEL_HUD_PATHS = tuple(
    ASSETS_DIR / f"Level {index} Label HUD.png"
    for index in range(1, 4)
)
PLAYER_SHEET_PATH = (
    ASSETS_DIR / "Main Character" / "astronaut_spritesheet_transparent.png"
)
FONT_PATH = ASSETS_DIR / "fonts" / "PressStart2P-Regular.ttf"

PLAYER_FRAME_WIDTH = 32
PLAYER_FRAME_HEIGHT = 48
PLAYER_SCALE = 2
PLAYER_SPEED = 260
PLAYER_JUMP_SPEED = 620
GRAVITY = 1700
GROUND_HEIGHT = 64
