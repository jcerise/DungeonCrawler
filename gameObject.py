import libtcodpy as libtcod

class Object:
    #Represents a generic object within the game; A chair, a player, an orc, stairs
    #This object is always represented by a character on the screen
    def __init__(self, x, y, char, name, color, blocks = False):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks

    def move(self, gameMap, dx, dy, blocked):
        #Update the position of this object
        if not blocked:
            self.x += dx
            self.y += dy

    def draw(self, fov_map, con):
        #Draw the character that represents this object, if its in the players field of view
        if libtcod.map_is_in_fov(fov_map, self.x, self.y):
            libtcod.console_set_default_foreground(con, self.color)
            libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def clear(self, con):
        #Erase the character that represents this object
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)
