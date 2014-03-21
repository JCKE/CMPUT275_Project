import pygame, sys, math
import pygame.gfxdraw
import pqueue, helper
from pygame.sprite import Sprite
from collections import namedtuple

# A container class which stores information about a tile.
Tile = namedtuple('Tile', ['type',
                           'sprite_id',
                           'passable',
                           'defense_bonus',
                           'range_bonus'])

# a dictionary of tile IDs associated with their type data
tile_types = {
    0:  Tile('plains', 0, True, 0, 0),
    1:  Tile('wall', 1, False, 0, 0),
    2:  Tile('water', 2, False, 0, 0),
    3:  Tile('sand', 3, True, 0, 0),
    4:  Tile('road', 4, True, 0, 0),
    5:  Tile('mountain', 5, False, 1, 2),
    6:  Tile('forest', 6, True, 2, 0)
}

HIGHLIGHT_RATE = 0.0025
GRID_COLOR = (0, 0, 0, 80)

class TileMap(Sprite):
    """
    A class which renders a grid of tiles from a spritesheet.
    """
    
    def __init__(self, sheet_name, tile_width, tile_height):
        """
        sheet_name: the filename of the sprite sheet to use
        tile_width: the width of each tile, in pixels
        tile_height: the height of each tile, in pixels
        """
        
        # Set up map info
        self._sprite_sheet = pygame.image.load(sheet_name)
        self._tile_width = tile_width
        self._tile_height = tile_height
        self._map_width = None
        self._map_height = None
        self._tiles = []
        self._highlights = {}
        
        Sprite.__init__(self)
        
        # These are required for a pygame Sprite
        self.image = None
        self._base_image = None
        self.rect = pygame.Rect(0, 0, 0, 0)
        
    def _tile_count(self):
        """
        Returns the number of tiles on the map.
        
        >>> t = TileMap("assets/tiles.png", 20, 20)
        >>> t.load_from_file("maps/test-1.gif")
        >>> t._tile_count()
        25
        """
        return self._map_width * self._map_height
        
    def _tile_position(self, index):
        """
        Returns a tile's coordinates in tile units within the map given its
        index in the list.
        
        >>> t = TileMap("assets/tiles.png", 20, 20)
        >>> t.load_from_file("maps/test-1.gif")
        >>> t._tile_position(12)
        (2, 2)
        """
        return (index % self._map_width, index // self._map_width)
        
    def _tile_exists(self, coords):
        """
        Returns true if a tile exists, or false if it doesn't
        
        >>> t = TileMap("assets/tiles.png", 20, 20)
        >>> t.load_from_file("maps/test-1.gif")
        >>> t._tile_exists((2, 2))
        True
        >>> t._tile_exists((-2, -1))
        False
        >>> t._tile_exists((6, 7))
        False
        """
        return not (
            coords[0] < 0 or
            coords[0] >= self._map_width or
            coords[1] < 0 or
            coords[1] >= self._map_height)
        
    def _tile_index(self, coords):
        """
        Returns a tile's index in the list given its tile coordinates in tile
        units. Returns -1 if the provided coordinates are invalid.
        
        >>> t = TileMap("assets/tiles.png", 20, 20)
        >>> t.load_from_file("maps/test-1.gif")
        >>> t._tile_index((2, 2))
        12
        """
        if not self._tile_exists(coords): return -1

        #make sure to cast to int because input is sometimes floats
        #There won't be rounding errors though because the numbers
        #are just integers with .0 after
        return int(coords[1]) * self._map_width + int(coords[0])
        
    def _get_highlight_color(self, colorA, colorB):
        """
        Returns the movement color, which changes based on time.
        """
        # This produces a sine wave effect between a and b.
        sin = (math.sin(pygame.time.get_ticks() * HIGHLIGHT_RATE) + 1) * 0.5
        effect = lambda a, b: a + sin * (b - a)
        
        r = effect(colorA[0], colorB[0])
        g = effect(colorA[1], colorB[1])
        b = effect(colorA[2], colorB[2])
        a = effect(colorA[3], colorB[3])
        
        return (r, g, b, a)
        
    def _render_base_image(self, redraw = []):
        """
        Redraws all the tiles onto the base image.
        """
        # Create the empty surface
        self._base_image = pygame.Surface(
            (self._tile_width * self._map_width,
            self._tile_height * self._map_height)
        )
        
        # draw in each tile
        for i in range(self._tile_count()):
            tile_id = tile_types[self._tiles[i]].sprite_id
            
            # get its position from its index in the list
            x, y = self._tile_position(i)
            x *= self._tile_width
            y *= self._tile_height
            
            # determine which subsection to draw based on the sprite id
            area = pygame.Rect(
                tile_id * self._tile_width,
                0,
                self._tile_width,
                self._tile_height
            )
            
            # draw the tile
            self._base_image.blit(self._sprite_sheet, (x, y), area)
            
    def _set_tiles(self, tiles):
        """
        Sets the list of tiles.
        """
        self._tiles = tiles[:]
        
        # The image now needs to be redrawn
        self._render_base_image()
            
    def get_tiles(self):
        """
        Returns a copy of the list of tiles.
        
        >>> t = TileMap("assets/tiles.png", 20, 20)
        >>> t.load_from_file("maps/test-1.gif")
        >>> t.get_tiles() == [0, 1, 2, 3, 4, 5, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        ...                   0, 0, 0, 0, 0, 0, 0, 0]
        True
        """
        return self._tiles[:]
            
    def load_from_file(self, filename):
        """
        Loads tile data from the given image file.
        The image file should be have an 8-bit indexed palette. Each colour
        index corresponds to the tile (e.g. colour index 2 = tile type 2)
        
        >>> t = TileMap("assets/tiles.png", 20, 20)
        >>> t.load_from_file("maps/test-1.gif")
        >>> t.rect
        <rect(0, 0, 100, 100)>
        >>> t.get_tiles() == [0, 1, 2, 3, 4, 5, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        ...                   0, 0, 0, 0, 0, 0, 0, 0]
        True
        """
        tiles = []
        
        # Load in the map image.
        map_image = pygame.image.load(filename)
        self._map_width, self._map_height = map_image.get_size()
        self.rect.w = self._map_width * self._tile_width
        self.rect.h = self._map_height * self._tile_height
        
        # Go through the image adding tiles
        map_tiles = []
        for y in range(map_image.get_height()):
            for x in range(map_image.get_width()):
                # The tile number corresponds to the pixel colour index
                tiles.append(map_image.get_at_mapped((x, y)))
        
        # Set the tiles
        self._set_tiles(tiles)
        
    def get_tile_size(self):
        """
        Returns a tuple containing a tile's width and height within this map.
        
        >>> t = TileMap("assets/tiles.png", 20, 20)
        >>> t.load_from_file("maps/test-1.gif")
        >>> t.get_tile_size()
        (20, 20)
        """
        return (self._tile_width, self._tile_height)
        
    def tile_coords(self, screen_coords):
        """
        Returns the tile coordinates within this TileMap that the given screen
        coordinates fall into.
        
        >>> t = TileMap("assets/tiles.png", 20, 20)
        >>> t.load_from_file("maps/test-1.gif")
        >>> t.tile_coords((45, 22))
        (2, 1)
        """
        x, y = screen_coords
        return (
            math.floor((x - self.rect.left) / self._tile_width),
            math.floor((y - self.rect.top) / self._tile_height)
        )
        
    def screen_coords(self, tile_coords):
        """
        Returns the screen coordinates of a given tile.
        
        >>> t = TileMap("assets/tiles.png", 20, 20)
        >>> t.load_from_file("maps/test-1.gif")
        >>> t.screen_coords((3, 4))
        (60, 80)
        """
        x, y = tile_coords
        return (
            x * self._tile_width + self.rect.x,
            y * self._tile_height + self.rect.y
        )
        
    def tile_data(self, coords):
        """
        Returns the tile data for a given tile.
        
        >>> t = TileMap("assets/tiles.png", 20, 20)
        >>> t.load_from_file("maps/test-1.gif")
        >>> t.tile_data((0, 0)) == tile_types[0]
        True
        >>> t.tile_data((1, 1)) == tile_types[6]
        True
        
        """
        if not self._tile_exists(coords): return False
        
        index = self._tile_index(coords)
        
        return tile_types[self._tiles[index]]
        
    def neighbours(self, coords):
        """
        Returns all neighbour coordinates to a given tile. Does not return
        coordinates which do not exist.
        
        >>> t = TileMap("assets/tiles.png", 20, 20)
        >>> t.load_from_file("maps/test-1.gif")
        >>> t.neighbours((0, 0))
        [(1, 0), (0, 1)]
        >>> t.neighbours((4, 4))
        [(4, 3), (3, 4)]
        >>> t.neighbours((1, 1))
        [(1, 0), (2, 1), (0, 1), (1, 2)]
        """
        x, y = coords
        
        # The possible neighbouring tiles.
        neighbours = [
            (x, y - 1),
            (x + 1, y),
            (x - 1, y),
            (x, y + 1)
        ]
        
        # Return only those which exist.
        return [n for n in neighbours if self._tile_exists(n)]
        
    def set_highlight(self, name, colorA, colorB, tiles):
        """
        Sets the given list of tile coordinates to be highlighted in the given
        color and wave between the first and second colors.
        It will be stored under the given name.
        """
        self._highlights[name] = (tiles, colorA, colorB)
        
    def remove_highlight(self, name):
        """
        Removes highlights of the given colour. If the highlights do not
        exist, does nothing.
        """
        if name in self._highlights:
            del self._highlights[name]
            
    def clear_highlights(self):
        """
        Removes all highlights.
        """
        self._highlights.clear()
        
    def update(self):
        """
        Overrides the default update function for sprites. This updates
        the image.
        """
        # copy over the base image
        self.image = self._base_image.copy()
        
        # draw the highlights
        for name, (tiles, colorA, colorB) in self._highlights.items():
            for coord in tiles:
                tile_rect = pygame.Rect(
                    coord[0] * self._tile_width,
                    coord[1] * self._tile_height,
                    self._tile_width,
                    self._tile_height
                )
                pygame.gfxdraw.box(self.image,
                                   tile_rect,
                                   self._get_highlight_color(colorA, colorB))
            
        # draw the grid
        for x in range(0,
                        self._map_width * self._tile_width,
                        self._tile_width):
            pygame.gfxdraw.vline(
                self.image,
                x,
                0,
                self._map_height * self._tile_height,
                GRID_COLOR
            )
        for y in range(0,
                        self._map_height * self._tile_height,
                        self._tile_height):
            pygame.gfxdraw.hline(
                self.image,
                0,
                self._map_width * self._tile_width,
                y,
                GRID_COLOR
            )
    
def better_tile(a, b, start, end):
    """
    Picks the best tile to use. This is used in case of a tie in the
    priority queue. Returns True if choosing tile a, or False for tile b.
    The tile with the closest slope to the slope between start and end
    will be given priority. If there's still a tie, the tile with the
    lowest Y is chosen. Finally, if that fails, the tile with the lowest
    X is chosen.
    
    Examples:
    The best tile here is (1, 1), as it lies directly on the line:
    >>> better_tile((1, 1), (1, 2), (0, 0), (3, 3))
    True
    
    The best tile here is (1, 4), as it lies closer to the line:
    >>> better_tile((1, 1), (1, 4), (0, 3), (3, 3))
    False
    
    Both tiles are equidistant to the line, so we choose the lowest Y,
    (1, 0):
    >>> better_tile((0, 1), (1, 0), (0, 0), (3, 3))
    False
    
    Both tiles are equidistant to the line and have equal Y, so we
    choose the lowest X, (3, 1):
    >>> better_tile((3, 1), (5, 1), (4, 0), (4, 4))
    True
    """
    dist_a = round(helper.squared_segment_dist(a, start, end), 3)
    dist_b = round(helper.squared_segment_dist(b, start, end), 3)
    
    # Choose the lowest difference from the line
    if dist_a < dist_b:
        return True
    elif dist_a > dist_b:
        return False
    else:
        # Still a tie - choose lowest Y
        if a[1] < b[1]:
            return True
        elif a[1] > b[1]:
            return False
        else:
            # Still a tie - choose lowest X
            if a[0] < b[0]:
                return True
            else:
                return False
            
def find_path(graph,
                start,
                end,
                cost = lambda pos: 1,
                passable = lambda pos: True,
                heuristic = helper.manhattan_dist):
    """
    Returns the path between two nodes as a list of nodes using the A*
    algorithm.
    If no path could be found, an empty list is returned.
    
    The cost function is how much it costs to leave the given node. This should
    always be greater than or equal to 1, or shortest path is not guaranteed.
    
    The passable function returns whether the given node is passable.
    
    The heuristic function takes two nodes and computes the distance between the
    two. Underestimates are guaranteed to provide an optimal path, but it may
    take longer to compute the path. Overestimates lead to faster path
    computations, but may not give an optimal path.
    
    Code based on algorithm described in:
    http://www.policyalmanac.org/games/aStarTutorial.htm
    
    Example use:
    >>> t = TileMap("assets/tiles.png", 20, 20)
    >>> t.load_from_file("maps/test-2.gif")
    
    >>> find_path(t, (0, 0), (4, 4))
    [(0, 0), (1, 0), (1, 1), (2, 1), (2, 2), (3, 2), (3, 3), (4, 3), (4, 4)]
    >>> find_path(t, (0, 0), (5, 5))
    []
    
    >>> t = TileMap("assets/tiles.png", 20, 20)
    >>> t.load_from_file("maps/test-3.gif")
    >>> cost = lambda c: 1
    >>> passable = lambda c: t.tile_data(c).passable
   
    >>> find_path(t, (2, 0), (4, 1), cost, passable) == [(2, 0), (1, 0), (0, 0),
    ... (0, 1), (0, 2), (1, 2), (2, 2), (3, 2), (3, 3), (3, 4), (4, 4), (5, 4),
    ... (5, 3), (5, 2), (5, 1), (4, 1)]
    True
    """
    # tiles to check (tuples of (x, y), cost)
    todo = pqueue.PQueue()
    todo.update(start, 0)
    
    # tiles we've been to
    visited = set()
    
    # associated G and H costs for each tile (tuples of G, H)
    costs = { start: (0, heuristic(start, end)) }
    
    # parents for each tile
    parents = {}
    
    while todo and (end not in visited):
        todo.tie_breaker = lambda a,b: better_tile(a, b, start, end)
    
        cur, c = todo.pop_smallest()
        visited.add(cur)
        
        # check neighbours
        for n in graph.neighbours(cur):
            # skip it if we've already checked it, or if it isn't passable
            if ((n in visited) or
                (not passable(n))):
                continue
                
            if not (n in todo):
                # we haven't looked at this tile yet, so calculate its costs
                g = costs[cur][0] + cost(cur)
                h = heuristic(n, end)
                costs[n] = (g, h)
                parents[n] = cur
                todo.update(n, g + h)
            else:
                # if we've found a better path, update it
                g, h = costs[n]
                new_g = costs[cur][0] + cost(cur)
                if new_g < g:
                    g = new_g
                    todo.update(n, g + h)
                    costs[n] = (g, h)
                    parents[n] = cur
    
    # we didn't find a path
    if end not in visited:
        return []
    
    # build the path backward
    path = []
    while end != start:
        path.append(end)
        end = parents[end]
    path.append(start)
    path.reverse()
    
    return path
    
def reachable_tiles(graph,
                      start,
                      max_cost,
                      cost = lambda pos: 1,
                      passable = lambda pos: True):
    """
    Returns a set of nodes which can be reached with a total cost of max_cost.
    The cost function is how much it costs to leave the given node. This should
    always be greater than or equal to 1, or shortest path is not guaranteed.
    The passable function returns whether the given node.
    
    Example use:
    >>> t = TileMap("assets/tiles.png", 20, 20)
    >>> t.load_from_file("maps/test-2.gif")
    
    >>> reachable_tiles(t, (2, 2), 2) == set([(2, 0), (1, 1), (2, 1), (3, 1),
    ... (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (1, 3), (2, 3), (3, 3), 
    ... (2, 4)])
    True
    
    >>> t = TileMap("assets/tiles.png", 20, 20)
    >>> t.load_from_file("maps/test-3.gif")
    >>> cost = lambda c: 1
    >>> passable = lambda c: t.tile_data(c).passable
   
    >>> reachable_tiles(t, (2, 0), 6, cost, passable) == set([(3, 0), (2, 0),
    ... (1, 0), (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (2, 2)])
    True
    """
    # tiles to check (tuples of x, y)
    todo = pqueue.PQueue()
    todo.update(start, 0)
    
    # tiles we've been to
    visited = set()
    
    # tiles which we can get to within max_cost
    reachable = set()
    reachable.add(start)
    
    while todo:
        cur, c = todo.pop_smallest()
        visited.add(cur)
        
        # it's too expensive to get here, so don't bother checking
        if c > max_cost:
            continue
        
        # check neighbours
        for n in graph.neighbours(cur):
            # skip it if it doesn't exist, if we've already checked it, or
            # if it isn't passable
            if ((n in visited) or
                (not passable(n))):
                continue
            
            # try updating the tile's cost
            new_cost = c + cost(cur)
            if todo.update(n, new_cost) and new_cost <= max_cost:
                reachable.add(n)
    
    return reachable
