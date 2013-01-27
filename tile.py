class Tile:
    #A tile on the map, and its properties
    #Tiles can block movement, and also sight, or any combination of the two
    #Blocks movement but not sight: a chasm or pit
    #Blocks sight but not movement: A hidden door or panel
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked

        #All tiles start out unexplored
        self.explored = False

        #By default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

    def is_wall(self):
        #Check if this tile is a wall (blocks sight and movement)
        if self.blocked and self.block_sight:
            return True

    def is_chasm(self):
        #Check if this tile is a chasm (blocks movement, but not sight
        if self.blocked and  not self.block_sight:
            return True


