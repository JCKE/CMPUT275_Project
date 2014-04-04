from unit.immobile_unit import ImmobileUnit
import unit, helper, effects
from tiles import Tile
import pygame

class Shipyard(ImmobileUnit):
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
        self.speed = 0
        self.health = 30
        self.max_atk_range = 0
        self.damage = 0
        self.defense = 2
        self.hit_effect = effects.Explosion
        self.health = 30
        
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


unit.unit_types["Shipyard"] = Shipyard
