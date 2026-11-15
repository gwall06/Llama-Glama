LLAMA SPACE PROGRAMME - INTEGRATED VERSION
=========================================

WHAT CHANGED
------------
The game now has one Pygame lifecycle controlled by main.py:

- main.py calls pygame.init() once and creates one 1280 x 720 display.
- The title screen, cutscenes, shops, Blackjack, rocket flight, and Mars
  exploration all reuse that same display surface.
- The individual stages no longer call pygame.init(),
  pygame.display.set_mode(), or pygame.quit().
- Phase 1 and Blackjack can hand control back and forth without restarting
  Pygame. Shared money, resources, and inventory continue to use
  global_variables.py.
- test.py is kept as an optional biome-map preview helper; it accepts an
  existing display surface and does not create or close Pygame itself.

RUNNING THE GAME
----------------
1. Keep all files and asset folders together as they are in this package.
2. Install the required Python packages:

       python -m pip install -r requirements.txt

3. Start the game from this folder:

       python main.py

DISPLAY
-------
The shared display is a fixed 1280 x 720 window. This matches the existing
hard-coded shop and Mars layouts, so the phases remain aligned while sharing
one display.

DEPENDENCIES
------------
- Python 3.10 or newer
- Pygame
- Pillow (used by the rocket-flight phase)

NOTES
-----
The source files were syntax-checked after integration. The game could not be
launched in the build environment because Pygame is not installed there, so a
full interactive play-through has not been verified here.

LATEST GAMEPLAY UPDATES
-----------------------
- Starting cash is £125,000.
- Press ESC while outside the shops to continue to the next phase.
- The shop area supports mouse selection and keyboard navigation. Use
  WASD or the arrow keys, then ENTER to open a shop; inside, use UP/DOWN
  (or W/S) to choose an item and ENTER to buy it. LEFT/RIGHT (or A/D)
  changes to the neighbouring shop.
- Phase 2 now ends at 25,000 metres (25 km).
- Phase 2 firing requires the Laser blaster from the Electronics shop.
  SPACE fires only when that item is in the shared inventory.
- Phase 2 rocket controls: A/D or LEFT/RIGHT to steer, W/UP to accelerate,
  and S/DOWN to slow down.
- Phase 3 movement supports both WASD and the arrow keys.
- Phase 3 checks the actual inventory when the phase begins, so a dome
  bought in Phase 1 is recognised correctly.
- The title, cutscenes, Blackjack opening choice, and shop navigation also
  support keyboard interaction.
