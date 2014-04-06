from unit.construction_unit import ConstructionUnit
import unit, helper, effects
from tiles import Tile
import pygame

class StartFlag(ConstructionUnit):
    """
    A start flag. Used to give player
    some options in choosing where to
    place their starting base.
    """
    sprite = pygame.image.load("assets/startflag.png")
    
    def __init__(self, **keywords):
        #load the image for the base class.
        self._base_image = StartFlag.sprite

        #load the base class
        super().__init__(**keywords)

        #sounds

        #set unit specific things.
        self.type = "StartFlag"
        self.speed = 10
        self.max_atk_range = 0
        self.damage = 0
        self.defense = 3
        self.health = 30


                                     
    def can_hit(self, target_unit):
        """
        Determines whether a unit can hit another unit.
        
        Overrides because tanks can't hit planes.
        """
        return False
            

    def can_turn_end(self):
        """
        Returns whether the player turn can end.
        """
        # We haven't created the base, so we can't finish the turn
        if (not self.turn_state[0] and
            self._active):
            return False
        
        # Default to the superclass
        return super().can_turn_end()


unit.unit_types["StartFlag"] = StartFlag
