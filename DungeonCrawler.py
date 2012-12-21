import libtcodpy as libtcod
from gameObject import Object
from tile import Tile
from rect import Rect

#Set the size of our window
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

#Set the size of our playable map
MAP_WIDTH = 80
MAP_HEIGHT = 45

#Set the framerate limit. We do not use this, as our game is turn based, not real time
LIMIT_FPS = 20

#Set parameters for room generation
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 4
MAX_ROOMS = 30

#Set the colors for floor and wall tiles
color_dark_wall = libtcod.Color(85, 85, 85)
color_dark_ground = libtcod.Color(117, 104, 87)

def make_map():
    global map
    global player_start_x
    global player_start_y

    #Fill map with blocked tiles, this will allow us to 'carve' rooms for the player
    #to explore
    map = [[Tile(True)
        for y in range(MAP_HEIGHT) ]
            for x in range(MAP_WIDTH) ]

    rooms = []
    num_rooms = 0

    for r in range(MAX_ROOMS):
        #Generate a random width and height for each room
        w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)

        #Generate a random map position, inside the bounds of the map
        x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
        y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h -1)

        #Create a new room from the random numbers
        new_room = Rect(x, y, w, h)

        #Run through all the other rooms and see if they intersect with this one
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break

        if not failed:
            #If we've gotten here, the room is valid, and does not intersect any other rooms
            #Carve the room into the maps tiles
            create_room(new_room)

            #Get the center coordinates for the new room
            (new_x, new_y) = new_room.center()

            if num_rooms == 0:
                #This is the first room created, so start the player off in the center
                player_start_x = new_x
                player_start_y = new_y
            else:
                #This is not the first room, so connect it to the previous room via tunnels

                #Get the center coordinates for the previous room
                (prev_x, prev_y) = rooms[num_rooms - 1].center()

                #Flip a coin to see if we move horizontally, or vertically first
                if libtcod.random_get_int(0, 0, 1) == 1:
                    #Tunnel horizontally first, then vertically
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:
                    #Tunnel vertically first, then horizontally
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)

            #Finally, append the newly added room to the rooms list
            rooms.append(new_room)
            num_rooms += 1


def create_room(room):
    global map
    #go through each tile in the rectangle and make them passable
    #range() will exclude the last value in the range, which is perfect,
    #as we want a one block thick wall surrounding the room
    for x in range(room.x1, room.x2):
        for y in range(room.y1, room.y2):
            map[x][y].blocked = False
            map[x][y].block_sight = False

def create_h_tunnel(x1, x2, y):
    #carve a horizontal tunnel from x1 to x2
    global map
    for x in range(min(x1, x2), max(x1, x2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def create_v_tunnel(y1, y2, x):
    #carve a vertical tunnel from y1 to y2
    global map
    for y in range(min(y1, y2), max(y1, y2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False


def handle_keys():
    global player_x, player_y

    #Wait for the player to press a key before continuing
    key = libtcod.console_wait_for_keypress(True)

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #ALT + Enter, toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif key.vk == libtcod.KEY_SHIFT and key.lalt:
        #Redraw the map, and move the player to the first room
        #Debug and testing purposes only
        map = []
        make_map()
        player.x = player_start_x
        player.y = player_start_y

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

#Create our objects, in this case just a player, then add them to the objects array
player = Object(con, map, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, '@', libtcod.white)
player.x = player_start_x
player.y = player_start_y

objects = []
objects.insert(0, player)

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

