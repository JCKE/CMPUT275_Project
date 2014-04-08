"""
This program will take a .pbm image, and store its pixel (x, y) coordinates and colour in a .txt file for other purposes.

The format of the .txt file will be:
x, y, colour
0, 0, -equivalent of black-
1, 0, -equivalent of white-
and soforth...

Jesse Emery
31/03/2014
"""

import os
import sys
    
def color565(redNumber, greenNumber, blueNumber):
    redNumber = redNumber//8
    greenNumber = greenNumber//4
    blueNumber = blueNumber//8

    redNumber = redNumber << 11
    greenNumber = greenNumber << 5
    
    return (redNumber+greenNumber+blueNumber)
    
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
    current_file = open(filename + '.pbm', 'r')
    
    if os.path.isfile('{}_cont.pbm'.format(filename)):
        contour_file = open('{}_cont.pbm'.format(filename), 'r')
    else:
        contour_file = open('master_contour.pbm', 'r')
    
    # This next bit handles first 4 pieces of header information always preceding the pixel info.
    # This information MUST be consistent with the contour file.
    current_file.readline()          # PPM Identifier, not that usefull to us
    width = current_file.readline()  # Width of image in pixels
    height = current_file.readline() # Height of image in pixels
    current_file.readline()          # Colour precision equal to the highest possible colour: 8-bit = 255, 16-bit = 65535 etc.

    for l in range(4):
        contour_file.readline() # Get past the pointless info
    
    width = int(width.rstrip('\n'))
    height = int(height.rstrip('\n'))
    info = dict()
    
    # Now we're getting into the actual image.
    for pixel in range(width*height):
        RGB = current_file.read(3)
        new_RGB = color565(ord(RGB[0]), ord(RGB[1]), ord(RGB[2]))
        
        RGB_cont = contour_file.read(3)
        new_RGB_cont = color565(ord(RGB_cont[0]), ord(RGB_cont[1]), ord(RGB_cont[2]))

        info[(pixel%width, pixel//width)] = (new_RGB, new_RGB_cont) # Store a color for each pixel
        

    current_file.close()
    contour_file.close()
    
    return info, width, height

def main():
    file_data = {} # dictionary where k, v = color, (x, y)coor
    
    print('\nEnter a .pbm map (without the .pbm):')
    map_name = sys.stdin.readline().rstrip('\n')
    print('Processing...')
            
    file_data, pixels_x, pixels_y = unpack_image(map_name)
    print_to_dot_h(map_name, file_data, pixels_x, pixels_y)
    
def print_to_dot_h(map_name, file_info, pixel_x, pixel_y):
    """
    Prints EVERYTHING into a .h file for reading of Arduino.
    """
    os.chdir("..") # Changes to previous directory (where map.h SHOULD be)
    master_map_file = open('project.h', 'r') # open map.h to read previous info
    info_buffer = master_map_file.read().split('\n')
    master_map_file.close()
    os.remove('project.h')
    
    master_map_file = open('project.h', 'w') # make map.h to write to now
    while info_buffer:
        if info_buffer[0][:17] == 'tile *current_map':
            master_map_file.write('tile *current_map = {};\n'.format(map_name))
        elif info_buffer[0] != '#include "Maps/{}.h"'.format(map_name):
            master_map_file.write(info_buffer[0] + '\n')
        if info_buffer[0] == '#include "tile.h"':
            master_map_file.write('#include "Maps/{}.h"\n'.format(map_name))
        info_buffer.remove(info_buffer[0])
        
    master_map_file.close()
    os.chdir("Maps")
    
    dot_h_file = open(map_name + '.h', 'w') # create and open a .h file for writing.
    msg = ("#ifndef __{}_H__\n".format(map_name.upper()) +
            "#define __{}_H__\n\n".format(map_name.upper()) +
            "#include \"tile.h\"\n\n")
        
    dot_h_file.write(msg)
    dot_h_file.write('tile ' + map_name + '[] = {')
    
    for pixel in range(pixel_x*pixel_y):
        tile_type = Tiles[file_info[(pixel%pixel_x, pixel//pixel_x)][0]]
        contour_density = Contour_map[file_info[(pixel%pixel_x, pixel//pixel_x)][1]]
        dot_h_file.write('{ ' + "{}, {}, '{}', {}".format(pixel%pixel_x, pixel//pixel_x, tile_type[0], contour_density) + ' }') #format first character of tile/contour type
        
        if pixel != pixel_x*pixel_y-1:
            if pixel%4 == 3:
                dot_h_file.write(',\n')
            else:
                dot_h_file.write(', ')
        else:
            dot_h_file.write('};\n')
    
        if pixel%pixel_x == pixel_x-1:
            dot_h_file.write('\n')

            
    dot_h_file.write('#endif')
    dot_h_file.close()
    print("Success!")

if __name__ == '__main__':
    main()
