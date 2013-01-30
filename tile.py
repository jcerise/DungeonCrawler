class Tile:
    #A tile on the map, and its properties
    #Tiles can block movement, and also sight, or any combination of the two
    #Blocks movement but not sight: a chasm or pit
    #Blocks sight but not movement: A hidden door or panel
    def __init__(self, x, y,  blocked, block_sight = None):
        #Set the X,Y coordinates of this tile, so it can figure out its neighbors
        self.x = x
        self.y = y

        self.blocked = blocked

        #All tiles start out unexplored
        self.explored = False

        #By default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

        #Set a variable to keep track of whether or not this tile has been visited. Can be used for flood fill, or
        #other procedures
        self.visited = False

    def is_wall(self):
        #Check if this tile is a wall (blocks sight and movement)
        if self.blocked and self.block_sight:
            return True

    def is_chasm(self):
        #Check if this tile is a chasm (blocks movement, but not sight
        if self.blocked and  not self.block_sight:
            return True

    def visit(self, visited):
        #Mark this tile as visited or not
        self.visited = visited


