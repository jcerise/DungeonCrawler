import libtcodpy as libtcod


class Equipment:
    #Defines an object that can be equipped, and is not a one-shot item
    def __init__(self, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0):
        self.slot = slot
        self.is_equipped = False
        self.power_bonus = 0
        self.defense_bonus = 0
        self.max_hp_bonus = 0

    def toggle_equip(self):
        #If the equipment is equipped, remove it, otherwise equip it
        if self.is_equipped:
            return self.de_equip()
        else:
            return self.equip()

    def equip(self):
        #Equip the piece of equipment in question
        self.is_equipped = True
        message = ['success', 'Equipped ' + self.owner.name + ' on ' + self.slot + '.', libtcod.light_green]
        return message

    def de_equip(self):
        #Un-equip the equipment in question
        if not self.is_equipped:
            return

        self.is_equipped = False
        message = ['success', 'Un-equipped ' + self.owner.name + ' from ' + self.slot + '.', libtcod.light_yellow]
        return message

