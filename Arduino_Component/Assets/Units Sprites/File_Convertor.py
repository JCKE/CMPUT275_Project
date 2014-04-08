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
    
def unpack_image(filename):
    current_file = open(filename + '.pbm', 'r')
    
    # This next bit handles first 4 pieces of header information always preceding the pixel info.
    # This information MUST be consistent with the contour file.
    current_file.readline()          # PPM Identifier, not that usefull to us
    width = current_file.readline()  # Width of image in pixels
    height = current_file.readline() # Height of image in pixels
    current_file.readline()          # Colour precision equal to the highest possible colour: 8-bit = 255, 16-bit = 65535 etc.
    
    width = int(width.rstrip('\n'))
    height = int(height.rstrip('\n'))
    info = dict()
    
    # Now we're getting into the actual image.
    for pixel in range(width*height):
        RGB = current_file.read(3)
        new_RGB = color565(ord(RGB[0]), ord(RGB[1]), ord(RGB[2]))

        info[(pixel%width, pixel//width)] = "0x%X"%new_RGB#hex(new_RGB) # Store a color for each pixel
        

    current_file.close()
    
    return info, width, height

def main():
    file_data = {} # dictionary where k, v = color, (x, y)coor
    
    print('\nEnter a .pbm image (without the .pbm):')
    image_file = sys.stdin.readline().rstrip('\n') 

    print('\nEnter .c file to write to (without the .c):')
    write_file = sys.stdin.readline().rstrip('\n') 

    print('\nEnter a .h file to write to, or skip.\n(must have //<><>UNITS<><> to write properly)')
    dot_h = sys.stdin.readline().rstrip('\n')
    print('Processing...')
            
    file_data, pixels_x, pixels_y = unpack_image(image_file)
    print_to_dot_c(image_file, write_file, file_data, pixels_x, pixels_y, dot_h)
    
def print_to_dot_c(image_name, write_file, file_info, pixel_x, pixel_y, dot_h):
    """
    Prints EVERYTHING into a .h file for reading of Arduino.
    """
    if(dot_h != ''):
        dot_h_file = open(dot_h + '.h', 'r') # open dot.h to read previous info
        info_buffer = dot_h_file.read().split('\n')
        dot_h_file.close()
        os.remove(dot_h + '.h')
    
        dot_h_file = open(dot_h + '.h', 'w') # make map.h to write to now
        while info_buffer:
            dot_h_file.write(info_buffer[0] + '\n')
            if info_buffer[0][:15] == '//<><>UNITS<><>':
                dot_h_file.write('extern prog_uint16_t {}[{}]; // {}x{}\n'.format(image_name, pixel_x*pixel_y, pixel_x, pixel_y))
            
            info_buffer.remove(info_buffer[0])
        
        dot_h_file.close()
    
    dot_c_file = open(write_file + '.c', 'a') # create and open a .c file for writing.
    
    dot_c_file.write('#include <avr/pgmspace.h>\n\nprog_uint16_t {}[{}] PROGMEM='.format(image_name, pixel_x*pixel_y) + '{\n')
        
    for pixel in range(pixel_x*pixel_y):
        
        dot_c_file.write("{}".format(file_info[(pixel%pixel_x, pixel//pixel_x)]))
        
        if file_info[(pixel%pixel_x, pixel//pixel_x)] == '0x0':
            dot_c_file.write("000") # add some extra zeros to make it looke nice
        
        if pixel != (pixel_x*pixel_y)-1:
            if pixel%16 == 15:
                dot_c_file.write(',\n')
            else:
                dot_c_file.write(', ')
        else:
            dot_c_file.write('};\n\n')

    dot_c_file.close()
    print("Success!")

if __name__ == '__main__':
    main()
