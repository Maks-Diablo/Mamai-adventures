import pygame

import Level1
import Level2

pygame.init()

if Level1.LEVEL == 0:
    Level1.main_game()
if Level2.LEVEL == 0:
    Level2.main_game()

# выход из pygame
pygame.quit()
