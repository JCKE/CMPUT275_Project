from unit.ground_unit import GroundUnit
import unit, helper, effects
from tiles import Tile
import pygame

class Base(GroundUnit):
    """
    A base. High health, this is the life blood of your army.
    It allows you to create units.
    
    Other notes:
    - Can make air and ground defenses to protect itself but
      only within a certain radius.
    """
    sprite = pygame.image.load("assets/base.png")
    
    def __init__(self, **keywords):
        #load the image for the base class.
        self._base_image = Base.sprite

        #load the base class
        super().__init__(**keywords)

        #sounds

        #set unit specific things.
        self.type = "Base"
        self.speed = 5
        self.health = 30
        self.max_atk_range = 0
        self.damage = 0
        self.defense = 2
        self.hit_effect = effects.Explosion

        
    def can_hit(self, target_unit):
        """
        Determines whether a unit can hit another unit.
        
        Overrides because base can't hit anything.
        Defenses are a separate class.
        """
        # If it's an air unit return false
        if isinstance(target_unit, unit.air_unit.AirUnit):
            return True
            
        # Can't hit anything
        return False

    def is_passable(self, tile, pos):
        """
        Returns whether or not this unit can move over a certain tile.
        """
        #Check superclass to see if it's passable first
        if not super().is_passable(tile, pos):
            return False

        """
        #This unit can't pass these specific terrains
        if (tile.type == 'mountain' or
            tile.type == 'forest'):
            return False
        
        #The tile is passable
        return True
        """
        return False


unit.unit_types["Base"] = Base
