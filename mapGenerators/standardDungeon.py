from tile import *
import libtcodpy as libtcod
from rect import Rect
from abstractMapGenerator import *
from gameObject import *

#Objerct components
from objectComponent.fighter import *
from objectComponent.item import *

#Object AIs
from fighterAi.basic import *

class StandardDungeon(AbstractMapGenerator):

    def __init__(self, width, height, max_rooms, min_room_size, max_room_size, max_monsters, max_items):
        self.width = width
        self.height = height
        self.max_rooms = max_rooms
        self.min_room_size = min_room_size
        self.max_room_size = max_room_size
        self.max_monsters = max_monsters
        self.max_items = max_items

        self.objects = []

        #Create lists of items and monsters based on the current dungeon level
        #These are added into the objects array
        (self.monsters, self.monster_appearance_chances) = self.setup_monsters()
        (self.items, self.item_appearance_chances) = self.setup_items()

        #Fill map with blocked tiles, this will allow us to 'carve' rooms for the player
        #to explore
        self.map = [[Tile(True)
                        for y in range(self.height) ]
                            for x in range(self.width) ]

    def setup_map(self):
        #Create the map, add objects and monsters, and save it all for later use
        rooms = []
        num_rooms = 0

        for r in range(self.max_rooms):
            #Generate a random width and height for each room
            w = libtcod.random_get_int(0, self.min_room_size, self.max_room_size)
            h = libtcod.random_get_int(0, self.min_room_size, self.max_room_size)

            #Generate a random map position, inside the bounds of the map
            x = libtcod.random_get_int(0, 0, self.width - w - 1)
            y = libtcod.random_get_int(0, 0, self.height - h -1)

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
                self.create_room(new_room)

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
                    self.place_objects(new_room)

                    #Get the center coordinates for the previous room
                    (prev_x, prev_y) = rooms[num_rooms - 1].center()

                    #Flip a coin to see if we move horizontally, or vertically first
                    if libtcod.random_get_int(0, 0, 1) == 1:
                        #Tunnel horizontally first, then vertically
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        #Tunnel vertically first, then horizontally
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                #Finally, append the newly added room to the rooms list
                rooms.append(new_room)
                num_rooms += 1

        return (self.map, self.objects, player_start_x, player_start_y)

    def place_objects(self, room):
        #Place Monsters in each room, randomly of course
        num_monsters = libtcod.random_get_int(0, 0, self.max_monsters)

        for i in range(num_monsters):
            x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
            y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

            if not self.is_blocked(self.map, self.objects, x, y):
                #Choose a monster to spawn from the list of applicable monsters
                spawn = self.random_choice_index(self.monster_appearance_chances)

                #Choose the monster based on the spawn chance
                monster = self.monsters[spawn]

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
                self.objects.append(monster)

        #Place items in each room, randomly as well
        num_items = libtcod.random_get_int(0, 0, self.max_items)

        for i in range(num_items):
            #Create x num_items number of items in this room
            x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
            y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

            if not self.is_blocked(self.map, self.objects, x, y):
                #Choose an item to create from the list of applicable items
                item_choice = self.random_choice_index(self.item_appearance_chances)

                #Choose the item based on the spawn chance
                item = self.items[item_choice]

                #Find the use function for this object, and apply it to the item
                item_use_function = item[2]

                #Create an object and item component from the loaded values
                item_component = Item(value = int(item[3]), range = int(item[4]), use_function = item_use_function,
                    targeting = item[10])
                item = Object(x, y, item[5], item[0], color = libtcod.Color(int(item[6]), int(item[7]), int(item[8])),
                    item = item_component)
                self.objects.append(item)

    def create_room(self, room):
        #go through each tile in the rectangle and make them passable
        #range() will exclude the last value in the range, which is perfect,
        #as we want a one block thick wall surrounding the room
        for x in range(room.x1, room.x2):
            for y in range(room.y1, room.y2):
                self.map[x][y].blocked = False
                self. map[x][y].block_sight = False

    def create_h_tunnel(self, x1, x2, y):
        #carve a horizontal tunnel from x1 to x2
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.map[x][y].blocked = False
            self.map[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        #carve a vertical tunnel from y1 to y2
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.map[x][y].blocked = False
            self.map[x][y].block_sight = False

