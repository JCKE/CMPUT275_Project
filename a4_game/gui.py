import sys, pygame
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
CENTER = 100

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
    Select, ChooseMove, Moving, ChooseAttack, GameOver = range(5)

# A container class which stores button information.
# Each "slot" is a BUTTON_HEIGHT pixel space counting up from the bottom
# of the screen.
Button = namedtuple('Button', ['slot', 'text', 'onClick', 'condition'])

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
        self.change_mode(Modes.Select)
        
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
        
        # The rect containing the map view
        self.view_rect = pygame.Rect(0,
                                      0,
                                      MAP_WIDTH,
                                      screen_rect.h)
        self.bg_color = bg_color
        self.map = None

        # Set up team information
        self.num_teams = None
        self.current_turn = 0
        self.win_team = None 

        # The currently selected unit
        self.sel_unit = None
        
        # Set up GUI
        self.buttons = [
            Button(0, "MOVE", self.move_pressed, self.can_move),
            Button(1, "ATTACK", self.attack_pressed, self.can_attack),
            Button(2, "END TURN", self.end_turn_pressed, None)]
        
        # We start in select mode
        self.mode = Modes.Select
        
        # Tiles we can move to/attack
        self._movable_tiles = set()
        self._attackable_tiles = set()

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

                    # select a new unit
                    elif (self.mode == Modes.Select and
                          unit.team == self.cur_team):
                        self.sel_unit = unit
                        SoundManager.play(SELECT_SOUND)
                        
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
            
            # Otherwise, the user is interacting with the GUI panel
            else:
                # Check which button was pressed
                for button in self.buttons:
                    # If the button is enabled and has a click function, call
                    # the function
                    if ((not button.condition or button.condition()) and
                        self.get_button_rect(button).collidepoint(e.pos)):
                        button.onClick()
                        
                        # Play the button sound
                        SoundManager.play(BUTTON_SOUND)
                        
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

#                self.draw_bar_text("Potential Damage: {}".format(pot_dmg),
#                                    line_num)
                                    

            #divider
            self.draw_bar_div_line(line_num)
            line_num += 1

        for button in self.buttons:
            self.draw_bar_button(button)

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
