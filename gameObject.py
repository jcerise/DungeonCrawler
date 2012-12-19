import libtcodpy as libtcod

class Object:
    #Represents a generic object within the game; A chair, a player, an orc, stairs
    #This object is always represented by a character on the screen
    def __init__(self, con,  x, y, char, color):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.con = con

    def move(self, dx, dy):
        #Update the position of this object
        self.x += dx
        self.y += dy

    def draw(self):
        #Draw the character that represents this object
        libtcod.console_set_default_foreground(self.con, self.color)
        libtcod.console_put_char(self.con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def clear(self):
        #Erase the character that represents this object
        libtcod.console_put_char(self.con, self.x, self.y, ' ', libtcod.BKGND_NONE)

