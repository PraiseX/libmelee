import argparse
import signal
import sys
import melee
import random

from melee.enums import Action
from melee.gamestate import GameState
from melee import *

# This example program demonstrates how to use the Melee API to run a console,
#   setup controllers, and send button presses over to a console


def check_port(value):
    ivalue = int(value)
    if ivalue < 1 or ivalue > 4:
        raise argparse.ArgumentTypeError("%s is an invalid controller port. \
                                         Must be 1, 2, 3, or 4." % value)
    return ivalue


parser = argparse.ArgumentParser(description='Example of libmelee in action')
parser.add_argument('--port', '-p', type=check_port,
                    help='The controller port (1-4) your AI will play on',
                    default=2)
parser.add_argument('--opponent', '-o', type=check_port,
                    help='The controller port (1-4) the opponent will play on',
                    default=1)
parser.add_argument('--debug', '-d', action='store_true',
                    help='Debug mode. Creates a CSV of all game states')
parser.add_argument('--address', '-a', default="127.0.0.1",
                    help='IP address of Slippi/Wii')
parser.add_argument('--dolphin_executable_path', '-e', default=None,
                    help='The directory where dolphin is')
parser.add_argument('--connect_code', '-t', default="",
                    help='Direct connect code to connect to in Slippi Online')
parser.add_argument('--iso', default=None, type=str,
                    help='Path to melee iso.')

args = parser.parse_args()

# This logger object is useful for retroactively debugging issues in your bot
#   You can write things to it each frame, and it will create a CSV file describing the match
log = None
if args.debug:
    log = melee.Logger()

# Create our Console object.
#   This will be one of the primary objects that we will interface with.
#   The Console represents the virtual or hardware system Melee is playing on.
#   Through this object, we can get "GameState" objects per-frame so that your
#       bot can actually "see" what's happening in the game
console = melee.Console(path=args.dolphin_executable_path,
                        slippi_address=args.address,
                        logger=log)

# Create our Controller object
#   The controller is the second primary object your bot will interact with
#   Your controller is your way of sending button presses to the game, whether
#   virtual or physical.
controller = melee.Controller(console=console,
                              port=args.port,
                              type=melee.ControllerType.STANDARD)

controller_opponent = melee.Controller(console=console,
                                       port=args.opponent,
                                       type=melee.ControllerType.GCN_ADAPTER)

# This isn't necessary, but makes it so that Dolphin will get killed when you ^C


def signal_handler(sig, frame):
    console.stop()
    if args.debug:
        log.writelog()
        print("")  # because the ^C will be on the terminal
        print("Log file created: " + log.filename)
    print("Shutting down cleanly...")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

# Run the console
console.run(iso_path=args.iso)

# Connect to the console
print("Connecting to console...")
if not console.connect():
    print("ERROR: Failed to connect to the console.")
    sys.exit(-1)
print("Console connected")

# Plug our controller in
#   Due to how named pipes work, this has to come AFTER running dolphin
#   NOTE: If you're loading a movie file, don't connect the controller,
#   dolphin will hang waiting for input and never receive it
print("Connecting controller to console...")
if not controller.connect():
    print("ERROR: Failed to connect the controller.")
    sys.exit(-1)
print("Controller connected")

costume = 0
framedata = melee.framedata.FrameData()

# Our action functions
def waveShine():
    controller.press_button(melee.Button.BUTTON_B)
    controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0)
    
    if gamestate.players[2].action == Action.DOWN_B_STUN:
        controller.press_button(melee.Button.BUTTON_X)
    if gamestate.players[2].action in jumping:
        controller.press_button(melee.Button.BUTTON_R)
        controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0)

def getup():
    defenseChoice = random.randint(0, 3)
    #print(defenseChoice)
    # up
    if defenseChoice == 0:
        controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 0.5, 1)
    # left
    if defenseChoice == 1:
        controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 0, 0.5)
    # right
    if defenseChoice == 2:
        controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 1, 0.5)
    # a button
    if defenseChoice == 3:
        controller.press_button(melee.Button.BUTTON_A)
    controller.empty_input()

def recover(gamestate, pos):
    if pos == "above":
        if gamestate.players[1].x > 0:
            controller.press_button(melee.Button.BUTTON_B)
            controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 0, 0.5)
            # print("wants to side b left")

        else:
            controller.press_button(melee.Button.BUTTON_B)
            controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 1, 0.5)
            # print("wants to side b right")

    elif pos == "below":
        if gamestate.players[1].x > 0:
            controller.press_button(melee.Button.BUTTON_B)
            controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 0, 1)
            # print("wants to up b left")

        else:
            controller.press_button(melee.Button.BUTTON_B)
            controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 1, 1)
            # print("wants to up b right")

    if abs(gamestate.players[2].x) > abs(melee.stages.EDGE_POSITION[gamestate.stage]):
            # is above ledge
            if abs(gamestate.players[2].y) > abs(melee.stages.EDGE_POSITION[gamestate.stage]):
                if gamestate.players[2].x > 0:
                    controller.press_button(melee.Button.BUTTON_B)
                    controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 0, 0.5)
                    # print("wants to side b left")
                else:
                    controller.press_button(melee.Button.BUTTON_B)
                    controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 1, 0.5)
                    # print("wants to side b right")

            else:
                if gamestate.players[2].x > 0:
                    controller.press_button(melee.Button.BUTTON_B)
                    controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 0, 1)
                    # print("wants to up b left")

                else:
                    controller.press_button(melee.Button.BUTTON_B)
                    controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 1, 1)
                    # print("wants to up b right")

frame_count = 0

# Main loop
while True:
    # "step" to the next frame
    gamestate = console.step()
    if gamestate is None:
        continue

    # The console object keeps track of how long your bot is taking to process frames
    #   And can warn you if it's taking too long
    if console.processingtime * 1000 > 12:
        print("WARNING: Last frame took " +
              str(console.processingtime*1000) + "ms to process.")

    # What menu are we in?
    if gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:

        # Slippi Online matches assign you a random port once you're in game that's different
        #   than the one you're physically plugged into. This helper will autodiscover what
        #   port we actually are.
        discovered_port = args.port
        if args.connect_code != "":
            discovered_port = melee.gamestate.port_detector(
                gamestate, melee.Character.FOX, costume)
        if discovered_port > 0:
            # NOTE: This is where your AI does all of its stuff!
            # This line will get hit once per frame, so here is where you read
            # in the gamestate and decide what buttons to push on the controller

            # print(gamestate.players[1].action)

            controller.release_all()

            knockDown = [Action.LYING_GROUND_UP, Action.LYING_GROUND_DOWN, Action.LYING_GROUND_UP_HIT]
            jumping = [Action.JUMPING_ARIAL_FORWARD, Action.JUMPING_ARIAL_BACKWARD]
            #print(gamestate.players[2].x, gamestate.players[2].y)
           
       
            distanceY = abs(gamestate.players[1].y - gamestate.players[2].y)
            # print(distanceY)
            # Nuetral Game
            if gamestate.distance > 15 and distanceY <= 30:
                # Follow

                onleft = gamestate.players[2].x < gamestate.players[1].x
                controller.tilt_analog(melee.Button.BUTTON_MAIN, int(onleft), 0.5)
                # if abs(gamestate.players[2].x) < abs(melee.stages.EDGE_POSITION[gamestate.stage]) - 5:
                #     controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0.5)
            
            # Get off ledge and stop teetering
            if gamestate.players[2].action == Action.EDGE_HANGING or Action.EDGE_TEETERING or Action.EDGE_TEETERING_START:
                controller.press_button(melee.Button.BUTTON_A)
                # print("wants to get off ledge")

            if gamestate.players[2].action == Action.GRAB_WAIT:
                if gamestate.players[2].x <= 0:
                    controller.tilt_analog(melee.Button.BUTTON_MAIN, 0, 0.5)
                else:
                    controller.tilt_analog(melee.Button.BUTTON_MAIN, 1, 0.5)

            if gamestate.players[2].action == Action.UPSMASH or Action.DOWNSMASH or Action.FSMASH_MID:
                controller.release_button(melee.Button.BUTTON_A)

            # Get up
            if gamestate.players[2].action in knockDown:
                defenseChoice = random.randint(0, 3)
                # up
                if defenseChoice == 0:
                    controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 1)
                # left
                if defenseChoice == 1:
                    controller.tilt_analog(melee.Button.BUTTON_MAIN, 0, 0.5)
                # right
                if defenseChoice == 2:
                    controller.tilt_analog(melee.Button.BUTTON_MAIN, 1, 0.5)
                # a button
                if defenseChoice == 3:
                    controller.press_button(melee.Button.BUTTON_A)
                controller.empty_input()

            # Recover
            if abs(gamestate.players[2].x) > abs(melee.stages.EDGE_POSITION[gamestate.stage]):
                #print(melee.stages.EDGE_POSITION[gamestate.stage].x)
                    #print(melee.stages.EDGE_POSITION[gamestate.stage].y)
                    # print(gamestate.players[2].x)
                    if gamestate.players[2].x <= -melee.stages.EDGE_POSITION[gamestate.stage] - 10:
                        if gamestate.players[2].y >= -17:
                            controller.press_button(melee.Button.BUTTON_B)
                            controller.tilt_analog(melee.Button.BUTTON_MAIN, 1, 0.5)
                            # print("wants to side b right")

                        elif gamestate.players[2].y < -30:
                            controller.press_button(melee.Button.BUTTON_B)
                            controller.tilt_analog(melee.Button.BUTTON_MAIN, 1, 1)
                            # print("wants to up b right")
                        else:
                            controller.press_button(melee.Button.BUTTON_Y)
                            controller.tilt_analog(melee.Button.BUTTON_MAIN, 1, 0.5)
                            # print("wants to jump right")

                    elif gamestate.players[2].x >= melee.stages.EDGE_POSITION[gamestate.stage] + 10:
                        if gamestate.players[2].y >= -17:

                            controller.press_button(melee.Button.BUTTON_B)
                            controller.tilt_analog(melee.Button.BUTTON_MAIN, 0, 0.5)
                            # print("wants to side b left")

                        elif gamestate.players[2].y < -30:
                            controller.press_button(melee.Button.BUTTON_B)
                            controller.tilt_analog(melee.Button.BUTTON_MAIN, 0, 1)
                            # print("wants to up b left")
                        else:
                            controller.press_button(melee.Button.BUTTON_Y)
                            controller.tilt_analog(melee.Button.BUTTON_MAIN, 0, 0.5)
                            # print("wants to jump left")          
            # Attacking
            else:
                # Get some damage in
                if gamestate.players[1].percent < 60:
                    
                    attackPick = random.randint(0, 3)
                    if gamestate.distance < 10:
                        # Grab
                        if attackPick == 0:
                            controller.tilt_analog(melee.Button.BUTTON_C, .5, 0)
                        else:        
                            # Shine
                                controller.press_button(melee.Button.BUTTON_B)
                                controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0)
                                # if gamestate.players[2].action == Action.DOWN_B_STUN:
                                #     controller.press_button(melee.Button.BUTTON_X)
                                # if gamestate.players[2].action in jumping:
                                #     controller.press_button(melee.Button.BUTTON_R)
                                #     controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0)

                else:
                    # Up smash
                    if gamestate.distance < 10:
                        attackPick = random.randint(0, 1)
                        if attackPick == 0:
                            if gamestate.players[2].x > gamestate.players[1].x:
                                controller.tilt_analog(melee.Button.BUTTON_C, 0, 0.5)
                            else:
                                controller.tilt_analog(melee.Button.BUTTON_C, 1, 0.5)
                        else:
                            controller.tilt_analog(melee.Button.BUTTON_C, .5, 1)


        else:
            # If the discovered port was unsure, reroll our costume for next time
            costume = random.randint(0, 4)

        # Log this frame's detailed info if we're in game
        if log:
            log.logframe(gamestate)
            log.writeframe()
    else:
        melee.MenuHelper.menu_helper_simple(gamestate, controller,
                                            melee.Character.FOX,
                                            melee.Stage.YOSHIS_STORY,
                                            args.connect_code,
                                            costume=costume,
                                            autostart=True,
                                            swag=False)

        # If we're not in game, don't log the frame
        if log:
            log.skipframe()