# Space Platformer

A small Pygame starter project using the existing pixel-art assets.

## Setup

From the project folder, create and activate a virtual environment, then install
the dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

```powershell
python main.py
```

The game opens in a 1280×720 window while keeping its 16:9 pixel-art layout.
The main menu opens a three-level selector and a **Controls** page. Menus work
with the mouse or keyboard: use **Up/Down** and **Enter** to select an option.
In-game, **A/D** or the **arrow keys** move, **Space**, **W**, or **Up** jumps,
and **Escape** opens the pause menu. Reach the portal to advance, collect
crystals, and avoid lasers and electric traps. Touching a hazard or falling
off-screen returns you to the current level's starting platform.
Short synthesized sound effects play for menu actions, jumps, crystal
collections, death, and portals. They use Pygame's mixer and do not require
additional audio files or Python packages.

## Project layout

```text
assets/
  Backgrounds/
  Crystal/
  Main Character/
  Tile/
  fonts/
game/
  audio.py        # synthesized menu and gameplay sound effects
  player.py       # spritesheet slicing, animation, movement, and collisions
  levels.py       # level layouts, platforms, hazards, crystals, and portals
  settings.py     # window, physics, audio, and asset paths
main.py           # game loop and demo scene
requirements.txt
```

The astronaut sheet is treated as a 6-column by 3-row grid of 32×48 frames:
2 idle frames, 6 running frames, and 3 jumping frames. Animation frame
coordinates are declared in `game/player.py` and can be adjusted there if the
sheet's animation layout changes.

The bundled Press Start 2P font is distributed under the SIL Open Font License;
its license text is in `assets/fonts/OFL.txt`.
