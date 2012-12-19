import libtcodpy as libtcod

#Set the size of our window
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

#Set the framerate limit. We do not use this, as our game is turn based, not real time
LIMIT_FPS = 20

def handle_keys():
    global player_x, player_y

    #Wait for the player to press a key before continuing
    key = libtcod.console_wait_for_keypress(True)

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #ALT + Enter, toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif key.vk == libtcod.KEY_ESCAPE:
        #Escape, exit game
        return True

    #Handle movement keys
    if libtcod.console_is_key_pressed(libtcod.KEY_UP):
        player_y -= 1
    elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
        player_y += 1
    elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
        player_x += 1
    elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
        player_x -= 1

#Tell the engine which font to use, and what type of font it is
libtcod.console_set_custom_font('fonts/arial10x10.png', libtcod.FONT_TYPE_GRAYSCALE | libtcod.FONT_LAYOUT_TCOD)

#Initialize the console window, set its size, title, and tell it to not go fullscreen
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'DungeonCrawler', False)

#Use this line to limit the FPS of the game, since ours is turn-based, this will have no effect
#libtcod.sys_set_fps(LIMIT_FPS)

player_x = SCREEN_WIDTH / 2
player_y = SCREEN_HEIGHT / 2

while not libtcod.console_is_window_closed():
    #Set the foreground (text color) of console 1 (our main window) to white
    libtcod.console_set_default_foreground(0, libtcod.white)
    libtcod.console_put_char(0, player_x, player_y, '@', libtcod.BKGND_NONE)
    libtcod.console_flush()

    #Stop character trails by placing a space where the player is. If they don't move, their icon will overwrite this
    libtcod.console_put_char(0, player_x, player_y, ' ', libtcod.BKGND_NONE)

    #Decide what to do. If the escape key is pressed, handle_keys returns true, and we exit the game, otherwise,
    #we process the key press accordingly
    exit = handle_keys()
    if exit:
        break

