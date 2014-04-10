import sys, pygame, tiles, serial, argparse
from gui import GUI

global debug
debug = False

RESOLUTION = pygame.Rect(0, 0, 915, 600)
BG_COLOR = (32, 32, 32)

# To run:
# $ python3 main.py -s /dev/ttyACM0
# or $ python3 main.py -m <desired map> -s <serial-port>
# Working from stdin/stdout not recommended

def main():
    """
    Main function. Acts as a front end, calls
    initializations and takes input and directs it
    to where it needs to be, same with output.
    Used parser from assignment.
    """

    args = parse_args()

    # Initialize
    pygame.mixer.pre_init(22050, -16, 2, 512) # Small buffer for less sound lag
    pygame.init()
    pygame.display.set_caption("Tactics 2")
    main_gui = GUI(RESOLUTION, BG_COLOR)
    clock = pygame.time.Clock()

    if args.serialport:
        print("Opening serial port: %s" % args.serialport)
        serial_out = serial_in =  serial.Serial(args.serialport, 9600)
    else:
        print("No serial port.  Using stdin/stdout.")
        serial_out = sys.stdout
        serial_in = sys.stdin

    # If a filename was given, load that level. Otherwise, load a default.
    if args.map:
        level = args.map
        main_gui.load_level("maps/" + level + ".lvl")
    # In case of debuging
    if args.verbose:
        debug = True
        print("Debugging turned on")
    else:
        debug = False

    # The main game loop
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                sys.exit()
            # End if q is pressed
            elif (event.type == pygame.KEYDOWN and
                  (event.key == pygame.K_q or event.key == pygame.K_ESCAPE)):
                pygame.display.quit()
                sys.exit()
            # Respond to clicks
            elif event.type == pygame.MOUSEBUTTONUP:
                main_gui.on_click(event)
            # Allows player to use enter/return to end turn
            elif (event.type == pygame.KEYDOWN and 
                  (event.key == pygame.K_RETURN or event.key == pygame.K_d)):
                main_gui.on_click(event)
        main_gui.update()
        # Coordinate with arduino
        if main_gui.newturn == 1:
            # Send that a turn is ending
            try:
                serial_out.write(1)
            except TypeError:
                reencoded = bytes(1, encoding='ascii')
                serial_out.write(reencoded)
            # Recieve incoming resources and signal that turn is ended
            main_gui.update_resources(serial_in)
            main_gui.signal()
        main_gui.draw()
        clock.tick(60)


def parse_args():
    """
Parses arguments for this program.
Returns an object with the following members:
args.
serialport -- str
verbose -- bool
map -- str
"""    
    parser = argparse.ArgumentParser(
        description='Final project: Tactics 2',
        epilog = 'If SERIALPORT is not specified, stdin/stdout are used.')

    parser.add_argument('-s', '--serial',
                        help='path to serial port',
                        dest='serialport',
                        default=None)
    parser.add_argument('-d', dest='verbose',
                        help='debug',
                        action='store_true')
    parser.add_argument('-m', '--map', dest='map',
                        help='map to load',
                        default="map-1")

    return parser.parse_args()


if __name__ == '__main__':
    main()
