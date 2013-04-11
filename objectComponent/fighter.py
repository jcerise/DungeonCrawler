import libtcodpy as libtcod
from combatResolver import CombatResolver


class Fighter:
    #A component that forms the basis for anything in the game that can fight, such as a monster, the player,
    #or an NPC.
    #Each action method (take_damage, attack, etc, returns a list of messages that will be printed to the console,
    #so the player knows whats going on. Each message has a color associated with it
    def __init__(self, hp, attack, defence, strength, protection, agility, accuracy, xp, is_player = False, death_function = None):
        self.hp = hp
        self.max_hp = hp
        #Base chance to avoid attack. This is improved by agility
        self.base_defence = defence
        #Base chance to hit, this is improved by accuracy
        self.base_attack = attack
        #Determines damage dealt
        self.base_strength = strength
        #Determines damage reduction
        self.base_protection = protection
        #Determines chance of hitting
        self.base_accuracy = accuracy
        #Determines chance of dodging attacks
        self.base_agility = agility
        #TODO: Add willpower and intelligence. Intelligence will modify casting results, willpower will determine mana
        self.xp = xp
        self.death_function = death_function
        self.is_player = is_player

        self.combatResolver = CombatResolver(6)

    @property
    def damage(self):
        #Calculate how much damage this fighter deals, based on equipped weapons and base strength
        bonus = sum(int(equipment.value) for equipment in self.get_all_equipped_weapons(self.is_player))
        return self.base_strength + bonus

    @property
    def equipmentDamage(self):
        return sum(int(equipment.value) for equipment in self.get_all_equipped_weapons(self.is_player))

    @property
    def equipmentProtection(self):
        return sum(int(equipment.value) for equipment in self.get_all_equipped_armor(self.is_player))

    @property
    def protection(self):
        #Calculate how much protection this fighter has, based on equipped armors and base protection
        bonus = sum(int(equipment.value) for equipment in self.get_all_equipped_armor(self.is_player))
        return self.base_protection + bonus

    def __getstate__(self):
        #We need to remove the death function call, as it creates an instance method exception when pickling
        result = self.__dict__.copy()
        del result['death_function']
        return result

    def __setstate__(self, dict):
        #We need to re-add the death function upon loading from the pickle, this is easy as it can only be one of two
        self.__dict__ = dict
        if self.is_player:
            self.__dict__['death_function'] = getattr(Fighter, 'player_death')
        else:
            self.__dict__['death_function'] = getattr(Fighter, 'monster_death')

    def get_all_equipped_weapons(self, is_player):
        #Get every item that the object has equipped and return them as a list
        #Currently, this only applies to the player, but in the future monsters may have inventories
        if is_player:
            equipped_list = []
            #Check through every item in the inventory
            for item in self.owner.inventory:
                #If its equipment and equipped, add it to the returned list
                if item.equipment and item.equipment.is_equipped and item.equipment.use == 'attack':
                    equipped_list.append(item.equipment)
            return equipped_list
        else:
            #Monsters have no equipment, so just return an empty list, for now
            return []

    def get_all_equipped_armor(self, is_player):
        #Get every item that the object has equipped and return them as a list
        #Currently, this only applies to the player, but in the future monsters may have inventories
        if is_player:
            equipped_list = []
            #Check through every item in the inventory
            for item in self.owner.inventory:
                #If its equipment and equipped, add it to the returned list
                if item.equipment and item.equipment.is_equipped and item.equipment.use == 'defense':
                    equipped_list.append(item.equipment)
            return equipped_list
        else:
            #Monsters have no equipment, so just return an empty list, for now
            return []


    def take_damage(self, damage, source):
        #apply damage if possible
        if damage > 0:
            self.hp -= damage

        #If the player has died, call the appropriate (previously defined at object creation) death function
        if self.hp <= 0:
            function = self.death_function
            if function is not None:

                #Give the player some XP for killing this nasty beastie (if it is a nasty beastie, and not the player)
                if not self.is_player:
                    source.xp += self.xp

                #Return the messages printed upon execution of this event
                return function(self, self.owner)

    def attack(self, target):
        #Simple damage calculation - power minus target defense
        messages, damageDealt = self.combatResolver.initiateCombat(self, target)

        if damageDealt > 0:
            #Make the target take some damage

            #If the fighter has not died, this will return None, otherwise it returns the death message
            death_string = target.fighter.take_damage(damageDealt, self)
            if death_string is not None:
                messages.append(death_string)

        #Return the messages array to print to the console
        return messages

    def heal(self, amount):
        #Heal by the given amount, without going over max_hp
        message = []
        if self.hp == self.max_hp and amount >= 0:
            #Fighters health is already full, cannot heal further
            message = [['cancelled', 'You are already at full health!', libtcod.red]]
            return message

        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

        if amount > 0:
            message = [['success', 'Your wounds start to feel better!', libtcod.light_violet]]
        elif amount < 0:
            message = [['success', 'Yuck! That item was spoiled! You dont feel very good...', libtcod.sea]]
        else:
            message = [['success', 'You dont notice any effect...', libtcod.white]]

        #Certain items, cursed or otherwise, can do negative healing damage. Make sure this is handled properly
        if self.hp <= 0:
            function = self.death_function
            if function is not None:
                #Return the messages printed upon execution of this event
                message += [function(self, self.owner)]

        return message

    def player_death(self, player):
        #The player has died, replace him with a corpse and end the game
        player.set_alive_or_dead(False)

        #Change the players icon into a corpse
        player.char = '%'
        player.color = libtcod.dark_red
        return ['success', 'You have died a terrible death at the hands of the denizens of this foul place...', libtcod.dark_red]

    def monster_death(self, monster):
        #Change the monster into a corpse. It cannot attack, doesnt block, and cant move
        monster.char = '%'
        monster.color = libtcod.dark_red
        monster.blocks = False
        monster.ai = None
        message = ['success', 'The ' + monster.name.capitalize() + ' has been slain! You have gained ' +
            str(monster.fighter.xp) + ' experience points.', libtcod.orange]
        monster.name = 'Remains of ' + monster.name
        monster.fighter = None
        return message