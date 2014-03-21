from unit.water_unit import WaterUnit
import unit, helper, effects
from tiles import Tile
import pygame

class Carrier(WaterUnit):
    """
    An aircraft carrier. Not designed for battle; instead, it provides a spot
    for up to 4 aircraft to dock.
    
    Armour: Medium
    Speed: Low
    Range: Low
    Damage: Low
    
    Other notes:
    - Aircraft can stop moving and refuel on any of the 4 tiles adjacent to this
      unit.
    """
    sprite = pygame.image.load("assets/carrier.png")
    
    def __init__(self, **keywords):
        #load the image for the base class.
        self._base_image = Carrier.sprite

        #load the base class
        super().__init__(**keywords)
        
        #sounds
        self.hit_sound = "MachineGunFire"

        #set unit specific things.
        self.type = "Carrier"
        self.speed = 4
        self.max_atk_range = 2
        self.damage = 4
        self.defense = 2
        self.hit_effect = effects.Ricochet

unit.unit_types["Carrier"] = Carrier
