import melee

console = melee.Console(dolphin_executeable_path="C:\Users\semor\AppData\Roaming\Slippi Launcher\netplay")

controller = melee.Controller(console=console, port=1)
controller_human = melee.Controller(console=console,
                                    port=2,
                                    type=melee.ControllerType.GCN_ADAPTER)

console.run()
console.connect()

controller.connect()
controller_human.connect()

while True:
    gamestate = console.step()
    # Press buttons on your controller based on the GameState here!

    if gamestate.menu_state in [melee.enums.Menu.IN_GAME, melee.enums.Menu.SUDDEN_DEATH]:
        if gamestate.distance < 4:
            controller.press_button(melee.enums.Button.BUTTON_B)
            controller.tilt_analog(melee.enums.Button.BUTTON_MAIN,0.5,0)
        else:
            controller.empty_input()
    else:
        melee.menuhelper.MenuHelper.menu_helper_simple(gamestate, controller,controller.port,melee.enums.Character.FOX, melee.enums.Stage.POKEMON_STADIUM, "", autostart=False, swag=True)
