from unit.construction_unit import ConstructionUnit
import unit, helper, effects
from tiles import Tile
import pygame

class Airstrip(ConstructionUnit):
    """
    An airstrip. High health, this is the life blood of your airforce.
    It allows you to create air units.

    
    Other notes:
    - Can make air and ground defenses to protect itself but
      only within a certain radius.
    """
    sprite = pygame.image.load("assets/airstrip.png")
    
    def __init__(self, **keywords):
        #load the image for the base class.
        self._base_image = Airstrip.sprite

        #load the base class
        super().__init__(**keywords)

        #sounds

        #set unit specific things.
        self.type = "Airstrip"
        self.speed = 1
        self.health = 30
        self.max_atk_range = 0
        self.damage = 0
        self.defense = 2
        self.hit_effect = effects.Explosion
        

unit.unit_types["Airstrip"] = Airstrip
