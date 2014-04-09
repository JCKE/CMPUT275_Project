import sys, pygame, serial
import random

from pygame.sprite import LayeredUpdates
from collections import namedtuple

import tiles, unit, animation
from unit import *
from effects.explosion import Explosion
from sounds import SoundManager
import analyze


# Sound names
SELECT_SOUND = "Select"
BUTTON_SOUND = "Button"

# GUI size information
MAP_WIDTH = 600
BAR_WIDTH = 200
BUTTON_HEIGHT = 50
UNIT_BUTTON_HEIGHT = 35
CENTER = 100
UNITS_BARW = 115
NUM_UNIT_BUTTONS = 12

# Set the fonts
pygame.font.init() 
FONT_SIZE = 16
BIG_FONT_SIZE = 42
FONT = pygame.font.SysFont("Arial", FONT_SIZE)
BIG_FONT = pygame.font.SysFont("Arial", BIG_FONT_SIZE)
BIG_FONT.set_bold(True)

# padding for left and top side of the bar
PAD = 6

# Speed of reticle blinking
RETICLE_RATE = 0.02

# RGBA colors for grid stuff
SELECT_COLOR = (255, 255, 0, 255)
UNMOVED_COLOR = (0, 0, 0, 255)
MOVE_COLOR_A = (0, 0, 160, 120)
MOVE_COLOR_B = (105, 155, 255, 160)
ATK_COLOR_A = (255, 0, 0, 140)
ATK_COLOR_B = (220, 128, 0, 180)
BLD_COLOR_A = (255, 240, 0, 80)
BLD_COLOR_B = (252, 255, 0, 140)

# RGB colors for the GUI
FONT_COLOR = (0, 0, 0)
BAR_COLOR = (150, 150, 150)
OUTLINE_COLOR = (50, 50, 50)
BUTTON_HIGHLIGHT_COLOR = (255, 255, 255)
BUTTON_DISABLED_COLOR = (64, 64, 64)

# Names for the different teams
TEAM_NAME = {
    0: "green",
    1: "red"
}

# Possible GUI modes
# http://stackoverflow.com/questions/702834/whats-the-common-practice-
# for-enums-in-python
class Modes:
    Begin, Select, ChooseMove, Moving, ChooseAttack, GameOver, Build, ChooseSpot = range(8)

# A container class which stores button information.
# Each "slot" is a BUTTON_HEIGHT pixel space counting up from the bottom
# of the screen.
Button = namedtuple('Button', ['slot', 'text', 'onClick', 'condition', 'price'])

class GUI(LayeredUpdates):
    """
    This class handles user input, and is also responsible for 
    rendering objects on-screen (including converting unit tile 
    positions into on-screen positions). Essentially, it is the 
    middleman between objects and the actual tilemap.
    """ 
    # number of GUI instances
    num_instances = 0
            
    # These functions need to be defined ahead of __init__ because
    # they're passed as references in the buttons.
    def can_move(self):
        """
        Checks whether the move button can be pressed.
        """
        # If no unit is selected, we obviously can't.
        if not self.sel_unit: return False
        
        # If the unit is done its move, we also can't.
        return not self.sel_unit.turn_state[0]
    
    def can_attack(self):
        """
        Checks whether the attack button can be pressed.
        """
        # If no unit is selected, we obviously can't.
        if not self.sel_unit: return False
        
        # If the unit is done its attack, we also can't.
        return not self.sel_unit.turn_state[1]
   
    def can_build_ground_units(self):
        """
        Checks whether the Factory is selected. 
        """
        # If the Factory unit is selected then we can
        # use ground units.
        # Otherwise we can't use the buttons.
        if self.sel_unit:
            type = self.sel_unit.type
            if type != "Factory": return False
        return self.sel_unit

    def can_build_air_units(self):
        """
        Checks whether the airstrip is selected. 
        """
        # If the airstrip unit is selected then
        # we can build air units.
        # Otherwise we can't use the buttons.
        if self.sel_unit:
            type = self.sel_unit.type
            if type != "Airstrip": return False
        return self.sel_unit

    def can_build_water_units(self):
        """
        Checks whether the shipyard is selected. 
        """
        # If the shipyard unit is selected then we can
        # use water units.
        # Otherwise we can't use the buttons.
        if self.sel_unit:
            type = self.sel_unit.type
            if type != "Shipyard": return False
        return self.sel_unit

    def can_build_factory(self):
        """
        Checks whether the startflag is selected.
        """
        # If the startflag unit is selected then we can
        # use the factory unit.
        # Otherwise we can't use the buttons.
        if self.sel_unit:
            type = self.sel_unit.type
            if type != "StartFlag": return False
        return self.sel_unit
        
    def check_resources(self):
        """
        Makes sure players can't use negative resources.
        """
        if self.cur_team == 0:

            if self.current_button == "Tank":
                if self.gteam_gold - unit.tank.Tank.price()[0] < 0:
                    return False
                elif self.gteam_wood - unit.tank.Tank.price()[1] < 0:
                    return False
                elif self.gteam_food - unit.tank.Tank.price()[2] < 0:
                    return False
                else:
                    return True

            elif self.current_button == "Anti-Air":
                if self.gteam_gold - unit.anti_air.AntiAir.price()[0] < 0:
                    return False
                elif self.gteam_wood - unit.anti_air.AntiAir.price()[1] < 0:
                    return False
                elif self.gteam_food - unit.anti_air.AntiAir.price()[2] < 0:
                    return False
                else:
                    return True

            elif self.current_button == "Jeep":
                if self.gteam_gold - unit.jeep.Jeep.price()[0] < 0:
                    return False
                elif self.gteam_wood - unit.jeep.Jeep.price()[1] < 0:
                    return False
                elif self.gteam_food - unit.jeep.Jeep.price()[2] < 0:
                    return False                
                else:
                    return True

            elif self.current_button == "Anti-Armour":
                if self.gteam_gold - unit.anti_armour.AntiArmour.price()[0] < 0:
                    return False
                elif self.gteam_wood - unit.anti_armour.AntiArmour.price()[1] < 0:
                    return False
                elif self.gteam_food - unit.anti_armour.AntiArmour.price()[2] < 0:
                    return False
                else:
                    return True

            elif self.current_button == "Artillery":
                if self.gteam_gold - unit.artillery.Artillery.price()[0] < 0:
                    return False
                elif self.gteam_wood - unit.artillery.Artillery.price()[1] < 0:
                    return False
                elif self.gteam_food - unit.artillery.Artillery.price()[2] < 0:
                    return False                
                else:
                    return True

            elif self.current_button == "Bomber":
                if self.gteam_gold - unit.bomber.Bomber.price()[0] < 0:
                    return False
                elif self.gteam_wood - unit.bomber.Bomber.price()[1] < 0:
                    return False
                elif self.gteam_food - unit.bomber.Bomber.price()[2] < 0:
                    return False
                else:
                    return True

            elif self.current_button == "Fighter":
                if self.gteam_gold - unit.fighter.Fighter.price()[0] < 0:
                    return False
                elif self.gteam_wood - unit.fighter.Fighter.price()[1] < 0:
                    return False
                elif self.gteam_food - unit.fighter.Fighter.price()[2] < 0:
                    return False
                else:
                    return True

            elif self.current_button == "Carrier":
                if self.gteam_gold - unit.carrier.Carrier.price()[0] < 0:
                    return False
                elif self.gteam_wood - unit.carrier.Carrier.price()[1] < 0:
                    return False
                elif self.gteam_food - unit.carrier.Carrier.price()[2] < 0:
                    return False
                else:
                    return True

            elif self.current_button == "Battleship":
                if self.gteam_gold - unit.battleship.Battleship.price()[0] < 0:
                    return False
                elif self.gteam_wood - unit.battleship.Battleship.price()[1] < 0:
                    return False
                elif self.gteam_food - unit.battleship.Battleship.price()[2] < 0:
                    return False
                else:
                    return True

            elif self.current_button == "Shipyard":
                if self.gteam_gold - unit.shipyard.Shipyard.price()[0] < 0: 
                    return False 
                elif self.gteam_wood - unit.shipyard.Shipyard.price()[1] < 0:
                    return False 
                elif self.gteam_food - unit.shipyard.Shipyard.price()[2] < 0:
                    return False
                else:
                    return True

            elif self.current_button == "Airstrip":
                if self.gteam_gold - unit.airstrip.Airstrip.price()[0] < 0: 
                    return False 
                elif self.gteam_wood - unit.airstrip.Airstrip.price()[1] < 0:
                    return False 
                elif self.gteam_food - unit.airstrip.Airstrip.price()[2] < 0:
                    return False
                else:
                    return True
            else:
                return True

        elif self.cur_team == 1:

            if self.current_button == "Tank":
                if self.rteam_gold - unit.tank.Tank.price()[0] < 0:
                    return False
                elif self.rteam_wood - unit.tank.Tank.price()[1] < 0:
                    return False
                elif self.rteam_food - unit.tank.Tank.price()[2] < 0:
                    return False
                else:
                    return True

            elif self.current_button == "Anti-Air":
                if self.rteam_gold - unit.anti_air.AntiAir.price()[0] < 0:
                    return False
                elif self.rteam_wood - unit.anti_air.AntiAir.price()[1] < 0:
                    return False
                elif self.rteam_food - unit.anti_air.AntiAir.price()[2] < 0:
                    return False
                else:
                    return True

            elif self.current_button == "Jeep":
                if self.rteam_gold - unit.jeep.Jeep.price()[0] < 0:
                    return False
                elif self.rteam_wood - unit.jeep.Jeep.price()[1] < 0:
                    return False
                elif self.rteam_food - unit.jeep.Jeep.price()[2] < 0:
                    return False                
                else:
                    return True

            elif self.current_button == "Anti-Armour":
                if self.rteam_gold - unit.anti_armour.AntiArmour.price()[0] < 0:
                    return False
                elif self.rteam_wood - unit.anti_armour.AntiArmour.price()[1] < 0:
                    return False
                elif self.rteam_food - unit.anti_armour.AntiArmour.price()[2] < 0:
                    return False
                else:
                    return True

            elif self.current_button == "Artillery":
                if self.rteam_gold - unit.artillery.Artillery.price()[0] < 0:
                    return False
                elif self.rteam_wood - unit.artillery.Artillery.price()[1] < 0:
                    return False
                elif self.rteam_food - unit.artillery.Artillery.price()[2] < 0:
                    return False                
                else:
                    return True

            elif self.current_button == "Bomber":
                if self.rteam_gold - unit.bomber.Bomber.price()[0] < 0:
                    return False
                elif self.rteam_wood - unit.bomber.Bomber.price()[1] < 0:
                    return False
                elif self.rteam_food - unit.bomber.Bomber.price()[2] < 0:
                    return False
                else:
                    return True

            elif self.current_button == "Fighter":
                if self.rteam_gold - unit.fighter.Fighter.price()[0] < 0:
                    return False
                elif self.rteam_wood - unit.fighter.Fighter.price()[1] < 0:
                    return False
                elif self.rteam_food - unit.fighter.Fighter.price()[2] < 0:
                    return False
                else:
                    return True

            elif self.current_button == "Carrier":
                if self.rteam_gold - unit.carrier.Carrier.price()[0] < 0:
                    return False
                elif self.rteam_wood - unit.carrier.Carrier.price()[1] < 0:
                    return False
                elif self.rteam_food - unit.carrier.Carrier.price()[2] < 0:
                    return False
                else:
                    return True

            elif self.current_button == "Battleship":
                if self.rteam_gold - unit.battleship.Battleship.price()[0] < 0:
                    return False
                elif self.rteam_wood - unit.battleship.Battleship.price()[1] < 0:
                    return False
                elif self.rteam_food - unit.battleship.Battleship.price()[2] < 0:
                    return False
                else:
                    return True

            elif self.current_button == "Shipyard":
                if self.rteam_gold - unit.shipyard.Shipyard.price()[0] < 0: 
                    return False 
                elif self.rteam_wood - unit.shipyard.Shipyard.price()[1] < 0:
                    return False 
                elif self.rteam_food - unit.shipyard.Shipyard.price()[2] < 0:
                    return False
                else:
                    return True

            elif self.current_button == "Airstrip":
                if self.rteam_gold - unit.airstrip.Airstrip.price()[0] < 0: 
                    return False 
                elif self.rteam_wood - unit.airstrip.Airstrip.price()[1] < 0:
                    return False 
                elif self.rteam_food - unit.airstrip.Airstrip.price()[2] < 0:
                    return False
                else:
                    return True
            else:
                return True
        else:
            raise Exception("Where is your team?")

    def renew_resources(self, unit_name):
        """
        Updates resources if unit is deleted.
        Gives back half of original price.
        """
        if self.cur_team == 0:

            if unit_name == "Tank":
                self.gteam_gold += unit.tank.Tank.price()[0] // 2
                self.gteam_wood += unit.tank.Tank.price()[1] // 2
                self.gteam_food += unit.tank.Tank.price()[2] // 2

            elif unit_name == "Anti-Air":
                self.gteam_gold += unit.anti_air.AntiAir.price()[0] // 2
                self.gteam_wood += unit.anti_air.AntiAir.price()[1] // 2
                self.gteam_food += unit.anti_air.AntiAir.price()[2] // 2

            elif unit_name == "Jeep":
                self.gteam_gold += unit.jeep.Jeep.price()[0] // 2
                self.gteam_wood += unit.jeep.Jeep.price()[1] // 2
                self.gteam_food += unit.jeep.Jeep.price()[2] // 2
                
            elif unit_name == "Anti-Armour":
                self.gteam_gold += unit.anti_armour.AntiArmour.price()[0] // 2
                self.gteam_wood += unit.anti_armour.AntiArmour.price()[1] // 2
                self.gteam_food += unit.anti_armour.AntiArmour.price()[2] // 2
                
            elif unit_name == "Artillery":
                self.gteam_gold += unit.artillery.Artillery.price()[0] // 2
                self.gteam_wood += unit.artillery.Artillery.price()[1] // 2
                self.gteam_food += unit.artillery.Artillery.price()[2] // 2
                 
            elif unit_name == "Bomber":
                self.gteam_gold += unit.bomber.Bomber.price()[0] // 2
                self.gteam_wood += unit.bomber.Bomber.price()[1] // 2
                self.gteam_food += unit.bomber.Bomber.price()[2] // 2
                
            elif unit_name == "Fighter":
                self.gteam_gold += unit.fighter.Fighter.price()[0] // 2
                self.gteam_wood += unit.fighter.Fighter.price()[1] // 2
                self.gteam_food += unit.fighter.Fighter.price()[2] // 2
                
            elif unit_name == "Carrier":
                self.gteam_gold += unit.carrier.Carrier.price()[0] // 2
                self.gteam_wood += unit.carrier.Carrier.price()[1] // 2
                self.gteam_food += unit.carrier.Carrier.price()[2] // 2

            elif unit_name == "Battleship":
                self.gteam_gold += unit.battleship.Battleship.price()[0] // 2
                self.gteam_wood += unit.battleship.Battleship.price()[1] // 2
                self.gteam_food += unit.battleship.Battleship.price()[2] // 2

            elif unit_name == "Shipyard":
                self.gteam_gold += unit.shipyard.Shipyard.price()[0] // 2 
                self.gteam_wood += unit.shipyard.Shipyard.price()[1] // 2
                self.gteam_food += unit.shipyard.Shipyard.price()[2] // 2
                
            elif unit_name == "Airstrip":
                self.gteam_gold += unit.airstrip.Airstrip.price()[0] // 2 
                self.gteam_wood += unit.airstrip.Airstrip.price()[1] // 2
                self.gteam_food += unit.airstrip.Airstrip.price()[2] // 2
                
        elif self.cur_team == 1:

            if unit_name == "Tank":
                self.rteam_gold += unit.tank.Tank.price()[0] // 2
                self.rteam_wood += unit.tank.Tank.price()[1] // 2
                self.rteam_food += unit.tank.Tank.price()[2] // 2

            elif unit_name == "Anti-Air":
                self.rteam_gold += unit.anti_air.AntiAir.price()[0] // 2
                self.rteam_wood += unit.anti_air.AntiAir.price()[1] // 2
                self.rteam_food += unit.anti_air.AntiAir.price()[2] // 2

            elif unit_name == "Jeep":
                self.rteam_gold += unit.jeep.Jeep.price()[0] // 2
                self.rteam_wood += unit.jeep.Jeep.price()[1] // 2
                self.rteam_food += unit.jeep.Jeep.price()[2] // 2
                
            elif unit_name == "Anti-Armour":
                self.rteam_gold += unit.anti_armour.AntiArmour.price()[0] // 2
                self.rteam_wood += unit.anti_armour.AntiArmour.price()[1] // 2
                self.rteam_food += unit.anti_armour.AntiArmour.price()[2] // 2
                
            elif unit_name == "Artillery":
                self.rteam_gold += unit.artillery.Artillery.price()[0] // 2
                self.rteam_wood += unit.artillery.Artillery.price()[1] // 2
                self.rteam_food += unit.artillery.Artillery.price()[2] // 2
                 
            elif unit_name == "Bomber":
                self.rteam_gold += unit.bomber.Bomber.price()[0] // 2
                self.rteam_wood += unit.bomber.Bomber.price()[1] // 2
                self.rteam_food += unit.bomber.Bomber.price()[2] // 2
                
            elif unit_name == "Fighter":
                self.rteam_gold += unit.fighter.Fighter.price()[0] // 2
                self.rteam_wood += unit.fighter.Fighter.price()[1] // 2
                self.rteam_food += unit.fighter.Fighter.price()[2] // 2
                
            elif unit_name == "Carrier":
                self.rteam_gold += unit.carrier.Carrier.price()[0] // 2
                self.rteam_wood += unit.carrier.Carrier.price()[1] // 2
                self.rteam_food += unit.carrier.Carrier.price()[2] // 2

            elif unit_name == "Battleship":
                self.rteam_gold += unit.battleship.Battleship.price()[0] // 2
                self.rteam_wood += unit.battleship.Battleship.price()[1] // 2
                self.rteam_food += unit.battleship.Battleship.price()[2] // 2

            elif unit_name == "Shipyard":
                self.rteam_gold += unit.shipyard.Shipyard.price()[0] // 2 
                self.rteam_wood += unit.shipyard.Shipyard.price()[1] // 2
                self.rteam_food += unit.shipyard.Shipyard.price()[2] // 2
                
            elif unit_name == "Airstrip":
                self.rteam_gold += unit.airstrip.Airstrip.price()[0] // 2 
                self.rteam_wood += unit.airstrip.Airstrip.price()[1] // 2
                self.rteam_food += unit.airstrip.Airstrip.price()[2] // 2

    def move_pressed(self):
        """
        This is called when the move button is pressed.
        """
        # Switch out of move mode if we're already in it.
        if self.mode == Modes.ChooseMove:
            self.change_mode(Modes.Select)
            return
        
        # If there is no unit selected, nothing happens.
        if not self.sel_unit: return
        # If the unit has already moved nothing happens.
        elif self.sel_unit.turn_state[0] == True: return
        
        # Determine where we can move.
        pos = (self.sel_unit.tile_x, self.sel_unit.tile_y)
        
        # These will be used in pathfinding
        cost = lambda c: (
            self.sel_unit.move_cost(self.map.tile_data(c)))
        passable = lambda c: (
            self.sel_unit.is_passable(self.map.tile_data(c), c))
        
        reachable = tiles.reachable_tiles(
            self.map,
            pos,
            self.sel_unit.speed,
            cost,
            passable)
        
        # Check that the tiles can actually be stopped in
        for t_pos in reachable:
            tile = self.map.tile_data(t_pos)
            
            # This can be stopped in, so add it
            if self.sel_unit.is_stoppable(tile, t_pos):
                self._movable_tiles.add(t_pos)
        
        # Highlight those squares
        self.map.set_highlight(
            "move", MOVE_COLOR_A, MOVE_COLOR_B, self._movable_tiles)
        
        # Set the current GUI mode
        self.change_mode(Modes.ChooseMove)
            
    def attack_pressed(self):
        """
        This is called when the attack button is pressed.
        """
        # Switch out of move mode if we're already in it.
        if self.mode == Modes.ChooseAttack:
            self.change_mode(Modes.Select)
            return
        
        # If there is no unit selected, nothing happens.
        if not self.sel_unit: return
        # If the unit has already attacked, nothing happens.
        elif self.sel_unit.turn_state[1] == True: return
        
        # Get information about the unit and its location.
        unit_pos = (self.sel_unit.tile_x, self.sel_unit.tile_y)
        unit_tile = self.map.tile_data(unit_pos)
        
        # These are all the positions in range of the unit's attack.
        in_range = self.sel_unit.positions_in_range(unit_tile, unit_pos)
        
        # Determine which tiles the unit can actually attack.
        for check_pos in in_range:
            check_tile = self.map.tile_data(check_pos)
            if self.sel_unit.is_attackable(
                unit_tile,
                unit_pos,
                check_tile,
                check_pos):
                self._attackable_tiles.add(check_pos)
        
        # Highlight the attackable tiles
        self.map.set_highlight(
            "attack", ATK_COLOR_A, ATK_COLOR_B, in_range)
            
        # Reset the reticle blinking
        self._reticle.reset()
        
        # Set the current GUI mode
        self.change_mode(Modes.ChooseAttack)
        
    def end_turn_pressed(self):
        """
        This is called when the end turn button is pressed.
        Advances to the next turn.
        """
        # Check if the turn can actually end
        for unit in base_unit.BaseUnit.active_units:
            if unit.team == self.cur_team and not unit.can_turn_end():
                
                # Make sure the game mode is changed back to Select
                self.change_mode(Modes.Select)
                
                # If not, switch to that unit
                self.sel_unit = unit
                return
        
        # reset game mode
        self.change_mode(Modes.Begin)
        
        # unselect unit
        self.sel_unit = None
        
        # Reset the turn states of all units
        for unit in base_unit.BaseUnit.active_units:
            # This is the current team's unit, so call its turn end function
            if unit.team == self.cur_team and not unit.turn_ended():
                    # The unit died! Add its death effect
                    if unit.die_effect:
                        self._effects.add(unit.die_effect(unit.rect.topleft))
        
        # advance turn
        self.current_turn += 1
        
        #Send end turn code

    def build_pressed(self):
        """
        This is called when one of the build buttons is pressed.
        """
        # Switch out of move mode if we're already in it.
        if self.mode == Modes.Build:
            self.change_mode(Modes.Select)
            return

        # Make sure players can't go into the overdraft
        if self.check_resources() == False:
            return

        # If there is no unit selected, nothing happens.
        if not self.sel_unit: return
        # Make sure you pressed a build button
        if self.current_button ==  None: return

        # Determine where we can build.
        pos = (self.sel_unit.tile_x, self.sel_unit.tile_y)
        
        # These will be used in pathfinding
        cost = lambda c: (
            self.sel_unit.move_cost(self.map.tile_data(c)))
        buildable = lambda c: (
            self.sel_unit.is_buildable(self.map.tile_data(c), c))

        # Allow for a bigger build distance from factory for bases
        if self.current_button == "Airstrip":
            self.sel_unit.speed = 5
        elif self.current_button == "Shipyard":
            self.sel_unit.speed = 5
        elif self.current_button == "Factory":
            self.sel_unit.speed = 10
        else:
            self.sel_unit.speed = 2

        available = tiles.reachable_tiles(
            self.map,
            pos,
            self.sel_unit.speed,
            cost,
            buildable)
        
        # Check that the tiles can actually be stopped in
        for t_pos in available:
            tile = self.map.tile_data(t_pos)
            # Can only build a shipyard by the water (i.o.w. on sand tiles)
            if self.current_button == "Shipyard":
                if tile.type == "sand" and self.sel_unit.is_buildable(tile, t_pos):
                    self._buildable_tiles.add(t_pos)
            # This can be stopped in, so add it
            elif self.sel_unit.is_buildable(tile, t_pos):
                self._buildable_tiles.add(t_pos)
        
        # Highlight those squares
        self.map.set_highlight(
            "build", BLD_COLOR_A, BLD_COLOR_B, self._buildable_tiles)
        
        # Set the current GUI mode
        self.change_mode(Modes.ChooseSpot)


    def build_unit(self, pos):
        """
        Handles pressing one of the unit buttons.
        Builds selected unit by your team's base.
        """

        # Create the units

        unit_team = self.cur_team
        unit_angle = 0

        # Make sure you are building at the right base
        if pos in self._buildable_tiles:
            unit_x, unit_y = pos[0], pos[1]
        else:
            raise Exception("Not able to build")
            
        if self.current_button == "Tank":
            unit_name = "Tank"
        elif self.current_button == "Anti-Air":
            unit_name = "Anti-Air"
        elif self.current_button == "Jeep":
            unit_name = "Jeep"
        elif self.current_button == "Anti-Armour":
            unit_name = "Anti-Armour"
        elif self.current_button == "Artillery":
            unit_name = "Artillery"
        elif self.current_button == "Bomber":
            unit_name = "Bomber"
        elif self.current_button == "Fighter":
            unit_name = "Fighter"
        elif self.current_button == "Carrier":
            unit_name = "Carrier"
        elif self.current_button == "Battleship":
            unit_name = "Battleship"
        elif self.current_button == "Shipyard":
            unit_name = "Shipyard"
        elif self.current_button == "Airstrip":
            unit_name = "Airstrip"
        elif self.current_button == "Factory":
            unit_name = "Factory"
            self.sel_unit.deactivate() # Make sure you can only build factory once
        else:
            raise Exception("Either team or unit is wrong team {} unit {}".format(self.cur_team, self.current_button))

        if not unit_name in unit.unit_types:
            raise Exception("No unit of name {} found!".format(unit_name))
        new_unit = unit.unit_types[unit_name](team = unit_team,
                                              tile_x = unit_x,
                                              tile_y = unit_y,
                                              activate = True,
                                              angle = unit_angle)
        # Add the unit to the update group and set its display rect
        self.update_unit_rect(new_unit)
        new_unit._update_image()
        
        # Subtract resources from team after building unit
        if self.cur_team == 0:
            self.gteam_gold -= unit.unit_types[unit_name].price()[0]
            self.gteam_wood -= unit.unit_types[unit_name].price()[1]
            self.gteam_food -= unit.unit_types[unit_name].price()[2]
        elif self.cur_team == 1:
            self.rteam_gold -= unit.unit_types[unit_name].price()[0]
            self.rteam_wood -= unit.unit_types[unit_name].price()[1]
            self.rteam_food -= unit.unit_types[unit_name].price()[2]

        # Deselect to choose what you want to do next
        self.change_mode(Modes.Select)
        self.sel_unit = None



    def __init__(self, screen_rect, bg_color):
        """
        Initialize the display.
        screen_rect: the bounds of the screen
        bg_color: the background color
        """
        LayeredUpdates.__init__(self)

        if GUI.num_instances != 0:
            raise Exception("GUI: can only have one instance of a simulation")
        GUI.num_instances = 1
        
        # Set up the screen
        self.screen = pygame.display.set_mode((screen_rect.w, screen_rect.h))
        self.screen_rect = screen_rect
        
        # The rect containing the info bar
        self.bar_rect = pygame.Rect(screen_rect.w - BAR_WIDTH,
                                     0,
                                     BAR_WIDTH,
                                     screen_rect.h)
        # The rect containing the units buttons
        self.units_bar_rect = pygame.Rect(0,
                                          0,
                                          UNITS_BARW,
                                          screen_rect.h)
        
        # The rect containing the map view
        self.view_rect = pygame.Rect(115,
                                      0,
                                      MAP_WIDTH,
                                      screen_rect.h)
        self.bg_color = bg_color
        self.map = None
        self.newturn = 0

        # Set up team information
        self.num_teams = 2
        self.current_turn = 0
        self.win_team = None 
        self.gteam_gold = 40
        self.gteam_wood = 50
        self.gteam_food = 75
        self.rteam_gold = 40
        self.rteam_wood = 50
        self.rteam_food = 75

        # The currently selected unit
        self.sel_unit = None
        self.check_base = 0
        self.current_button = None

        # Set up GUI
        self.buttons = [
            Button(0, "MOVE", self.move_pressed, self.can_move, None),
            Button(1, "ATTACK", self.attack_pressed, self.can_attack, None),
            Button(2, "END TURN", self.end_turn_pressed, None, None),
            Button(0, "Anti-Air", self.build_pressed, self.can_build_ground_units, unit.anti_air.AntiAir.price()),
            Button(1, "Tank", self.build_pressed, self.can_build_ground_units, unit.tank.Tank.price()),
            Button(2, "Jeep", self.build_pressed, self.can_build_ground_units, unit.jeep.Jeep.price()),
            Button(3, "Anti-Armour", self.build_pressed, self.can_build_ground_units, unit.anti_armour.AntiArmour.price()),
            Button(4, "Artillery", self.build_pressed, self.can_build_ground_units, unit.artillery.Artillery.price()),
            Button(5, "Bomber", self.build_pressed, self.can_build_air_units, unit.bomber.Bomber.price()),
            Button(6, "Fighter", self.build_pressed, self.can_build_air_units, unit.fighter.Fighter.price()),
            Button(7, "Carrier", self.build_pressed, self.can_build_water_units, unit.carrier.Carrier.price()),
            Button(8, "Battleship", self.build_pressed, self.can_build_water_units, unit.battleship.Battleship.price()),
            Button(9, "Shipyard", self.build_pressed, self.can_build_ground_units, unit.shipyard.Shipyard.price()),
            Button(10, "Airstrip", self.build_pressed, self.can_build_ground_units, unit.airstrip.Airstrip.price()),
            Button(11, "Factory", self.build_pressed, self.can_build_factory, unit.factory.Factory.price())]

        # We start in begin mode
        self.mode = Modes.Begin
        
        # Tiles we can move to/attack/build on
        self._movable_tiles = set()
        self._attackable_tiles = set()
        self._buildable_tiles = set()

        # The targeting reticle
        self._reticle = animation.Animation("assets/reticle.png",
                                             20,
                                             20,
                                             RETICLE_RATE)
        
        # This will store effects which are drawn over everything else
        self._effects = pygame.sprite.Group()


    @property
    def cur_team(self):
        """
        Gets the current team based on the turn.
        """
        return (self.current_turn) % self.num_teams
    
    @property
    def cur_day(self):
        """
        Gets the current day based on the turn.
        """
        return (self.current_turn) // self.num_teams + 1
        
    def change_mode(self, new_mode):
        """
        Changes the current mode.
        """
        if self.mode == new_mode:
            return
        
        # Deal with the current mode
        if self.mode == Modes.ChooseMove:
            # Reset the move markers
            self._movable_tiles = set()
            self.map.remove_highlight("move")
        
        # Deal with the current mode
        if self.mode == Modes.ChooseAttack:
            # Reset the move markers
            self._attackable_tiles = set()
            self.map.remove_highlight("attack")

        # Deal with the current mode
        if self.mode == Modes.ChooseSpot:
            self._buildable_tiles = set()
            self.map.remove_highlight("build")

        self.mode = new_mode
        
    def load_level(self, filename):
        """
        Loads a map from the given filename.
        """
        self.remove(self.map)
        
        map_file = open(filename, 'r')
        
        # Move up to the line with the team count
        line = map_file.readline()
        while line.find("Teams: ") < 0:
            line = map_file.readline()
            if line == "":
                raise Exception ("Expected team count")
        
        # Get the number of teams
        line = line.lstrip("Teams: ")
        self.num_teams = int(line)
        
        # Move up to the line with the tile sprites
        line = map_file.readline()
        while line.find("Tiles: ") < 0:
            line = map_file.readline()
            if line == "":
                raise Exception ("Expected tile file")
        
        # Get the number of teams
        line = line.lstrip("Tiles: ")
        line = line.strip()
        tile_filename = line
        
        # Move up to the line with the tile size
        line = map_file.readline()
        while line.find("Tile size: ") < 0:
            line = map_file.readline()
            if line == "":
                raise Exception ("Expected tile size")
        
        # Get the number of teams
        line = line.lstrip("Tile size: ")
        line = line.strip()
        size = line.split('x')
        tile_w, tile_h = size
        
        # Convert to ints
        tile_w = int(tile_w)
        tile_h = int(tile_h)
        
        # Move up to the line with the map file
        line = map_file.readline()
        while line.find("Map: ") < 0:
            line = map_file.readline()
            if line == "":
                raise Exception ("Expected map filename")
        
        # Get the map filename
        line = line.lstrip("Map: ")
        line = line.strip()
        map_filename = line
        
        # Create the tile map
        self.map = tiles.TileMap(tile_filename,
                                  tile_w,
                                  tile_h)
        self.map.load_from_file(map_filename)
        self.add(self.map)
        
        # Center the map on-screen
        self.map.rect.center = self.view_rect.center
        
        # Move map to the right 150

        # Move up to the unit definitions
        while line.find("UNITS START") < 0:
            line = map_file.readline()
            if line == "":
                raise Exception ("Expected unit definitions")
        line = map_file.readline()
        
        # Create the units
        while line.find("UNITS END") < 0:
            line = line.rstrip()
            line = line.split(' ')
            unit_name = line[0]
            unit_team = int(line[1])
            unit_x, unit_y = int(line[2]), int(line[3])
            unit_angle = int(line[4])

                
            if not unit_name in unit.unit_types:
                raise Exception("No unit of name {} found!".format(unit_name))
            new_unit = unit.unit_types[unit_name](team = unit_team,
                                                  tile_x = unit_x,
                                                  tile_y = unit_y,
                                                  activate = True,
                                                  angle = unit_angle)
            
            # Add the unit to the update group and set its display rect
            self.update_unit_rect(new_unit)
            
            line = map_file.readline()
            if line == "":
                raise Exception ("Expected end of unit definitions")
        
    def begin_turn(self):
        """
        Iterates through every active unit and collects tile type
        of every unit at the start of each turn. The tile type is used
        for the purposes of giving a bonus to wookiees in the forest.

        Only looks over units of the active team.
        """
        for u in base_unit.BaseUnit.active_units:
            if u.day == 0: # The workaround to fix the 'base.damage not printing properly'
                u._update_image()
            if u.team == self.cur_team:
                unit_pos = (u.tile_x, u.tile_y)
                unit_tile = self.map.tile_data(unit_pos)[0]
                u.begin_round(unit_tile)

        # Change to next mode
        self.change_mode(Modes.Select)

    def which_button(self, button):
        """
        Figures out which button is being pressed.
        Used in building the correct unit at the 
        correct base.
        """
        if button[1] == "Artillery":
            self.current_button = "Artillery"
        elif button[1] == "Anti-Air":
            self.current_button = "Anti-Air"
        elif button[1] == "Tank":
            self.current_button = "Tank"
        elif button[1] == "Jeep":
            self.current_button = "Jeep"
        elif button[1] == "Anti-Armour":
            self.current_button = "Anti-Armour"
        elif button[1] == "Fighter":
            self.current_button = "Fighter"
        elif button[1] == "Bomber":
            self.current_button = "Bomber"
        elif button[1] == "Carrier":
            self.current_button = "Carrier"
        elif button[1] == "Battleship":
            self.current_button = "Battleship"
        elif button[1] == "Airstrip":
            self.current_button = "Airstrip"
        elif button[1] == "Shipyard":
            self.current_button = "Shipyard"
        elif button[1] == "Factory":
            self.current_button = "Factory"
                    

    def on_click(self, e):
        """
        This is called when a click event occurs.
        e is the click event.
        """

        # Don't react when in move, attack or game over mode.
        if (self.mode == Modes.Moving or
            self.mode == Modes.GameOver):
            return
        # make sure we have focus and that it was the left mouse button
        if (e.type == pygame.MOUSEBUTTONUP
            and e.button == 1
            and pygame.mouse.get_focused()):
            
            # If this is in the map, we're dealing with units or tiles
            if self.map.rect.collidepoint(e.pos):
                # Get the tile's position
                to_tile_pos = self.map.tile_coords(e.pos)

                # get the unit at the mouseclick
                unit = self.get_unit_at_screen_pos(e.pos)
                
                if unit:
                    # clicking the same unit again deselects it and, if
                    # necessary, resets select mode
                    if unit == self.sel_unit:
                        self.change_mode(Modes.Select)
                        self.sel_unit = None

                    # select a new unit and go into move mode on click
                    elif (self.mode == Modes.Select and
                          unit.team == self.cur_team):
                        self.sel_unit = unit
                        SoundManager.play(SELECT_SOUND)
                        self.buttons[0].onClick()                        
                        
                    # Attack
                    elif (self.mode == Modes.ChooseAttack and
                        self.sel_unit and
                        to_tile_pos in self._attackable_tiles):
                        # Attack the selected tile
                        self.sel_unit_attack(to_tile_pos)
                else:
                    # No unit there, so a tile was clicked

                    if (self.mode == Modes.ChooseMove and
                        self.sel_unit and
                        to_tile_pos in self._movable_tiles):
                        
                        # Move to the selected tile
                        self.sel_unit_move(to_tile_pos)

                    # Now choosing a spot to build the unit
                    elif (self.mode == Modes.ChooseSpot and
                          self.sel_unit and
                          to_tile_pos in self._buildable_tiles):
                        self.build_unit(to_tile_pos)

            # Otherwise, the user is interacting with the GUI panel
            # Make sure you aren't clicking outside button area
            # Handles the unit building buttons
            elif e.pos[0] < UNITS_BARW and e.pos[1] > 160 and e.pos[1] <= 600:
                count = 0
                for button in self.buttons:
                    if count > 2:
                    # If the button is a mode changing button
                    # and is enabled and has a click function, call the function
                        if ((not button.condition or button.condition()) and
                            self.get_unit_button_rect(button).collidepoint(e.pos)):
                            # Determine which button was pressed
                            self.which_button(button)
                            button.onClick()
                            # Play sound button
                            SoundManager.play(BUTTON_SOUND)
                    count += 1
            # Handles turn buttons
            else:
                # Check which button was pressed
                for button in self.buttons:
                    # If the button is a mode changing button
                    # and is enabled and has a click function, call the function
                    if (button[1] == "MOVE" or button[1] == "ATTACK" or button[1] == "END TURN"):
                        if ((not button.condition or button.condition()) and
                            self.get_button_rect(button).collidepoint(e.pos)):
                            button.onClick()
                            # Play the button sound
                            SoundManager.play(BUTTON_SOUND)

        # make sure we have focus and that it was the right mouse button
        elif (e.type == pygame.MOUSEBUTTONUP
            and e.button == 3
            and pygame.mouse.get_focused()):
            
            # If this is in the map, we're dealing with units or tiles
            if self.map.rect.collidepoint(e.pos):
                # Get the tile's position
                to_tile_pos = self.map.tile_coords(e.pos)

                # get the unit at the mouseclick
                unit = self.get_unit_at_screen_pos(e.pos)
                
                if unit:
                    # clicking the same unit again deselects it and, if
                    # necessary, resets select mode
                    if unit == self.sel_unit:
                        self.change_mode(Modes.Select)
                        self.sel_unit = None

                    # select a new unit and goes into attack mode on click of unit
                    elif (self.mode == Modes.Select and
                          unit.team == self.cur_team):
                        self.sel_unit = unit
                        SoundManager.play(SELECT_SOUND)
                        self.buttons[1].onClick()
                        
                    # Attack
                    elif (self.sel_unit and
                          to_tile_pos in self._attackable_tiles):
                        # Attack the selected tile
                        self.sel_unit_attack(to_tile_pos)
                else:
                    # No unit there, so a tile was clicked
                    if (self.mode == Modes.ChooseMove and
                        self.sel_unit and
                        to_tile_pos in self._movable_tiles):
                        
                        # Move to the selected tile
                        self.sel_unit_move(to_tile_pos)
            
        # Pressing enter/return ends the turn
        elif(e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN):
            self.buttons[2].onClick()

        # Pressing d allows you to delete a unit and gain resources back
        # Makes sure you can't delete factory or startflag
        # Changes mode back to select afterwards
        elif(e.type == pygame.KEYDOWN and e.key == pygame.K_d):
            if self.sel_unit != None:
                type = self.sel_unit.type
                if (self.sel_unit.type != "StartFlag" and
                    self.sel_unit.type != "Factory"):
                    self.sel_unit.deactivate()
                    self.renew_resources(self.sel_unit.type)
                    self.change_mode(Modes.Select)
                    self.sel_unit = None
            
    def sel_unit_attack(self, pos):
        """
        Attack the given position using the selected unit.
        """
        # Change the game state to show that there was an attack.
        self.change_mode(Modes.Select)
        
        # Mark that the unit has attacked.
        self.sel_unit.turn_state[1] = True
        
        # Face the attackee
        self.sel_unit.face_vector((
            pos[0] - self.sel_unit.tile_x,
            pos[1] - self.sel_unit.tile_y))
        
        # Get info about the attackee
        atk_unit = unit.base_unit.BaseUnit.get_unit_at_pos(pos)
        atk_tile = self.map.tile_data(pos)
        
        # Calculate the damage
        damage = self.sel_unit.get_damage(atk_unit, atk_tile)
        
        damage += random.choice([-1, -1, 0, 0, 0, 0, 0, 1, 1, 2])

        damage = max(damage, 0)

        # Deal damage
        atk_unit.hurt(damage)
        
        # Do the attack effect.
        if self.sel_unit.hit_effect:
            self._effects.add(self.sel_unit.hit_effect(
                self.map.screen_coords(pos)))
                
        # Play the unit's attack sound
        if self.sel_unit.hit_sound:
            SoundManager.play(self.sel_unit.hit_sound)
        
        if not atk_unit.active:
            # Add its death effect
            if atk_unit.die_effect:
               self._effects.add(atk_unit.die_effect(
                    self.map.screen_coords(pos)))
            
            # Play its death sound
            if atk_unit.die_sound:
                SoundManager.play(atk_unit.die_sound)

            # If the unit was destroyed, check if there are any others
            # left on a team other than the selected unit
            for u in unit.base_unit.BaseUnit.active_units:
                if u.team != self.sel_unit.team:
                    return
                
            # No other units, so game over!
            self.win_team = self.sel_unit.team
            self.mode = Modes.GameOver
    
    def sel_unit_move(self, pos):
        """
        Move the selected unit to the given position.
        """
        # Change the game state to show that there was a movement.
        self.change_mode(Modes.Moving)
        
        # Mark that the unit has moved
        self.sel_unit.turn_state[0] = True
        
        #the tile position the unit is at
        from_tile_pos = (self.sel_unit.tile_x,
                         self.sel_unit.tile_y)
        
        # Play the unit's movement sound
        SoundManager.play(self.sel_unit.move_sound)
        
        # These will be used in pathfinding
        cost = lambda c: (
            self.sel_unit.move_cost(self.map.tile_data(c)))
        passable = lambda c: (
            self.sel_unit.is_passable(self.map.tile_data(c), c))
        #set the path in the unit.
        self.sel_unit.set_path(
            tiles.find_path(
                self.map,
                from_tile_pos,
                pos,
                cost,
                passable))
                
    def get_unit_at_screen_pos(self, pos):
        """
        Gets the unit at a specified screen position ((x,y) tuple).
        Returns None if no unit.
        """
        # Get the unit's tile position.
        tile_pos = self.map.tile_coords(pos)
        return unit.base_unit.BaseUnit.get_unit_at_pos(tile_pos)
        
    def update_unit_rect(self, unit):
        """
        Scales a unit's display rectangle to screen coordiantes.
        """
        x, y = unit.tile_x, unit.tile_y
        screen_x, screen_y = self.map.screen_coords((x, y))
        unit.rect.x = screen_x
        unit.rect.y = screen_y
        
    def update(self):
        """
        Update everything in the group.
        """
        LayeredUpdates.update(self)
        
        # Update units
        base_unit.BaseUnit.active_units.update()
        
        if self.mode == Modes.Begin:
            # signal coordination and begin new turn
            self.newturn = 1
            self.begin_turn()
            
        # The unit is finished moving, so go back to select
        if self.mode == Modes.Moving:
            if (not self.sel_unit) or (not self.sel_unit.is_moving):
                self.change_mode(Modes.Select)
                
        # Update the reticle effect
        self._reticle.update()
        
        # Update effects
        self._effects.update()

    def draw(self):
        """
        Render the display.
        """
        # Fill in the background
        self.screen.fill(self.bg_color)
        
        # Update and draw the group contents
        LayeredUpdates.draw(self, self.screen)
        
        # draw units
        for u in base_unit.BaseUnit.active_units:
            self.update_unit_rect(u)
        base_unit.BaseUnit.active_units.draw(self.screen)
        
        # If there's a selected unit, outline it
        if self.sel_unit:
            pygame.gfxdraw.rectangle(
                self.screen,
                self.sel_unit.rect,
                SELECT_COLOR)
                
        # Mark potential targets
        for tile_pos in self._attackable_tiles:
            screen_pos = self.map.screen_coords(tile_pos)
            self.draw_reticle(screen_pos)
            
        # Draw effects
        self._effects.draw(self.screen)
        
        # Draw the status bar
        self.draw_bar()

        # Draw units bar
        self.draw_units_bar()
        
        # Draw the win message
        if self.mode == Modes.GameOver:
            # Determine the message
            win_text = "TEAM {} WINS!".format(
                TEAM_NAME[self.win_team].upper())
            
            # Render the text
            win_msg = BIG_FONT.render(
                win_text,
                True,
                FONT_COLOR)
                
            # Move it into position
            msg_rect = pygame.Rect((0, 0), win_msg.get_size())
            msg_rect.center = (MAP_WIDTH / 2, self.screen.get_height() / 2)
            
            # Draw it
            self.screen.blit(win_msg, msg_rect)

        # Update the screen
        pygame.display.flip()
        
    def draw_reticle(self, pos):
        """
        Draws a reticle with its top-left corner at pos.
        """
        self.screen.blit(self._reticle.image, pos)

    def draw_bar(self):
        """
        Draws the info bar on the right side of the screen. This 
        function is unavoidably quite large, as each panel needs to be
        handled with separate logic.
        """
        if not self.map: return
        
        line_num = 0
        
        #Determine where the mouse is
        mouse_pos = pygame.mouse.get_pos()
        coords = self.map.tile_coords(mouse_pos)
        
        #draw the background of the bar
        barRect = self.bar_rect
        pygame.draw.rect(self.screen, BAR_COLOR, barRect)
        
        #draw the outline of the bar
        outlineRect = self.bar_rect.copy()
        outlineRect.w -= 1
        outlineRect.h -= 1
        pygame.draw.rect(self.screen, OUTLINE_COLOR, outlineRect, 2)
        
        #Title for turn info
        self.draw_bar_title("DAY {}".format(self.cur_day), line_num)
        line_num += 1
        
        #Current turn
        self.draw_bar_title(
            "TEAM {}'S TURN".format(
                TEAM_NAME[self.cur_team].upper()),
            line_num)
        line_num += 1

        #divider
        self.draw_bar_div_line(line_num)
        line_num += 1
        
        #Get the tile data
        tile = self.map.tile_data(coords)

        if self.sel_unit:
            #title for tile section
            self.draw_bar_title("SELECTED UNIT", line_num)
            line_num += 1
            
            #type
            type = self.sel_unit.type
            self.draw_bar_text("Type: {}".format(type), line_num)
            line_num += 1

            #speed/range
            speed = self.sel_unit.speed
            u_range = self.sel_unit.get_atk_range()
            self.draw_bar_text(
                "Speed: {}  |  Range: {}".format(speed, u_range), line_num)
            line_num += 1

            #damage/defense
            damage = self.sel_unit.damage
            defense = self.sel_unit.defense
            self.draw_bar_text(
                "Attack: {}  |  Defense: {}".format(damage, defense), line_num)
            line_num += 1
            
            #fuel remaining
            if isinstance(self.sel_unit, unit.air_unit.AirUnit):
                fuel = self.sel_unit.fuel
                max_fuel = self.sel_unit.max_fuel
                self.draw_bar_text(
                    "Fuel: {}/{}".format(fuel, max_fuel), line_num)
                line_num += 1
            
            #whether this has moved
            has_moved = self.sel_unit.turn_state[0]
            self.draw_bar_text("Has Moved: {}".format(has_moved), line_num)
            line_num += 1

            #whether this has attacked
            has_atk = self.sel_unit.turn_state[1]
            self.draw_bar_text("Has Attacked: {}".format(has_atk), line_num)
            line_num += 1

            #divider
            self.draw_bar_div_line(line_num)
            line_num += 1

        if tile:
            #title for tile section
            self.draw_bar_title("HOVERED TILE", line_num)
            line_num += 1
            
            #Tile type
            type_name = tile.type.capitalize()
            self.draw_bar_text("Type: {}".format(type_name), line_num)
            line_num += 1
            
            #Tile coordinates
            self.draw_bar_text("Coordinates: {}".format(coords), line_num)
            line_num += 1
            
            #Tile defense
            defense = tile.defense_bonus
            if defense != 0:
                self.draw_bar_text("Defense: +{}".format(defense), line_num)
                line_num += 1
                
            #Tile range
            range_b = tile.range_bonus
            if range_b != 0:
                self.draw_bar_text("Range: +{}".format(range_b), line_num)
                line_num += 1

            #We can only know if there's a unit currently selected
            if self.sel_unit:
                #Is the tile passable?
                passable = self.sel_unit.is_passable(tile, coords)
                self.draw_bar_text("Passable: {}".format(passable), line_num)
                line_num += 1
                
                if passable:
                    #Movement cost
                    cost = self.sel_unit.move_cost(tile)
                    self.draw_bar_text("Movement Cost: {}".format(cost),
                                        line_num)
                    line_num += 1
            
            #divider
            self.draw_bar_div_line(line_num)
            line_num += 1
            
        #Get the hovered unit
        hov_unit = unit.base_unit.BaseUnit.get_unit_at_pos(coords)
        
        if hov_unit:
            #title for tile section
            self.draw_bar_title("HOVERED UNIT", line_num)
            line_num += 1
            
            #type
            type = hov_unit.type
            self.draw_bar_text("Type: {}".format(type), line_num)
            line_num += 1

            #speed/range
            speed = hov_unit.speed
            u_range = hov_unit.get_atk_range()
            self.draw_bar_text(
                "Speed: {}  |  Range: {}".format(speed, u_range), line_num)
            line_num += 1

            #damage/defense
            damage = hov_unit.damage
            defense = hov_unit.defense
            self.draw_bar_text(
                "Attack: {}  |  Defense: {}".format(damage, defense), line_num)
            line_num += 1
            
            #fuel remaining
            if isinstance(hov_unit, unit.air_unit.AirUnit):
                fuel = hov_unit.fuel
                max_fuel = hov_unit.max_fuel
                self.draw_bar_text(
                    "Fuel: {}/{}".format(fuel, max_fuel), line_num)
                line_num += 1
            
            #can only display this for units on current team
            if hov_unit.team == self.cur_team:
                #whether this has moved
                has_moved = hov_unit.turn_state[0]
                self.draw_bar_text("Has Moved: {}".format(has_moved),
                                    line_num)
                line_num += 1

                #whether this has attacked
                has_atk = hov_unit.turn_state[1]
                self.draw_bar_text("Has Attacked: {}".format(has_atk),
                                    line_num)
                line_num += 1

            if self.sel_unit and hov_unit.team != self.sel_unit.team:

                
                if self.sel_unit.can_hit(hov_unit):
                    #how much damage can we do?
                    pot_dmg = self.sel_unit.get_damage(hov_unit, tile)

                    FONT.set_bold(True)
                    self.draw_bar_text("Damage Range: {}-{}".format(
                            max(pot_dmg-1,0),pot_dmg+2), line_num)
                    line_num += 1
                    FONT.set_bold(False)

                    #analyze the probability of destroying hov_unit
                    #using up to 30 attackes
                    probs = analyze.destroy_prob(self.sel_unit, hov_unit,
                                                 tile, 30)

                    #find the first (noticeably) nonzero probability
                    min_nonzero = 0
                    while min_nonzero < 26 and probs[min_nonzero] < 0.00005:
                        min_nonzero += 1

                    #display up to 4 entries, quitting if the probability
                    #is essentially 1
                    self.draw_bar_div_line(line_num)
                    line_num += 1
                    for i in range(min_nonzero, min_nonzero+4):
                        self.draw_bar_text("{} turn(s): {:.2f}%".format(
                                i, probs[i]*100), line_num)
                        line_num += 1
                        if probs[i] >= 0.99995: break

                else:
                    FONT.set_bold(True)
                    self.draw_bar_text("Cannot Target", line_num)
                    line_num += 1
                    FONT.set_bold(False)

            #divider
            self.draw_bar_div_line(line_num)
            line_num += 1

        # Only draw change mode buttons
        for button in range(3):
            self.draw_bar_button(self.buttons[button])

    def draw_bar_text(self, text, line_num):
        """
        Draws text with a specified variable at a specifed line number.
        """
        line_text = FONT.render(text, True, FONT_COLOR)
        self.screen.blit(
            line_text,
            (self.bar_rect.x + PAD, FONT_SIZE * line_num + PAD))

    def draw_bar_title(self, text, line_num):
        """
        Draws a title at a specified line number with the specified text.
        """
        title_text = FONT.render(text, True, FONT_COLOR)
        self.screen.blit(
            title_text,
            (self.bar_rect.centerx - (title_text.get_width()/2),
            FONT_SIZE * line_num + PAD))

    def draw_bar_div_line(self, line_num):
        """
        Draws a dividing line at a specified line number.
        """
        y = FONT_SIZE * line_num + FONT_SIZE//2 + PAD
        pygame.draw.line(
            self.screen,
            (50, 50, 50),
            (self.bar_rect.x, y),
            (self.bar_rect.right, y))
            
    def get_button_rect(self, button):
        """
        Gets the rectangle bounding a button in screen cordinates.
        """
        # The y-coordinate is based on its slot number
        y = self.screen.get_height() - BUTTON_HEIGHT * (button.slot + 1)
        return pygame.Rect(self.bar_rect.x,
                            y,
                            self.bar_rect.width,
                            BUTTON_HEIGHT)

    def draw_bar_button(self, button):
        """
        Renders a button to the bar.
        If the mouse is hovering over the button it is rendered in white,
        else rgb(50, 50, 50).
        """

        but_rect = self.get_button_rect(button)
        
        # The outline needs a slightly smaller rectangle
        but_out_rect = but_rect
        but_out_rect.width -= 1

        # Determine the button color
        but_color = BAR_COLOR
        
        # The button can't be used
        if button.condition and not button.condition():
            but_color = BUTTON_DISABLED_COLOR
        else:
            # The button can be used
            mouse_pos = pygame.mouse.get_pos()
            if but_rect.collidepoint(mouse_pos):
                # Highlight on mouse over
                but_color = BUTTON_HIGHLIGHT_COLOR
        
        # Draw the button
        pygame.draw.rect(self.screen, but_color, but_rect)
            
        # Draw the outline
        pygame.draw.rect(self.screen, OUTLINE_COLOR, but_out_rect, 2)

        # Draw the text
        but_text = FONT.render(button.text, True, FONT_COLOR)
        self.screen.blit(
            but_text,
            (self.bar_rect.centerx - (but_text.get_width()/2),
            but_rect.y + (BUTTON_HEIGHT//2) - but_text.get_height()//2))


    def draw_units_bar(self):
        """
        Draws the units buttons bar on the left side of the screen.
        """
        if not self.map: return
        
        line_num = 0

        #Determine where the mouse is
        mouse_pos = pygame.mouse.get_pos()
        coords = self.map.tile_coords(mouse_pos)
        
        #draw the background of the bar
        barRect = self.units_bar_rect
        pygame.draw.rect(self.screen, BAR_COLOR, barRect)
        
        #draw the outline of the bar
        outlineRect = self.units_bar_rect.copy()
        outlineRect.w -= 1
        outlineRect.h -= 1
        pygame.draw.rect(self.screen, OUTLINE_COLOR, outlineRect, 2)

        # Draw the resources text for each team
        self.draw_units_bar_title("RESOURCES", line_num)
        line_num += 1

        if self.cur_team == 0:
            self.draw_units_bar_text("Gold: {}".format(self.gteam_gold), line_num)
            line_num += 1
            self.draw_units_bar_text("Wood: {}".format(self.gteam_wood), line_num)
            line_num += 1
            self.draw_units_bar_text("Food: {}".format(self.gteam_food), line_num)
            line_num += 1
        elif self.cur_team == 1:
            self.draw_units_bar_text("Gold: {}".format(self.rteam_gold), line_num)
            line_num += 1
            self.draw_units_bar_text("Wood: {}".format(self.rteam_wood), line_num)
            line_num += 1
            self.draw_units_bar_text("Food: {}".format(self.rteam_food), line_num)
            line_num += 1
        
        self.show_price(mouse_pos, line_num)
        
         # Only draw units buttons
        for button in range(3, len(self.buttons)):
            self.draw_units_button(self.buttons[button])

    def show_price(self, coords, line_num):
        """
        Draws price of unit when the mouse is hovering over it.
        Bounds the buttons in screen coordinates and then differentiates
        between each button.
        """
        button_start = MAP_WIDTH - (NUM_UNIT_BUTTONS * UNIT_BUTTON_HEIGHT)
        if coords[0] < UNITS_BARW:
            if coords[1] >= button_start:
                for button in self.buttons:
                    if ((button[1] != "MOVE" and button[1] != "ATTACK" and 
                         button[1] != "END TURN") and (NUM_UNIT_BUTTONS - 1) 
                        - (coords[1]-button_start)//UNIT_BUTTON_HEIGHT == button[0]):
                        self.draw_units_bar_div_line(line_num)
                        line_num += 1
                        self.draw_units_bar_title("COST", line_num)
                        line_num += 1
                        self.draw_units_bar_text("Gold: {}".format(button[4][0]), line_num)
                        line_num += 1
                        self.draw_units_bar_text("Wood: {}".format(button[4][1]), line_num)
                        line_num += 1
                        self.draw_units_bar_text("Food: {}".format(button[4][2]), line_num)
                        line_num += 1

    def draw_units_bar_text(self, text, line_num):
        """
        Draws text with a specified variable at a specifed line number.
        """
        line_text = FONT.render(text, True, FONT_COLOR)
        self.screen.blit(
            line_text,
            (self.units_bar_rect.x + PAD, FONT_SIZE * line_num + PAD))

    def draw_units_bar_title(self, text, line_num):
        """
        Draws a title at a specified line number with the specified text.
        """
        title_text = FONT.render(text, True, FONT_COLOR)
        self.screen.blit(
            title_text,
            (self.units_bar_rect.centerx - (title_text.get_width()/2),
            FONT_SIZE * line_num + PAD))

    def draw_units_bar_div_line(self, line_num):
        """
        Draws a dividing line at a specified line number.
        """
        y = FONT_SIZE * line_num + FONT_SIZE//2 + PAD
        pygame.draw.line(
            self.screen,
            (50, 50, 50),
            (self.units_bar_rect.x, y),
            (self.units_bar_rect.right, y))

    def draw_units_button(self, button):
        """
        Renders a button to the units bar.
        If the mouse is hovering over the button it is rendered in white,
        else rgb(50, 50, 50).
        """
        but_rect = self.get_unit_button_rect(button)

        # The outline needs a slightly smaller rectangle
        but_out_rect = but_rect
        but_out_rect.width -= 1

        # Determine the button color
        but_color = BAR_COLOR
        
        # The button can't be used
        if button.condition and not button.condition():
            but_color = BUTTON_DISABLED_COLOR
        else:
            # The button can be used
            mouse_pos = pygame.mouse.get_pos()
            if but_rect.collidepoint(mouse_pos):
                # Highlight on mouse over
                but_color = BUTTON_HIGHLIGHT_COLOR
        
        # Draw the button
        pygame.draw.rect(self.screen, but_color, but_rect)
            
        # Draw the outline
        pygame.draw.rect(self.screen, OUTLINE_COLOR, but_out_rect, 2)

        # Draw the text
        but_text = FONT.render(button.text, True, FONT_COLOR)
        self.screen.blit(
            but_text,
            (self.units_bar_rect.centerx - (but_text.get_width()/2),
            but_rect.y + (UNIT_BUTTON_HEIGHT//2) - (but_text.get_height()//2)))


    def get_unit_button_rect(self, button):
        """
        Gets the rectangle bounding a button in screen cordinates.
        """
        # The y-coordinate is based on its slot number
        y = self.screen.get_height() - UNIT_BUTTON_HEIGHT * (button.slot + 1)
        return pygame.Rect(self.units_bar_rect.x,
                            y,
                            self.units_bar_rect.width,
                            UNIT_BUTTON_HEIGHT)
    def signal(self):
        """
        Used for coordinating with arduino
        """
        self.newturn = 0

    def update_resources(self, serial_in):
        """
        Recieves resource info from arduino
        """
        raw_data = serial_in.readline()
        
        try:
            data = raw_data.decode('ascii')
        except (AttributeError, TypeError, UnicodeDecodeError):
            print("client: ascii decoding problem")
            data = raw_data

        data = data.split()

        if self.cur_team == 0:
            self.gteam_gold += int(data[0])
            self.gteam_wood += int(data[1])
            self.gteam_food += int(data[2])
        elif self.cur_team == 1:
            self.rteam_gold += int(data[0])
            self.rteam_wood += int(data[1])
            self.rteam_food += int(data[2])
