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
