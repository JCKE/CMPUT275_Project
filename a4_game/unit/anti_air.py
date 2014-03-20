from unit.ground_unit import GroundUnit
import unit, helper, effects
from tiles import Tile
import pygame

class AntiAir(GroundUnit):
    """
    An AA gun. Ineffective against ground units, but it does wonders to protect
    troops from aircraft of all kinds.
    
    Armour: Medium
    Speed: Medium
    Range: Medium
    Damage: Low (High against aircraft)
    
    Other notes:
    - Moves fastest on roads, and is slightly slowed on softer terrain.
    - Moves very slowly on mountains.
    - Too large to move through forests.
    """
    sprite = pygame.image.load("assets/anti_air.png")
    
    def __init__(self, **keywords):
        #load the image for the base class.
        self._base_image = AntiAir.sprite

        #load the base class
        super().__init__(**keywords)
        
        #sounds
        self.move_sound = "TankMove"
        self.hit_sound = "MachineGunFire"

        #set unit specific things.
        self.type = "Anti-Air"
        self.speed = 6
        self.max_atk_range = 4
        self.damage = 2
        self.bonus_damage = 7
        self.defense = 2
        self.hit_effect = effects.Ricochet
        
        self._move_costs = {'plains': 1.5,
                             'sand': 1.5,
                             'road': 1,
                             'mountain': 3}
        
    def is_passable(self, tile, pos):
        """
        Returns whether or not this unit can move over a certain tile.
        """
        #Check superclass to see if it's passable first
        if not super().is_passable(tile, pos):
            return False

        #This unit can't pass these specific terrains
        if (tile.type == 'forest'):
            return False
        
        #The tile is passable
        return True
        
    def get_damage(self, target, target_tile):
        """
        Returns the potential attack damage against a given enemy.
        
        This overrides the super class function to allow
        special damage effects.
        """
        # Do bonus damage to air units
        if isinstance(target, unit.air_unit.AirUnit):
            # Calculate the total damage
            damage = self.damage + self.bonus_damage
            
            # Get the unit's current defense
            defense = target.get_defense(tile = target_tile)
            
            # Don't do negative damage
            if (damage - defense < 0):
                return 0
            
            return damage - defense
        else: return super().get_damage(target, target_tile)

unit.unit_types["Anti-Air"] = AntiAir
