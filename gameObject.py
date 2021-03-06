import libtcodpy as libtcod
from objectComponent.item import Item
import math


class Object:
    #Represents a generic object within the game; A chair, a player, an orc, stairs
    #This object is always represented by a character on the screen
    def __init__(self, x, y, char, name, color, blocks=False, fighter=None, ai=None, item=None,
                 equipment=None, inventory=None, description=None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.alive = True

        #Set the inventory for this object. For the time being, only the player has an inventory, but might add one
        #for monsters in the future
        self.inventory = inventory

        self.fighter = fighter
        if self.fighter:
            self.fighter.owner = self

        self.ai = ai
        if self.ai:
            self.ai.owner = self

        self.item = item
        if self.item:
            self.item.owner = self

        self.equipment = equipment
        if self.equipment:
            self.equipment.owner = self
            #equipment is technically an item, so we need an item component for it to work properly
            #We also need to to set the type of the item to equipment
            self.item = Item(type='equipment', description=description)
            self.item.owner = self

    def move(self, gameMap, dx, dy, blocked):
        #Update the position of this object
        if not blocked:
            self.x += dx
            self.y += dy

    def is_blocked(self, x, y, map, objects):
        #Test the map tile at the coordinates to see if it is blocked or not
        if map[x][y].blocked:
            return True

        #Then, check through all objects and see if any of them are blocking
        for object in objects:
            if object.blocks and object.x == x and object.y == y:
                return True

        #There is no object or tile blocking this position
        return False

    def move_towards(self, gameMap, objects, target_x, target_y):
        #Create a vector from this object to the target, and get the distance
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        #Normalize it to length 1, maintaining the direction, then
        #round it and convert to an integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        blocked = self.is_blocked(self.x + dx, self.y + dy, gameMap, objects)
        self.move(gameMap, dx, dy, blocked)

    def distance(self, x, y):
        #Return the distance to some coordinates
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def distance_to(self, other):
        #Return the distance to another object
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy **2)

    def closest_fighter(self, objects):
        #Return the closest object with a fighter component to this object
        closest_distance = 1000
        closest_object = None
        for object in objects:
            #Search through all objects, ignoring ourself
            if object.fighter and object != self:
                distance = self.distance_to(object)
                if distance < closest_distance:
                    closest_distance = distance
                    closest_object = object
        return closest_object

    def draw(self, fov_map, con):
        #Draw the character that represents this object, if its in the players field of view
        if libtcod.map_is_in_fov(fov_map, self.x, self.y):
            libtcod.console_set_default_foreground(con, self.color)
            libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def clear(self, con):
        #Erase the character that represents this object
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

    def set_alive_or_dead(self, alive_or_dead):
        self.alive = alive_or_dead

    def check_if_dead(self):
        #Return false if the player has died
        return self.alive




