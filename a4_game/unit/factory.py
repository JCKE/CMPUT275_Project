from unit.construction_unit import ConstructionUnit
import unit, helper, effects
from tiles import Tile
import pygame

class Factory(ConstructionUnit):
    """
    A factory. High health, this is the life blood of your army.
    It allows you to create ground units and other bases.    
    """
    sprite = pygame.image.load("assets/factory.png")
    
    def __init__(self, **keywords):
        #load the image for the base class.
        self._base_image = Factory.sprite

        #load the base class
        super().__init__(**keywords)

        #sounds

        #set unit specific things.
        self.type = "Factory"
        self.speed = 1
        self.health = 30
        self.max_atk_range = 0
        self.damage = 0
        self.defense = 2
        self.hit_effect = effects.Explosion

    def price(): return (0,0,0)

unit.unit_types["Factory"] = Factory
