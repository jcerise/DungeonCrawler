from random import randrange
from abstractMapGenerator import *
from tile import *
from objectComponent.fighter import *
from objectComponent.item import *
from gameObject import *
from fighterAi.basic import *

class Cavern(AbstractMapGenerator):

    #TODO Implement place_objects for this map type. Probably will just be random placement, as there are no rooms

    def __init__(self, width, height, max_rooms, min_room_size, max_room_size, max_monsters, max_items, level):
        self.width = width
        self.height = height

        self.objects = []

        #Create lists of items and monsters based on the current dungeon level
        #These are added into the objects array
        (self.monsters, self.monster_appearance_chances) = self.setup_monsters(level)
        (self.items, self.item_appearance_chances) = self.setup_items(level)

        #First, fill the whole map with floor tiles
        self.map = [[Tile(x, y, False)
                for y in range(self.height) ]
               for x in range(self.width) ]


    def setup_map(self):
        #Generate a cavern type map using Cellular Automata (similar to game of life). The map is usually free of disjoint
        #segments (disconnected areas), but not always, and does a good job of making sure there are no large, open area

        #Next, make roughly 40% of the map wall tiles
        for x in range(0, len(self.map)):
            for y in range(0, len(self.map[x])):
                if randrange(0, 100) < 42:
                    self.map[x][y].blocked = True
                    self.map[x][y].block_sight = True

        #Now, we make several passes over the map, altering the wall tiles on each pass
        #If a tile has 5 or more neighbors (one tile away) that are walls, then that tile becomes a wall. If it has two
        #or fewer walls near (two or fewer tiles away) it, it also becomes a wall (This gets rid of large empty spaces).
        #If neither of these are true, the tile becomes a floor. This is repeated several times to smooth out the "noise"
        for _ in range(5):
            for x in range(0, len(self.map)):
                for y in range(0, len(self.map[x])):
                    wall_count_one_away = self.count_walls_n_steps_away(self.map, 1, x, y)
                    wall_count_two_away = self.count_walls_n_steps_away(self.map, 2, x, y)
                    tile = self.map[x][y]
                    if wall_count_one_away >= 5 or wall_count_two_away <= 2:
                        #This tile becomes a wall
                        tile.blocked = True
                        tile.block_sight = True
                    else:
                        tile.blocked = False
                        tile.block_sight = False

        #Finally, we make a few more passes to smooth out caverns a little more, and get rid of isolated, single tile walls
        for _ in range(4):
            for x in range(0, len(self.map)):
                for y in range(0, len(self.map[x])):
                    wall_count_one_away = self.count_walls_n_steps_away(self.map, 1, x, y)
                    tile = self.map[x][y]
                    if wall_count_one_away >= 5:
                        #This tile becomes a wall
                        tile.blocked = True
                        tile.block_sight = True
                    else:
                        tile.blocked = False
                        tile.block_sight = False

        #Now that we have the cavern generated, we need to remove any small, unattached caverns, as these will make it
        #more difficult to generate a starting position for the player

        #First, create a variable to store all the different sub-caverns in our larger cavern system. These are floor
        #areas not connected to any other cavern (separated by wall segments)
        caverns = []

        #Before we do anything else, we need to seal up the edges of the map, so the player cannot wander out into
        #nothingness. We do this by walking around the edges of the map and making them all wall
        for x in range(self.width):
            for y in range(self.height):
                if x == 0 or y == 0 or x == self.width - 1 or y == self.height - 1:
                    self.map[x][y].block_sight = True
                    self.map[x][y].blocked = True

        #Now, begin looping through the map, looking for individual caverns
        for x in range(self.width):
            for y in range(self.height):
                #Grab the tile at the current coordinates
                tile = self.map[x][y]

                #Set up some empty arrays to hold our current cavern
                cavern = []
                total_cavern_area = []

                #Ensure this is a non-wall tile that has not already been visited
                if not tile.visited and not tile.is_wall():
                    #If it meets the criteria, add it to the new cavern
                    cavern.append(tile)

                    #Loop through all potentially valid cavern tiles for this cavern, and see if they are actually part
                    #of the cavern or not. If they are, add them to the total, and grab all four of their neighbors
                    while len(cavern) > 0:
                        #Get the last item in the candidate list
                        node = cavern.pop()
                        if not node.visited and not node.is_wall():
                            #Mark the tile as visited
                            node.visit(True)
                            total_cavern_area.append(node)

                            #Append the tile to the west to the cavern array
                            if node.x - 1 > 0 and not self.map[node.x - 1][node.y].is_wall():
                                cavern.append(self.map[node.x - 1][node.y])
                            #Append the tile to the east to the cavern array
                            if node.x + 1 < len(self.map) and not self.map[node.x + 1][node.y].is_wall():
                                cavern.append(self.map[node.x + 1][node.y])
                            #Append the tile to the north to the cavern array
                            if node.y - 1 > 0 and not self.map[node.x][node.y - 1].is_wall():
                                cavern.append(self.map[node.x][node.y - 1])
                            #Append the tile to the south to the cavern array
                            if node.y + 1 < len(self.map[x]) and not self.map[node.x][node.y + 1].is_wall():
                                cavern.append(self.map[node.x][node.y + 1])

                    #Cavern detection and construction completed, so append this cavern to the list of all caverns
                    caverns.append(total_cavern_area)
                else:
                    #This was not a valid cavern candidate, so mark it as visited so we dont bother with it again
                    tile.visit(True)

        #Sort the cavern arrays so the largest cavern (the main cavern) is the last item, then remove it from the list
        #All the remaining caverns will be filled in
        sorted_caverns = sorted(caverns, lambda x,y: 1 if len(x)>len(y) else -1 if len(x)<len(y) else 0)
        main_cave = sorted_caverns.pop()

        #Fill in each of the remaining caverns, as they are not part of the main cave. This will ensure that every
        #part of the cavern system is accessible to the player
        for cave in sorted_caverns:
            for tile in cave:
                tile.blocked = True
                tile.block_sight = True

        #Finally, randomly place the player somewhere in the main cavern. we know it will be on a free, non-wall tile
        #since the cavern array only contains non-wall tiles
        random_tile = main_cave[randrange(0, len(main_cave))]
        (self.player_start_x, self.player_start_y) = (random_tile.x, random_tile.y)

        #Populate the cavern with some objects
        self.place_objects(main_cave)

        return (self.map, self.objects, self.player_start_x, self.player_start_y, self.stairs_down)

    def place_objects(self, cave):
        #Loop through all tiles in our main cavern, and based on a small chance, randomly place either an item or a
        #monster on the tile
        stairs_placed = False
        for tile in cave:
            chance = randrange(0, 100)
            #Roughly a 2 percent chance of an object (monster or item) spawning on this tile
            if chance <= 1:
                if not stairs_placed:
                    #Create the stairs in the last room to be created
                    self.stairs_down = Object(tile.x, tile.y, '>', 'stairs down', libtcod.white)
                    self.objects.append(self.stairs_down)
                    stairs_placed = True
                else:
                    #Place an object on this tile
                    object_type = randrange(0, 100)
                    if object_type <= 30:
                        #place an item
                        if not self.is_blocked(self.map, self.objects, tile.x, tile.y):
                            #Choose an item to create from the list of applicable items
                            item_choice = self.random_choice_index(self.item_appearance_chances)

                            #Choose the item based on the spawn chance
                            item = self.items[item_choice]

                            #Find the use function for this object, and apply it to the item
                            item_use_function = item[2]

                            #Create an object and item component from the loaded values
                            item_component = Item(value = int(item[3]), range = int(item[4]), use_function = item_use_function,
                                targeting = item[10])
                            item = Object(tile.x, tile.y, item[5], item[0], color = libtcod.Color(int(item[6]), int(item[7]), int(item[8])),
                                item = item_component)
                            self.objects.append(item)
                    else:
                        #Place a monster
                        if not self.is_blocked(self.map, self.objects, tile.x, tile.y):
                            #Choose a monster to spawn from the list of applicable monsters
                            spawn = self.random_choice_index(self.monster_appearance_chances)

                            #Choose the monster based on the spawn chance
                            monster = self.monsters[spawn]

                            #Create a death function for the monster
                            monster_death = getattr(Fighter, 'monster_death')

                            #Create a component for the monster based on the monster type
                            if monster[1] == 'fighter':
                                fighter_component = Fighter(hp = int(monster[3]), defense = int(monster[4]), power = int(monster[5]),
                                    xp = int(monster[11]), death_function = monster_death)

                            #Create an AI component for the monster based on its AI type
                            if monster[2] == 'basic':
                                ai_component = BasicMonster()

                            #Finally, create the monster
                            monster = Object(tile.x, tile.y, char = monster[6], name = monster[0], color = libtcod.Color(int(monster[7]),
                                int(monster[8]), int(monster[9])), blocks = True, fighter = fighter_component,  ai = ai_component)

                            #Add the monster to the objects array
                            self.objects.append(monster)


    def count_walls_n_steps_away(self, map, n, x, y):
        #count the number of wall tiles that are within n tiles of the source tile at (x, y)
        wall_count = 0

        for r in (-n, 0, n):
            for c in (-n, 0, n):
                try:
                    if map[x + r][y + c].is_wall():
                        wall_count += 1
                except IndexError:
                    #Check to see if the coordinates are off the map. Off map is considered wall
                    wall_count += 1

        return wall_count
