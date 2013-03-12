import libtcodpy as libtcod
from magic.spell import *


class Item:
    #Defines an item that can be picked up and used
    def __init__(self, value=0, range=0, use_function=None, targeting=None, type=None, description='Test'):
        #The value of an item determines how much it does of whatever it does (healing, damage, fatigue restore etc)
        self.value = value
        self.range = range
        self.use_function = use_function
        self.targeting = targeting
        #Create a spell component, which will enable this object to cast spells (or trigger abilities)
        self.spellComponent = Spell(None)

        #We need to keep track of a type, as equipment works differently, and we need to be able to handle it as such
        self.type = type
        self.description = description

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
            #Set up the messages array
            messages = []

            #Check for equipment equipped in the same slot. If present, un-equip it
            if not self.owner.equipment.is_equipped:
                old_equipment = self.get_equipped_in_slot(inventory, self.owner.equipment.slot)
                if old_equipment is not None:
                    messages.append(old_equipment.de_equip())

            #Equip the new
            messages.append(self.owner.equipment.toggle_equip())
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

    def drop(self, objects, inventory, player):
        #'Drop' the item by adding it back to the map, and removing it from the players inventory
        messages = []
        #if the item is equipment, un-equip it first
        if self.owner.equipment and self.owner.equipment.is_equipped:
            messages.append(self.owner.equipment.de_equip())

        objects.append(self.owner)
        inventory.remove(self.owner)
        self.owner.x = player.x
        self.owner.y = player.y
        messages.append(['success', 'You dropped ' + self.owner.name + '.', libtcod.yellow])

        return messages


    def get_equipped_in_slot(self, inventory, slot):
        for obj in inventory:
            if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
                return obj.equipment
        return None

    def determine_targeting(self):
        return self.targeting