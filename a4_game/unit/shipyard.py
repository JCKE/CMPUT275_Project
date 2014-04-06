from unit.construction_unit import ConstructionUnit
import unit, helper, effects
from tiles import Tile
import pygame

class Shipyard(ConstructionUnit):
    """
    A shipyard. High health, this is the life blood of your navy.
    It allows you to create water units.
    
    Other notes:
    - Can make air and ground defenses to protect itself but
      only within a certain radius.
    """
    sprite = pygame.image.load("assets/shipyard.png")
    
    def __init__(self, **keywords):
        #load the image for the base class.
        self._base_image = Shipyard.sprite

        #load the base class
        super().__init__(**keywords)

        #sounds

        #set unit specific things.
        self.type = "Shipyard"
        self.speed = 1
        self.health = 30
        self.max_atk_range = 0
        self.damage = 0
        self.defense = 2
        self.hit_effect = effects.Explosion
        self.health = 30
        
    def is_buildable(self, tile, pos):
        """
        Returns whether or not this unit can build another unit there.
        """
        # Make sure it's a tile
        if not tile:
            return False

        # This unit can build on these specific terrains
        if (tile.type == 'water'):
            return True
        else:
        # Can't build on anything else
            return False

    def price(): return (200, 200, 200)

unit.unit_types["Shipyard"] = Shipyard
