import libtcodpy as libtcod
import textwrap
import shelve
from random import randrange

from mapGenerators.standardDungeon import *
from mapGenerators.cavern import *

from gameObject import *
from tile import Tile
from rect import Rect

#Object Components
from objectComponent.fighter import *
from objectComponent.item import *

#Fighter AIs
from fighterAi.basic import *

#TODO: Change gameObject to only take base arguments, but have methods that require advanced map objects
#This will allow for creation of objects before the map has been initialized.

#Set the size of our window
SCREEN_WIDTH = 100
SCREEN_HEIGHT = 80

#Set the size of our playable map
MAP_WIDTH = SCREEN_WIDTH - (SCREEN_WIDTH / 4) - 1
MAP_HEIGHT = SCREEN_HEIGHT - (SCREEN_HEIGHT / 6) - 1

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
PANEL_HEIGHT = (SCREEN_HEIGHT / 6) - 1
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
INVENTORY_WIDTH = 50

INFO_WIDTH = (SCREEN_WIDTH / 4) - 2
INFO_HEIGHT = MAP_HEIGHT

#Message log constants
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 3

#Monster and object settings
MAX_ROOM_MONSTERS = 3
MAX_ROOM_ITEMS = 2

#Experience and Level up amounts
LEVEL_UP_BASE = 200
LEVEL_UP_FACTOR = 150
LEVEL_SCREEN_WIDTH = 40
CHARACTER_SCREEN_WIDTH = 45


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


def target_tile(max_range = None):
    #Return the coordinates of a tile left clicked in the players FOV (or optionally within a range)
    global key, mouse
    while True:
        #Render the screen, this erases the inventory screen, and shows the names of objects under the mouse
        libtcod.console_flush()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
        render_all()

        (x, y) = (mouse.cx, mouse.cy)

        if mouse.lbutton_pressed and libtcod.map_is_in_fov(fov_map, x, y) and \
           (max_range is None or player.distance(x, y <= max_range)):
            return x, y

        if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:
            #Right click and escape cancel tile selection
            return None, None


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
        for success, line, color in messages:
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
    global stairs_down
    global examineText

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #ALT + Enter, toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif key.vk == libtcod.KEY_ESCAPE:
        #Escape, exit game
        libtcod.console_set_default_background(0, libtcod.black)
        libtcod.console_clear(0)
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
                        print_messages(object.item.pick_up(inventory, objects))
                        break
            if key_char == 'i':
                #Show the inventory
                chosen_item = inventory_menu("Press the key of the item of you would like to use, or any other to "
                                             "cancel")
                if chosen_item is not None:
                    #Get and print out any messages returned by item use
                    #Set the coordinates to none. They will be set if we actually need to use them (targeting)
                    (x, y) = (None, None)
                    if chosen_item.type != 'equipment':
                        if chosen_item.targeting == 'manual':
                            message('Left-click a tile to target, or right-click to cancel.', libtcod.light_cyan)
                            (x, y) = target_tile()

                    print_messages(chosen_item.use(inventory, player, objects, fov_map, x, y))

            if key_char == '>':
                #Go down the stairs, but first check to ensure the player is standing directly on top of them
                if stairs_down.x == player.x and stairs_down.y == player.y:
                    next_level()

            if key_char == 'd':
                #show the inventory, and if an item is selected, drop it
                chosen_item = inventory_menu('Press the key of the item you wish to drop, or any other to cancel.\n')
                if chosen_item is not None:
                    print_messages(chosen_item.drop(objects, inventory, player))

            if key_char == 'e':
                #show the inventory, and if an item is selected, show the examine screen for it
                chosen_item = inventory_menu('Press the key of the item you wish to examine, or any other key to '
                                             'cancel.\n')
                if chosen_item is not None:
                    #We need to handle equipment a little differently, as it can have different values based on its type
                    if chosen_item.type == 'equipment':
                        examineText = chosen_item.owner.name + '\n\n' + chosen_item.description + '\n\n'
                        if chosen_item.owner.equipment.use == 'attack':
                            #Add a value for damage
                            examineText += 'Damage: ' + chosen_item.owner.equipment.value
                        elif chosen_item.owner.equipment.use == 'defense':
                            #add a value for defense
                            examineText += 'Defense: ' + chosen_item.owner.equipment.value
                        examineText += '\nEquips on: ' + chosen_item.owner.equipment.slot
                    else:
                        examineText = chosen_item.owner.name + '\n\n' + chosen_item.description + '\n\n'
                    return 'examining'

            if key_char == 'c':
                #Show the character sheet
                level_up_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
                msgbox('Character Information\n\nLevel: ' + str(player.level) + '\nExperience: ' + str(player.fighter.xp) +
                '\nExperience to Level up: ' + str(level_up_xp) + '\n\nMaximum HP: ' + str(player.fighter.max_hp) +
                '\nStrength: ' + str(player.fighter.base_strength) + '\nDefense: ' + str(player.fighter.base_defence) +
                '\nAgility: ' + str(player.fighter.base_agility) + '\nAccuracy: ' + str(player.fighter.base_accuracy) +
                '\n\nYou are capable of dealing ' + str(player.fighter.damage) + ' damage (' + str(player.fighter.equipmentDamage) +
                ' comes from equipped weapons)' + '\n\nYou can absorb ' + str(player.fighter.protection) + ' damage (' +
                str(player.fighter.equipmentProtection) + ' comes from equipment)', CHARACTER_SCREEN_WIDTH)

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

def print_messages(messages):
    #Print out a series of messages returned from components
    for success, line, color in messages:
        message(line, color)

def menu(header, options, width):
    #First, make sure the menu has 26 or fewer items (This is due to an alphabetical selection limitation)
    if len(options) > 26:
        raise ValueError('Cannot have a menu with more than 26 options!')

    #implicitly calculate the height of the window, based on the header height (after word wrap) and the number
    # of options
    header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
    if header == '':
        header_height = 0
    height = len(options) + header_height

    #Create an offscreen console that represents the menus window, and a slightly larger one to nest the menu inside of
    #This will create a border effect for the inner menu, strictly asthetic
    outer_window = libtcod.console_new(width + 2, height + 2)
    window = libtcod.console_new(width, height)

    #Print the header to our offscreen console
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_set_default_background(window, libtcod.darker_sepia)
    libtcod.console_clear(window)
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

    #Set up the outer window (which only acts as a border for the inner window, strictly graphical)
    libtcod.console_set_default_background(outer_window, libtcod.brass)
    libtcod.console_clear(outer_window)
    #Blit the actual message window onto the outer window, centered and one off from the borders
    libtcod.console_blit(window, 0, 0, width, height, outer_window, 1, 1)
    #Blit the outer window onto the screen, centered
    libtcod.console_blit(outer_window, 0, 0, width + 2, height + 2, 0, x, y)
    #Now that the console is presented to the player, wait for them to make a choice before doing anything else
    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)

    #Clear the main console, so no artifacts from the menu appear
    libtcod.console_clear(0)

    #Check for fullscreen keys
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #ALT + Enter, toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    #Convert the ASCII code to an index; if it corresponds to a valid menu item, return it
    index = key.c - ord('a')
    if index >= 0 and index < len(options): return index
    return None

def main_menu():
    #Set up the main menu, which is presented to the player when they first load the game
    img = libtcod.image_load('images/menu_background1.png')

    while not libtcod.console_is_window_closed():
        #Show the image at twice its usual resolution of the console
        libtcod.image_blit_2x(img, 0, SCREEN_WIDTH / 6, SCREEN_HEIGHT / 6)

        #Show the games title, and some credits
        libtcod.console_set_default_foreground(0, libtcod.light_yellow)
        libtcod.console_print_ex(0, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 4, libtcod.BKGND_NONE, libtcod.CENTER,
            'DUNGEONCRAWLER')
        libtcod.console_print_ex(0, SCREEN_WIDTH / 2, SCREEN_HEIGHT - 2, libtcod.BKGND_NONE, libtcod.CENTER,
            'By Jeremy Cerise')

        #Show menu options and wait for the players choice
        choice = menu('', ['Play a new game', 'Continue last game', 'Quit'], 24)

        if choice == 0:
            #Start a new game
            #Clear the base conosle, so the menu image and options don't show up under the rest of the UI
            libtcod.console_set_default_background(0, libtcod.brass)
            libtcod.console_clear(0)
            new_game()
            play_game()
        elif choice == 1:
            try:
                libtcod.console_set_default_background(0, libtcod.brass)
                libtcod.console_clear(0)
                load_game()
            except:
                msgbox('\n No saved game to load!\n', 24)
        elif choice == 2:
            #Exit the program
            break;


def msgbox(text, width = 50):
    #Create a menu as a quick and dirty message box
    menu(text, [], width)

def inventory_menu(header):
    #Show a menu with each item of the inventory as an option
    if len(inventory) == 0:
        options = ['Inventory is empty!']
    else:
        options = []
        for item in inventory:
            text = item.name
            #Show additional information in case this item is currently equipped
            if item.equipment and item.equipment.is_equipped:
                text = text + ' (on ' + item.equipment.slot + ')'
            options.append(text)

    index = menu(header, options, INVENTORY_WIDTH)

    #Return the item that was chosen, if any
    if index is None or len(inventory) == 0: return None
    return inventory[index].item

def render_bar(console, x, y, total_width, name, value, maximum, bar_color, back_color):
    #Build and render a status bar (health, mana, experience, etc)
    bar_width = int(float(value) / maximum * total_width)

    #Render the background first
    libtcod.console_set_default_background(console, back_color)
    libtcod.console_rect(console, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    #Now, render the bar on top
    libtcod.console_set_default_background(console, bar_color)
    if bar_width > 0:
        libtcod.console_rect(console, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    #Finally, put the name of the bar, and the actual values on top of everything, for clarity
    libtcod.console_set_default_foreground(console, libtcod.white)
    libtcod.console_print_ex(console, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
        name + ': ' + str(value) + '/' + str(maximum))

def render_all():
    global fov_map, color_dark_wall, color_light_wall
    global color_dark_ground, color_light_ground
    global fov_recompute
    global con
    global dungeon_level

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

    #Blit the map console onto the screen
    libtcod.console_blit(con, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 1, 1)

    #Prepare to render the GUI panel
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    libtcod.console_print_ex(panel, 1, 1, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon level ' + str(dungeon_level))

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
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH - 2, PANEL_HEIGHT - 1, 0, 1, PANEL_Y)

    #Blit the info panel onto the screen
    render_info_panel(info)


def render_info_panel(console):
    libtcod.console_set_default_background(info, libtcod.darker_sepia)
    libtcod.console_set_default_foreground(info, libtcod.light_gray)
    libtcod.console_clear(info)

    #Print out the characters name, class, and level
    libtcod.console_print_ex(info, INFO_WIDTH / 2, 1, libtcod.BKGND_NONE, libtcod.CENTER, 'Jeraman the Green')
    libtcod.console_print_ex(info, INFO_WIDTH / 2, 3, libtcod.BKGND_NONE, libtcod.CENTER, 'Novice Adventurer')
    libtcod.console_print_ex(info, INFO_WIDTH / 2, 5, libtcod.BKGND_NONE, libtcod.CENTER, 'Level: ' + str(player.level))
    libtcod.console_print_ex(info, INFO_WIDTH / 2, 7, libtcod.BKGND_NONE, libtcod.CENTER, '---------------------------')

    #Show the players stats
    render_bar(info, 2, 9, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp,
               libtcod.light_red, libtcod.darker_red)
    render_bar(info, 2, 11, BAR_WIDTH, 'MANA', 30, 30,
               libtcod.light_blue, libtcod.darker_blue)

    libtcod.console_print_ex(info, INFO_WIDTH / 2, 13, libtcod.BKGND_NONE, libtcod.RIGHT, 'Strength: ' +
                                                                                          str(player.fighter.base_strength))
    libtcod.console_print_ex(info, INFO_WIDTH / 2, 15, libtcod.BKGND_NONE, libtcod.RIGHT, 'Defense: ' +
                                                                                          str(player.fighter.base_defence))
    libtcod.console_print_ex(info, INFO_WIDTH / 2, 17, libtcod.BKGND_NONE, libtcod.RIGHT, 'Agility: ' +
                                                                                          str(player.fighter.base_agility))
    libtcod.console_print_ex(info, INFO_WIDTH / 2, 19, libtcod.BKGND_NONE, libtcod.RIGHT, 'Accuracy: ' +
                                                                                          str(player.fighter.base_accuracy))

    libtcod.console_print_ex(info, INFO_WIDTH / 2, 22, libtcod.BKGND_NONE, libtcod.CENTER, 'Damage: ' +
                                                                                           str(player.fighter.base_strength) + ' (+' + str(player.fighter.equipmentDamage) + ')')
    libtcod.console_print_ex(info, INFO_WIDTH / 2, 24, libtcod.BKGND_NONE, libtcod.CENTER, 'Protection: ' +
                                                                                           str(player.fighter.base_protection) + ' (+' + str(player.fighter.equipmentProtection) + ')')

    libtcod.console_print_ex(info, INFO_WIDTH / 2, 26, libtcod.BKGND_NONE, libtcod.CENTER, '---------------------------')
    libtcod.console_print_ex(info, INFO_WIDTH / 2, 28, libtcod.BKGND_NONE, libtcod.CENTER, 'Equipment')

    #Loop through the inventory, and identify all equipped items and their equipment slot
    equipped_items = {}
    for item in inventory:
        text = item.name
        if item.equipment and item.equipment.is_equipped:
            equipped_items[item.equipment.slot] = text

    libtcod.console_print_ex(info, INFO_WIDTH / 14, 30, libtcod.BKGND_NONE, libtcod.LEFT, 'Head:')
    if 'head' in equipped_items:
        libtcod.console_print_ex(info, INFO_WIDTH / 2, 31, libtcod.BKGND_NONE, libtcod.CENTER, equipped_items['head'])
    else:
        libtcod.console_print_ex(info, INFO_WIDTH / 2, 31, libtcod.BKGND_NONE, libtcod.CENTER, 'N/A')

    libtcod.console_print_ex(info, INFO_WIDTH / 5, 33, libtcod.BKGND_NONE, libtcod.CENTER, 'Torso:')
    if 'torso' in equipped_items:
        libtcod.console_print_ex(info, INFO_WIDTH / 2, 34, libtcod.BKGND_NONE, libtcod.CENTER, equipped_items['torso'])
    else:
        libtcod.console_print_ex(info, INFO_WIDTH / 2, 34, libtcod.BKGND_NONE, libtcod.CENTER, 'N/A')

    libtcod.console_print_ex(info, INFO_WIDTH / 12, 36, libtcod.BKGND_NONE, libtcod.LEFT, 'Left hand:')
    if 'left-hand' in equipped_items:
        libtcod.console_print_ex(info, INFO_WIDTH / 2, 37, libtcod.BKGND_NONE, libtcod.CENTER, equipped_items['left-hand'])
    else:
        libtcod.console_print_ex(info, INFO_WIDTH / 2, 37, libtcod.BKGND_NONE, libtcod.CENTER, 'N/A')

    libtcod.console_print_ex(info, INFO_WIDTH / 12, 39, libtcod.BKGND_NONE, libtcod.LEFT, 'Right hand:')
    if 'right-hand' in equipped_items:
        libtcod.console_print_ex(info, INFO_WIDTH / 2, 40, libtcod.BKGND_NONE, libtcod.CENTER, equipped_items['right-hand'])
    else:
        libtcod.console_print_ex(info, INFO_WIDTH / 2, 40, libtcod.BKGND_NONE, libtcod.CENTER, 'N/A')

    libtcod.console_print_ex(info, INFO_WIDTH / 5, 42, libtcod.BKGND_NONE, libtcod.CENTER, 'Gloves:')
    if 'hands' in equipped_items:
        libtcod.console_print_ex(info, INFO_WIDTH / 2, 43, libtcod.BKGND_NONE, libtcod.CENTER, equipped_items['hands'])
    else:
        libtcod.console_print_ex(info, INFO_WIDTH / 2, 43, libtcod.BKGND_NONE, libtcod.CENTER, 'N/A')

    libtcod.console_print_ex(info, INFO_WIDTH / 14, 45, libtcod.BKGND_NONE, libtcod.LEFT, 'Legs:')
    if 'legs' in equipped_items:
        libtcod.console_print_ex(info, INFO_WIDTH / 2, 46, libtcod.BKGND_NONE, libtcod.CENTER, equipped_items['legs'])
    else:
        libtcod.console_print_ex(info, INFO_WIDTH / 2, 46, libtcod.BKGND_NONE, libtcod.CENTER, 'N/A')

    libtcod.console_print_ex(info, INFO_WIDTH / 14, 48, libtcod.BKGND_NONE, libtcod.LEFT, 'Feet:')
    if 'feet' in equipped_items:
        libtcod.console_print_ex(info, INFO_WIDTH / 2, 49, libtcod.BKGND_NONE, libtcod.CENTER, equipped_items['feet'])
    else:
        libtcod.console_print_ex(info, INFO_WIDTH / 2, 49, libtcod.BKGND_NONE, libtcod.CENTER, 'N/A')

    libtcod.console_print_ex(info, INFO_WIDTH / 2, 51, libtcod.BKGND_NONE, libtcod.CENTER, '---------------------------')
    libtcod.console_print_ex(info, INFO_WIDTH / 2, 52, libtcod.BKGND_NONE, libtcod.CENTER, 'Experience')

    level_up_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR

    render_bar(info, 2, 54, BAR_WIDTH, 'XP', player.fighter.xp, level_up_xp,
               libtcod.light_yellow, libtcod.darker_yellow)
    libtcod.console_blit(info, 0, 0, INFO_WIDTH, INFO_HEIGHT, 0, MAP_WIDTH + 2, 1)

def new_game():
    #Initialize all the components needed to start up a new game
    global player, map, objects, game_msgs, game_state, inventory, stairs_down, dungeon_level

    #Set the dungeon level at one. This will be incremented as the player advances
    dungeon_level = 1

    #Create the map object, based on what type of map we need for this floor
    #Choose a map type at random. This is temporary, until I get floors and progression built in
    map_chance = randrange(0, 2)
    if map_chance == 0:
        mapObject = Cavern(MAP_WIDTH, MAP_HEIGHT, MAX_ROOMS, ROOM_MIN_SIZE, ROOM_MAX_SIZE,
            MAX_ROOM_MONSTERS, MAX_ROOM_ITEMS, dungeon_level)
    else:
        mapObject = StandardDungeon(MAP_WIDTH, MAP_HEIGHT, MAX_ROOMS, ROOM_MIN_SIZE, ROOM_MAX_SIZE,
            MAX_ROOM_MONSTERS, MAX_ROOM_ITEMS, dungeon_level)

    #Use the map object to generate the map array, placing all monsters and items in the process
    #This will return the map array, the objects array, and the start coordinates for the player
    (map, objects, player_start_x, player_start_y, stairs_down) = mapObject.setup_map()

    #Initialize the field of view
    initialize_fov()

    #Initialize the players inventory, empty of course. This will be attached to the player object
    inventory = []

    #Create our objects, in this case just a player, then add them to the objects array
    #Create a fighter component for the player. The player does not need an AI
    player_death = getattr(Fighter, 'player_death')
    fighter_component = Fighter(hp=30, attack=2, defence=2, strength=2, protection=0, agility=0, accuracy=0, xp=0,
                                is_player=True, death_function=player_death)
    player = Object(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, '@', 'player', libtcod.white, True,
                    fighter=fighter_component, inventory=inventory)
    player.x = player_start_x
    player.y = player_start_y

    #Set the players level
    player.level = 1

    #Add the player to the objects array, which will be drawn to the screen
    objects.insert(0, player)

    game_state = 'playing'

    #Create an empty list for game messages
    game_msgs = []

    #Add a welcome message
    message('Welcome Stranger! Prepare to perish in the Dungeons of Un-imaginable sorrow!', libtcod.red)

def next_level():
    #Advance the player to the next level in the dungeon
    global dungeon_level, map, objects, player, stairs_down

    message('You head down a winding passage, travelling deeper into the depths of the dungeon...')

    #Keep track of how many levels down the player is
    dungeon_level += 1

    #Create the map object, based on what type of map we need for this floor
    #Choose a map type at random. This is temporary, until I get floors and progression built in
    map_chance = randrange(0, 2)
    if map_chance == 0:
        mapObject = Cavern(MAP_WIDTH, MAP_HEIGHT, MAX_ROOMS, ROOM_MIN_SIZE, ROOM_MAX_SIZE,
            MAX_ROOM_MONSTERS, MAX_ROOM_ITEMS, dungeon_level)
    else:
        mapObject = StandardDungeon(MAP_WIDTH, MAP_HEIGHT, MAX_ROOMS, ROOM_MIN_SIZE, ROOM_MAX_SIZE,
            MAX_ROOM_MONSTERS, MAX_ROOM_ITEMS, dungeon_level)

    #Use the map object to generate the map array, placing all monsters and items in the process
    #This will return the map array, the objects array, and the start coordinates for the player
    (map, objects, player_start_x, player_start_y, stairs_down) = mapObject.setup_map()

    #Since we had to recreate the objects list, we need to re-add the player, with its new starting coordinates
    player.x = player_start_x
    player.y = player_start_y
    objects.insert(0, player)

    #Initialize the field of view
    initialize_fov()

def check_level_up():
    #Check each turn to see if the player has leveled up (xp = level up amount)
    level_up_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
    if player.fighter.xp >= level_up_xp:
        #DING DING DING
        player.level += 1
        player.fighter.xp -= level_up_xp
        message('Your prowess at survival has increased! You reached level ' + str(player.level) + '!', libtcod.yellow)

        choice = None
        while choice is None:
            choice = menu('Level up! Choose a stat to raise:\n',
                          ['Constitution (+20 HP, from ' + str(player.fighter.max_hp) + ')',
                           'Strength (+1 Attack, from ' + str(player.fighter.base_strength) + ')',
                           'Defence (+1 Defense, from ' + str(player.fighter.base_defence) + ')',
                           'Agility (+1 to dodge, from ' + str(player.fighter.base_agility) + ')',
                           'Accuracy (+1 to hit, from ' + str(player.fighter.base_accuracy)],
                          LEVEL_SCREEN_WIDTH)

        if choice == 0:
            player.fighter.max_hp += 20
        elif choice == 1:
            player.fighter.base_strength += 1
        elif choice == 2:
            player.fighter.base_defence += 1
        elif choice == 3:
            player.fighter.base_agility += 1
        elif choice == 4:
            player.fighter.base_accuracy += 1

def save_game():
    global objects, map, inventory, game_msgs, game_state, stairs_down, dungeon_level
    #Create a new, empty shelf to write the game data to, possibly overwriting an old save
    file = shelve.open('savegame', 'c')
    file['map'] = map
    file['objects'] = objects
    file['player_index'] = objects.index(player)
    file['inventory'] = inventory
    file['game_msgs'] = game_msgs
    file['game_state'] = game_state
    file['stairs_down_index'] = objects.index(stairs_down)
    file['dungeon_level'] = dungeon_level
    file.close()

def load_game():
    #Open a previously saved shelve and load the game data
    global objects, map, inventory, game_msgs, game_state, player, stairs_down, dungeon_level
    file = shelve.open('savegame', 'r')
    map = file['map']
    objects = file['objects']
    inventory = file['inventory']
    player = objects[file['player_index']]
    game_msgs = file['game_msgs']
    game_state = file['game_state']
    stairs_down = objects[file['stairs_down_index']]
    dungeon_level = file['dungeon_level']
    file.close()

    initialize_fov()

    play_game()


def initialize_fov():
    #When starting a new game, make sure we completely clear the console of other parts of previous games
    libtcod.console_clear(con)

    #Set up the FOV map
    global fov_recompute, fov_map
    fov_recompute = True

    fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            libtcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)

def play_game():
    #Start up the main game loop so the game can begin playing
    global key, mouse, game_state, examineText

    player_action = None

    mouse = libtcod.Mouse()
    key = libtcod.Key()

    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        #Render the map, and all objects
        render_all()

        libtcod.console_flush()

        check_level_up()

        # Stop character trails by placing a space where the object is. If they don't move, their icon will
        # overwrite this
        for object in objects:
            object.clear(con)

        #Decide what to do. If the escape key is pressed, handle_keys returns true, and we exit the game, otherwise,
        #we process the key press accordingly
        player_action = handle_keys()
        if player_action == 'exit':
            save_game()
            break

        player_alive = player.check_if_dead()
        if not player_alive:
            game_state = 'dead'


        #Let the monsters take their turn
        if game_state == 'playing' and player_action != 'didnt-take-turn' and player_action != 'examining':
            for object in objects:
                if object.ai:
                    messages = object.ai.take_turn(map, fov_map, player, objects)
                    if len(messages) > 0:
                        for success, line, color in messages:
                            message(line, color)
        elif player_action == 'examining':
            #The player is examining an item. We need to clear any other menus (such as the examine menu) so the
            #examine details screen can show
            render_all()
            libtcod.console_flush()
            #Show the examine details screen
            msgbox(examineText, CHARACTER_SCREEN_WIDTH)



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

#Create a panel for the GUI
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

#Create a console for the info panel
info = libtcod.console_new(INFO_WIDTH, INFO_HEIGHT)

#Present the player with the main menu
main_menu()






