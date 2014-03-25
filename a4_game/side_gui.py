import sys, pygame

from pygame.sprite import LayeredUpdates
from collections import namedtuple

import unit
from unit import *
from sounds import SoundManager

# Sound names
SELECT_SOUND = "Select"
BUTTON_SOUND = "Button"

# Gui panel size information
WIDTH = 200
BUTTON_HEIGHT = 50

# Set the fonts
pygame.font.init()
FONT_SIZE = 16
BIG_FONT_SIZE = 42
FONT = pygame.font.SysFont("Arial", FONT_SIZE)
BIG_FONT = pygame.font.SysFont("Arial", BIG_FONT_SIZE)
BIG_FONT.set_bold(True)

