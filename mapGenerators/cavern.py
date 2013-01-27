from random import randrange
from abstractMapGenerator import *
from tile import *

class Cavern(AbstractMapGenerator):

    #TODO Implement place_objects for this map type. Probably will just be random placement, as there are no rooms

    def __init__(self, width, height, max_rooms, min_room_size, max_room_size, max_monsters, max_items):
        self.width = width
        self.height = height

        #Create lists of items and monsters based on the current dungeon level
        #These are added into the objects array
        (self.monsters, self.monster_appearance_chances) = self.setup_monsters()
        (self.items, self.item_appearance_chances) = self.setup_items()

        #First, fill the whole map with floor tiles
        self.map = [[Tile(False)
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

        #TODO Calculate player start coordinates
        return (self.map, self.objects, self.player_start_x, self.player_start_y)



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
