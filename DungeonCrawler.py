import libtcodpy as libtcod
import xml.etree.ElementTree as ET
import textwrap
from gameObject import *
from tile import Tile
from rect import Rect

#TODO: Change gameObject to only take base arguments, but have methods that require advanced map objects
#This will allow for creation of objects before the map has been initialized.

#Set the size of our window
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

#Set the size of our playable map
MAP_WIDTH = 80
MAP_HEIGHT = 43

#Set the framerate limit. We do not use this, as our game is turn based, not real time
LIMIT_FPS = 20

#Set parameters for room generation
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 4
MAX_ROOMS = 30

#Set the colors for floor and wall tiles
color_dark_wall = libtcod.Color(63, 63, 63)
color_light_wall = libtcod.Color(159, 159, 159)
color_dark_ground = libtcod.Color(63, 50, 31)
color_light_ground = libtcod.Color(158, 134, 100)

#Field of View Algorithm settings
FOV_ALGO = 0
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 4

#Sizes and Coordinates for the GUI
BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
INVENTORY_WIDTH = 50

#Message log constants
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1

#Monster and object settings
MAX_ROOM_MONSTERS = 3
MAX_ROOM_ITEMS = 2

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

                #add some contents to this room, such as monsters, objects etc. We never add creatures to the
                #starting room
                place_objects(new_room)

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

def place_objects(room):
    global monsters
    global monster_appearance_chances
    global items
    global item_appearance_chances

    #Place Monsters in each room, randomly or course
    num_monsters = libtcod.random_get_int(0, 0, MAX_ROOM_MONSTERS)

    for i in range(num_monsters):
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

        if not is_blocked(x, y):
            #Choose a monster to spawn from the list of applicable monsters
            spawn = random_choice_index(monster_appearance_chances)

            #Choose the monster based on the spawn chance
            monster = monsters[spawn]

            #Create a death function for the monster
            monster_death = getattr(Fighter, 'monster_death')

            #Create a component for the monster based on the monster type
            if monster[1] == 'fighter':
                fighter_component = Fighter(hp = int(monster[3]), defense = int(monster[4]), power = int(monster[5]),
                    death_function = monster_death)

            #Create an AI component for the monster based on its AI type
            if monster[2] == 'basic':
                ai_component = BasicMonster()

            #Finally, create the monster
            monster = Object(x, y, char = monster[6], name = monster[0], color = libtcod.Color(int(monster[7]),
                int(monster[8]), int(monster[9])), blocks = True, fighter = fighter_component,  ai = ai_component)

            #Add the monster to the objects array
            objects.append(monster)

    #Place items in each room, randomly as well
    num_items = libtcod.random_get_int(0, 0, MAX_ROOM_ITEMS)

    for i in range(num_items):
        #Create x num_items number of items in this room
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

        if not is_blocked(x, y):
            #Find the use function for this object, and apply it to the item
            item_use_function = getattr(Item, 'cast_heal')
            item_component = Item(use_function = item_use_function)
            item = Object(x, y, '!', 'Small Healing Potion', libtcod.violet, item = item_component)
            objects.append(item)

def random_choice_index(chances):
    #Choose an option from a list of chances
    #Roll a die, whcih will land somewhere between 1 and the total of the chances list
    #Then, we simply need to figure out what range in the list that number falls under
    dice = libtcod.random_get_int(0, 1, sum(chances))

    running_sum = 0
    choice = 0
    #Go through all chances, keeping the total so far
    for w in chances:
        running_sum += w

        #Check if the die roll is smaller or equal to the current total.
        #If it is, we know the chance range the roll fell into
        if dice <= running_sum:
            return choice
        choice += 1

def is_blocked(x, y):
    #Test the map tile at the coordinates to see if it is blocked or not
    if map[x][y].blocked:
        return True

    #Then, check through all objects and see if any of them are blocking
    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return True

    #There is no object or tile blocking this position
    return False

def player_move_or_attack(dx, dy):
    global fov_recompute

    #Figure out where the player wants to move to
    x = player.x + dx
    y = player.y + dy

    #Check if there is a valid target at the destination
    target = None
    for object in objects:
        if object.fighter and object.x == x and object.y == y:
            target = object
            break

    #If there is a valid target at the destination, attack it, if not, move there
    if target is not None:
        messages = player.fighter.attack(target)
        for line, color in messages:
            message(line, color)
    else:
        blocked = is_blocked(x, y)
        player.move(map, dx, dy, blocked)
        fov_recompute = True

def handle_keys():
    global player_x, player_y
    global fov_recompute
    global map
    global key
    global inventory
    global objects

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
        return 'exit'

    #Handle movement keys
    #Also, flag the field of view for re-computation each time the player moves
    if game_state == 'playing':
        if key.vk == libtcod.KEY_UP:
            player_move_or_attack(0, -1)
        elif key.vk == libtcod.KEY_DOWN:
            player_move_or_attack(0, 1)
        elif key.vk == libtcod.KEY_RIGHT:
            player_move_or_attack(1, 0)
        elif key.vk == libtcod.KEY_LEFT:
            player_move_or_attack(-1, 0)
        else:
            #Test for other keys
            key_char = chr(key.c)

            if key_char == 'g':
                #pick up an item
                for object in objects:
                    #Check for an item in the players currently occupied tile
                    if object.x == player.x and  object.y == player.y and object.item:
                        #Check if its an item, and then pick it up
                        action_result = object.item.pick_up(inventory, objects)
                        #Print out any messages associated with this action
                        for line, color in action_result:
                            message(line, color)
                        break
            if key_char == 'i':
                #Show the inventory
                chosen_item = inventory_menu("Press the key of the item of you would like to use, or any other to cancel")
                if chosen_item is not None:
                    #Get and print out any messages returned by item use
                    action_result = chosen_item.use(inventory, player)
                    for line, color in action_result:
                        message(line, color)


            return 'didnt-take-turn'

def get_names_under_mouse():
    global mouse

    #rGet the coordinates of the mouse click
    (x, y) = (mouse.cx, mouse.cy)

    #create a list with the names of all objects at the mouses coordinates, and within FOV
    names = [obj.name for obj in objects
        if obj.x == x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y)]
    #Separate all names with commas, and capitalize them
    names = ', '.join(names)
    return names.capitalize()

def message(new_msg, color = libtcod.white):
    #Split the message to multiple lines if its too long
    #wrapper = TextWrapper()

    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

    for line in new_msg_lines:
        #Check if the buffer is full, if so, remove the first line to make room for the new line
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]

        #Add the new line as a tuple, setting the text and the text color
        game_msgs.append((line, color))

def menu(header, options, width):
    #First, make sure the menu has 26 or fewer items (This is due to an alphabetical selection limitation)
    if len(options) > 26:
        raise ValueError('Cannot have a menu with more than 26 options!')

    #implicitly calculate the height of the window, based on the header height (after word wrap) and the number
    # of options
    header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
    height = len(options) + header_height

    #Create an offscreen console that represents the menus window
    window = libtcod.console_new(width, height)

    #Print the header to our offscreen console
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    #Print all the options, with a corresponding ASCII character
    y = header_height
    #Get the ASCII value of the letter 'a'
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1

    #Blit the contents of the window to the main game screen, centered
    x = SCREEN_WIDTH / 2 - width / 2
    y = SCREEN_HEIGHT /2 - height / 2
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    #Now that the console is presented to the player, wait for them to make a choice before doing anything else
    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)

    #Convert the ASCII code to an index; if it corresponds to a valid menu item, return it
    index = key.c - ord('a')
    if index >= 0 and index < len(options): return index
    return None

def inventory_menu(header):
    #Show a menu with each item of the inventory as an option
    if len(inventory) == 0:
        options = ['Inventory is empty!']
    else:
        options = [item.name for item in inventory]

    index = menu(header, options, INVENTORY_WIDTH)

    #Return the item that was chosen, if any
    if index is None or len(inventory) == 0: return None
    return inventory[index].item

def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    #Build and render a status bar (health, mana, experience, etc)
    bar_width = int(float(value) / maximum * total_width)

    #Render the background first
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    #Now, render the bar on top
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    #Finally, put the name of the bar, and the actual values on top of everything, for clarity
    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
        name + ': ' + str(value) + '/' + str(maximum))

def render_all():
    global fov_map, color_dark_wall, color_light_wall
    global color_dark_ground, color_light_ground
    global fov_recompute
    global con

    if fov_recompute:
        #Recompute the Field of view (Player movement, door opened, etc)
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

        #Draw the map, set each tiles color according to the Field of View
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                wall = map[x][y].block_sight
                if not visible:
                    #This tile is not visible, check if its been explored
                    if map[x][y].explored:
                        #This tile has not been explored yet, so do not show it
                        if wall:
                            libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET)
                        else:
                            libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET)
                else:
                    #This tile is visible
                    if wall:
                        libtcod.console_set_char_background(con, x, y, color_light_wall, libtcod.BKGND_SET)
                    else:
                        libtcod.console_set_char_background(con, x, y, color_light_ground, libtcod.BKGND_SET)
                    #Mark the tile as explored, so it will continue to show on the map
                    map[x][y].explored = True

    #Draw all objects in the list
    for object in objects:
        if object != player:
            object.draw(fov_map, con)
    #Draw the player last so it appears on top of everything else
    player.draw(fov_map, con)

    libtcod.console_blit(con, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 0, 0)

    #Prepare to render the GUI panel
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    #Show the players stats
    render_bar(1, 1, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp,
        libtcod.light_red, libtcod.darker_red)

    #Display the names of objects under the mouse
    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse())

    #Print out messages in the game messages log
    y = 1
    for (line, color) in game_msgs:
        libtcod.console_set_default_foreground(panel, color)
        libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
        y += 1

    #Blit the new console for the GUI onto the screen
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

#####################################
# Initialization and Main Loop
####################################

#Tell the engine which font to use, and what type of font it is
libtcod.console_set_custom_font('fonts/arial10x10.png', libtcod.FONT_TYPE_GRAYSCALE | libtcod.FONT_LAYOUT_TCOD)

#Initialize the console window, set its size, title, and tell it to not go fullscreen
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'DungeonCrawler', False)

#Set up a off-screen console to act as a drawing buffer
con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)

#Use this line to limit the FPS of the game, since ours is turn-based, this will have no effect
libtcod.sys_set_fps(LIMIT_FPS)

#Initialize the objects array
objects = []

#Figure out which monsters to include on this level, and load them all
#TODO: For each level, the player can encounter monsters from the previous level, as well as the next level
#There is a 50% decrease in encounter chances for previous level monsters
#There is a 75% decrease in encounter chances for next level monsters
#This will keep the chance of difficult monsters a possibility on any level
monster_tree = ET.parse('monsters/level-0.xml')
monster_root = monster_tree.getroot()

monsters = []

#Create a list with all the applicable monsters for this floor
for monster in monster_root.findall('monster'):
    m = []
    m.append(monster.get('name'))
    m.append(monster.find('type').text)
    m.append(monster.find('ai-type').text)
    m.append(monster.find('hit-points').text)
    m.append(monster.find('defense').text)
    m.append(monster.find('attack-power').text)
    m.append(monster.find('character').text)
    m.append(monster.find('color-r').text)
    m.append(monster.find('color-g').text)
    m.append(monster.find('color-b').text)
    m.append(monster.find('encounter-chance').text)

    #Add the newly created monster list to the list of monsters
    monsters.append(m)

#Next, build a list with just the monster appearance chances, so we can figure out later how often each monster will
#show up. The index of the chance in this list directly corresponds to the index of the monster in the monsters list
monster_appearance_chances = []

for appearing_monster in monsters:
    monster_appearance_chances.append(int(appearing_monster[10]))

#Create the map
make_map()

fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
for y in range(MAP_HEIGHT):
    for x in range(MAP_WIDTH):
        libtcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)

#Create our objects, in this case just a player, then add them to the objects array
#Create a fighter component for the player. The player does not need an AI
player_death = getattr(Fighter, 'player_death')
fighter_component = Fighter(hp = 30, defense = 2, power = 5, death_function = player_death)
player = Object(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, '@', 'player', libtcod.white, True,
    fighter = fighter_component)
player.x = player_start_x
player.y = player_start_y

#Add the player to the objects array, which will be drawn to the screen
objects.insert(0, player)

game_state = 'playing'
player_action = None
fov_recompute = True

#Create a panel for the GUI
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

#Create an empty list for game messages
game_msgs = []

#Add a welcome message
message('Welcome Stranger! Prepare to perish in the Dungeons of Un-imaginable sorrow!', libtcod.red)

mouse = libtcod.Mouse()
key = libtcod.Key()

#Initialize the players inventory, empty of course
inventory = []

while not libtcod.console_is_window_closed():
    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

    #Render the map, and all objects
    render_all()

    libtcod.console_flush()

    #Stop character trails by placing a space where the object is. If they don't move, their icon will overwrite this
    for object in objects:
        object.clear(con)

    #Decide what to do. If the escape key is pressed, handle_keys returns true, and we exit the game, otherwise,
    #we process the key press accordingly
    player_action = handle_keys()
    if player_action == 'exit':
        break

    player_alive = player.check_if_dead()
    if not player_alive:
        game_state = 'dead'

    #Let the monsters take their turn
    if game_state == 'playing' and player_action != 'didnt-take-turn':
        for object in objects:
            if object.ai:
               messages = object.ai.take_turn(map, fov_map, player, objects)
               if len(messages) > 0:
                   for line, color in messages:
                       message(line, color)

