"""
.pbm Map Convertor
Jesse Emery
31/03/2014

This program, when run in the terminal, will take a .pbm map and store its pixel (x, y) coordinates
and tile information in a .h file (named after the .pbm) to be accessed by the main program.
If one already exists of the same name, it will rewrite over it instead of appending.
It also asks if you want to edit 'project.h', where it will automatically include things for you,
but there's much more on that below.

Everything is explained below, but it should be noted that this program MUST be run using python
and not python3. Trying to run in python3 kept giving errors that I was unsuccessful in fixing.

The magenta doesn't actually end up determining where the bases go; that must be hard-coded in.
It just acts as a guideline for what your map will look like, as well as telling the game not
to spawn resources or draw anything there. I threw in a few test files to mess around with too.
"""

import os
import sys

def color565(redNumber, greenNumber, blueNumber):
    # Basic color convertor; takes in a red, green, and blue value between 0-255
    # and bit-shifts them appropriately to output a 16-bit version of that color.
    redNumber = redNumber//8
    greenNumber = greenNumber//4
    blueNumber = blueNumber//8

    redNumber = redNumber << 11
    greenNumber = greenNumber << 5
    
    return (redNumber+greenNumber+blueNumber)


# These are the colors associated with each type of tile, so when reading the .pbm image
# the program knows which tiles correspond to each color. 

Tiles = {color565(255, 252, 114): "Beach", # Make sure the names have different first letters
         color565(0, 94, 29): "Forest",
         color565(0, 255, 0): "Grass",
         color565(215, 215, 215): "Mountain",
         color565(95, 95, 95): "Road",
         color565(0, 0, 0): "Wall",
         color565(0, 0, 255): "H2O",
         color565(255, 0, 255): "NO DRAW"} 

# This is used for resource distribution, which is a separate map.
Contour_map = {color565(215, 215, 215): 1,
               color565(95, 95, 95): 2,
               color565(0, 0, 0): 3,
               color565(255, 0, 255): 0} 
    
def unpack_image(filename):
    """
    unpack_image() takes in a file name, looks for a .pbm image of that file, and
    then opens it and parses the information. In order to work with the screens
    properly, the image must be the appropriate size since each pixel represents one tile.

    It stores a tuple of the color and the denisty of the resource on each pixel in a
    dictionary to be returned once all the information has been read. The map width
    and height are also returned to be used later.
    """
    current_file = open(filename + '.pbm', 'r')

    # This looks for a contour density map associated with the map name, otherwise just take from the master contour map
    if os.path.isfile('{}_cont.pbm'.format(filename)):
        contour_file = open('{}_cont.pbm'.format(filename), 'r')
    else:
        contour_file = open('master_contour.pbm', 'r')
    
    # This next bit handles first 4 pieces of header information always preceding the pixel info.
    # This information MUST be consistent with the contour file, as I'm assuming they're the same size.
    current_file.readline()          # PPM Identifier, not that usefull for the purpose of this program
    width = current_file.readline()  # Width of image in pixels
    height = current_file.readline() # Height of image in pixels
    current_file.readline()          # Colour precision equal to the highest possible colour: 8-bit = 255, 16-bit = 65535 etc.
    # Basically, the number of hexadecimal bytes to read in per color at a time
    # (not really useful again; I'm assuming you're storing the map in basic 8-bit color)

    # This information was just stored and should be the same as the previous readings, so we ignore it
    for l in range(4):
        contour_file.readline()
    
    width = int(width.rstrip('\n'))
    height = int(height.rstrip('\n'))
    info = dict()
    
    # Now we're getting into the actual image.
    for pixel in range(width*height):
        RGB = current_file.read(3)
        new_RGB = color565(ord(RGB[0]), ord(RGB[1]), ord(RGB[2])) # ord() makes hex into int
        
        RGB_cont = contour_file.read(3)
        new_RGB_cont = color565(ord(RGB_cont[0]), ord(RGB_cont[1]), ord(RGB_cont[2]))

        info[(pixel%width, pixel//width)] = (new_RGB, new_RGB_cont)
        

    current_file.close()
    contour_file.close()
    
    return info, width, height

def main():
    file_data = dict() 
    
    print('\nEnter a .pbm map (without the .pbm):')
    map_name = sys.stdin.readline().rstrip('\n')
            
    print('\nPrint to project.h in previous directory? (Y/N)')
    project = sys.stdin.readline().rstrip('\n')
    print('Processing...')
    
    file_data, pixels_x, pixels_y = unpack_image(map_name)
    print_to_dot_h(map_name, file_data, pixels_x, pixels_y, project)
    
def print_to_dot_h(map_name, file_info, pixel_x, pixel_y, project_YN):
    """
    This function first asks if you want to edit 'project.h', which would auto-#include the map you're converting
    and changing that map to be the one that loads on startup. I couldn't figure out how to just edit
    certain lines, so it stores whatever is in 'project.h' and erases 'project.h'. Then it makes a new one,
    throws all the stored info in, and a few extra lines within that once it finds the appropriate lines.

    It prints all the info from file_info as a data type 'tile', which is a struct. It only prints the first
    four pieces of the struct's information because everything else should just be the same on startup (doing it this
    way makes it less cluttered when reading). This info is it's x and y positions, tile type, and resource density.

    Now, if you take a look in tile.h at the 'tile' struct, you'll notice the fourth position is reserved for the resource
    amount. I'm piggybacking off of that since I don't need to know where a tile lies in the contour map once all
    the resources have been assigned. This way precious memory space is saved since it would've taken over 700 more bytes
    if another variable was introduced to the struct, and that would unnecessarily impede upon the already measly 8kB.
    
    
    Now, this function does assume you aren't messing around with certain things: it assumes you're in the 'Maps'
    directory, assumes 'project.h' is in the previous directory and assumes project.h has the line '#include "tile.h"'.
    But, for the purpose of this program you shouldn't really be moving these folders around anyways.
    This was more for just easability of throwing in a new map into the maps folder, running this program,
    and not having to edit anything else anywhere else; just upload and test. Presumably, you'll most-likely be
    testing these maps out as you create them so this isn't exactly a bad thing. Ultimately, you would only ever
    have to edit 'project.h' once you start deleting maps so it doesn't '#include' files that don't exist.
    """
    if(project_YN.upper() == 'Y'):
        os.chdir("..") # Changes to previous directory (where project.h MUST be)
        project_dot_h = open('project.h', 'r')
        info_buffer = project_dot_h.read().split('\n')
        project_dot_h.close()
        os.remove('project.h')
    
        project_dot_h = open('project.h', 'w')
        while info_buffer:
            if info_buffer[0][:17] == 'tile *current_map':
                project_dot_h.write('tile *current_map = {};\n'.format(map_name))
            elif info_buffer[0] != '#include "Maps/{}.h"'.format(map_name):
                project_dot_h.write(info_buffer[0])
                
            if len(info_buffer) > 1: # if you don't add this, the .h file will get pointless new-lines added every time
                project_dot_h.write('\n');
                
            if info_buffer[0] == '#include "tile.h"':
                project_dot_h.write('#include "Maps/{}.h"\n'.format(map_name))
                
            info_buffer.remove(info_buffer[0])
        
        project_dot_h.close()
        os.chdir("Maps")
    
    map_dot_h = open(map_name + '.h', 'w') # create and open a .h file for writing map info to
    msg = ("#ifndef __{}_H__\n".format(map_name.upper()) +
            "#define __{}_H__\n\n".format(map_name.upper()) +
            "#include \"tile.h\"\n\n")
        
    map_dot_h.write(msg)
    map_dot_h.write('tile ' + map_name + '[] = {')
        
    for pixel in range(pixel_x*pixel_y):
        tile_type = Tiles[file_info[(pixel%pixel_x, pixel//pixel_x)][0]] # find out what tile type we're dealing with
        contour_density = Contour_map[file_info[(pixel%pixel_x, pixel//pixel_x)][1]]
        map_dot_h.write('{ ' + "{}, {}, '{}', {}".format(pixel%pixel_x, pixel//pixel_x, tile_type[0], contour_density) + ' }') # format only the first character of tile_type
        
        if pixel != pixel_x*pixel_y-1:
            if pixel%4 == 3: # again, just something to make it easier to read
                map_dot_h.write(',\n')
            else:
                map_dot_h.write(', ')
        else:
            map_dot_h.write('};\n') # at the final pixel, close off the array
    
        if pixel%pixel_x == pixel_x-1: # add newlines to bunch it into rows of pixels
            map_dot_h.write('\n')

            
    map_dot_h.write('#endif') # end the file by closing off the initial 'ifndef'
    map_dot_h.close()
    print("Success!")

if __name__ == '__main__':
    main()
