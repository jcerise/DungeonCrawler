import libtcodpy as libtcod
from fighterAi.confused import *
from fighterAi.enraged import *
from magic.spell import *


class Item:
    #Defines an item that can be picked up and used
    def __init__(self, value=0, range=0, use_function=None, targeting=None, type=None):
        #The value of an item determines how much it does of whatever it does (healing, damage, fatigue restore etc)
        self.value = value
        self.range = range
        self.use_function = use_function
        self.targeting = targeting
        #Create a spell component, which will enable this object to cast spells (or trigger abilities)
        self.spellComponent = Spell(None)

        #We need to keep track of a type, as equipment works differently, and we need to be able to handle it as such
        self.type = type

    def pick_up(self, inventory, objects):
        #Check if the players inventory is full or not
        if len(inventory) >= 26:
            message = [['success', 'Your inventory is full, and you cannot pick up ' + self.owner.name + '.', libtcod.yellow]]
        else:
            #Add the item to the players inventory, and remove it from the dungeon
            inventory.append(self.owner)
            objects.remove(self.owner)
            message = [['success', "You picked up a " + self.owner.name + '!', libtcod.green]]

        return message

    def use(self, inventory, object, objects, fov_map, x=None, y=None):
        #We need to handle an item that is a piece of equipment. Rather than using equipment, it gets equipped, so
        #check here and do that if necessary
        if self.owner.equipment:
            messages = self.owner.equipment.toggle_equip()
            return messages

        #Call the use_function defined on object creation
        if self.use_function is None:
            #No usage defined for this item, it cannot be used
            message = [['The ' + self.owner.name + ' cannot be used at this time.', libtcod.white]]

            return message
        else:
            #Fire up the spell component, and trigger the spell specified on the object
            messages = self.spellComponent.cast_spell(self.use_function, self.value, self.range, object, objects,
                                                        fov_map, x, y)
            if messages[0][0] != 'cancelled':
                #Destroy the object, removing it from the players inventory
                inventory.remove(self.owner)

        return messages

    def determine_targeting(self):
        return self.targeting