import libtcodpy as libtcod
from gameObject import Object
from tile import Tile

#Set the size of our window
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

#Set the size of our playable map
MAP_WIDTH = 80
MAP_HEIGHT = 45

#Set the framerate limit. We do not use this, as our game is turn based, not real time
LIMIT_FPS = 20

#Set the colors for floor and wall tiles
color_dark_wall = libtcod.Color(105, 105, 105)
color_dark_ground = libtcod.Color(211, 211, 211)

def make_map():
    global map

    #Fill map with unblocked tiles
    map = [[Tile(False)
        for y in range(MAP_HEIGHT) ]
            for x in range(MAP_WIDTH) ]

    #Set up a few columns to test map placement
    map[30][22].blocked = True
    map[30][22].block_sight = True
    map[50][22].blocked = True
    map[50][22].block_sight = True
    map[75][15].blocked = True
    map[75][15].block_sight = True



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
        player.move(0, -1)
    elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
        player.move(0, 1)
    elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
        player.move(1, 0)
    elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
        player.move(-1, 0)

def render_all():
    #Draw the map
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            wall = map[x][y].block_sight
            if wall:
                libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET)
            else:
                libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET)

    #Draw all objects in the list
    for object in objects:
        object.draw()

    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)


#####################################
# Initialization and Main Loop
####################################

#Tell the engine which font to use, and what type of font it is
libtcod.console_set_custom_font('fonts/arial10x10.png', libtcod.FONT_TYPE_GRAYSCALE | libtcod.FONT_LAYOUT_TCOD)

#Initialize the console window, set its size, title, and tell it to not go fullscreen
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'DungeonCrawler', False)

#Set up a off-screen console to act as a drawing buffer
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

#Use this line to limit the FPS of the game, since ours is turn-based, this will have no effect
#libtcod.sys_set_fps(LIMIT_FPS)

#Create the map
make_map()

#Create our objects, in this case just a player and an NPC, then add them to the objects array
player = Object(con, map, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, '@', libtcod.white)
npc = Object(con, map, SCREEN_WIDTH / 2 - 5, SCREEN_HEIGHT / 2, '@', libtcod.yellow)
objects = [npc, player]

while not libtcod.console_is_window_closed():
    #Render the map, and all objects
    render_all()

    libtcod.console_flush()

    #Stop character trails by placing a space where the object is. If they don't move, their icon will overwrite this
    for object in objects:
        object.clear()

    #Decide what to do. If the escape key is pressed, handle_keys returns true, and we exit the game, otherwise,
    #we process the key press accordingly
    exit = handle_keys()
    if exit:
        break

