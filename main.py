import pygame
from Core.GameLoop import GameLoop

def main():
    print(pygame.font.get_fonts())
    game = GameLoop()
    game.run()

if __name__ == "__main__":
    main()