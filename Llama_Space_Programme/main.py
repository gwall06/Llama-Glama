"""Main entry point for the Llama Space Programme.

Pygame is initialised once here. Every game stage receives and reuses the
same display surface; individual stages never call pygame.init(),
pygame.display.set_mode(), or pygame.quit().
"""

import os
import pygame

from cutscene import run_cutscene
from title import run_title_screen


def main():
    game_folder = os.path.dirname(os.path.abspath(__file__))
    os.chdir(game_folder)

    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Totally Accurate Spaceflight Simulator")

    try:
        # Import the game stages only after the shared display exists.
        # Their module-level assets and fonts can then use the active display.
        import phase1
        import gambling
        import phase2
        import phase3

        print("Starting Title Screen...")
        if not run_title_screen(screen):
            return

        opening_cutscenes = [
            (
                "cutscene1.png", "sprite.png",
                "You are Professor Leopold Livingstone Llama, a lecturer emeritus in mammalian 17th Century literature. But in your many readings and musings of critical theory, you discovered a terrible truth...",
                "pan_left", 1.1, (100, 400)
            ),
            (
                "cutscene2.png", "sprite2.png",
                "Many animals have travelled into space. Dogs. Monkeys. Cats. Even the humble tardigrade...",
                "pan_right", 1.1, (100, 400)
            ),
            (
                "cutscene3.png", "sprite3.png",
                "But despite President L Bee J's civil rights advancements, no llamas have ever been to space...",
                "zoom_in", 0.8, (600, 200)
            ),
            (
                "cutscene4.png", "sprite2.png",
                "Inspired by the LLM movement, you seek to right this historic wrong...",
                "pan_right", 0.4, None
            ),
            (
                "cutscene5.png", "sprite2.png",
                "You must build your rocket, travel to Mars, and conquer space for the llama race.",
                "pan_left", 0.4, None
            ),
        ]

        for index, scene in enumerate(opening_cutscenes, start=1):
            print(f"Starting Cutscene {index}...")
            background, sprite, dialogue, motion, scale, position = scene
            if not run_cutscene(
                screen, background, sprite, dialogue, motion,
                sprite_scale=scale, sprite_position=position
            ):
                return

        # Phase 1 can return to the shop after Blackjack as many times as
        # the player chooses. It never shuts down or recreates Pygame.
        while True:
            print("Starting Phase 1...")
            gambling_requested = phase1.run_phase1(screen)

            if gambling_requested is None:
                return

            if not gambling_requested:
                print("Phase 1 finished. Continuing to the next cutscene...")
                break

            print("Starting The Golden Ace - Blackjack...")
            if not gambling.run_blackjack(screen):
                return
            print("Returning to Phase 1...")

        print("Starting Cutscene 7...")
        if not run_cutscene(
            screen,
            "cutscene7.png",
            "sprite7.png",
            "You must build your rocket, travel to Mars, and conquer space for the llama race...",
            "zoom_in",
            sprite_scale=0.8,
            sprite_position=(400, 400)
        ):
            return

        print("Starting Phase 2...")
        if not phase2.run_phase2(screen):
            return

        print("Starting Phase 2 to Phase 3 Cutscene...")
        if not run_cutscene(
            screen,
            "cutscene5.png",
            "sprite7.png",
            "Congratulations! Your mission has brought you one step closer to the stars. But the real adventure is only just beginning...",
            "zoom_in",
            sprite_scale=0.8,
            sprite_position=(400, 400)
        ):
            return

        print("Starting Phase 3...")
        if not phase3.run_phase3(screen):
            return

        print("Game finished!")

    finally:
        # This is the only place in the game that shuts Pygame down.
        try:
            pygame.mixer.music.stop()
        except pygame.error:
            pass
        pygame.quit()


if __name__ == "__main__":
    main()
