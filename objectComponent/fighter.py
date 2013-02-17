import libtcodpy as libtcod
import math

class Fighter:
    #A component that forms the basis for anything in the game that can fight, such as a monster, the player,
    #or an NPC.
    #Each action method (take_damage, attack, etc, returns a list of messages that will be printed to the console,
    #so the player knows whats going on. Each message has a color associated with it
    def __init__(self, hp, defense, power, xp, is_player = False, death_function = None):
        self.hp = hp
        self.max_hp = hp
        self.defense = defense
        self.power = power
        self.xp = xp
        self.death_function = death_function
        self.is_player = is_player

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
        damage = self.power - target.fighter.defense

        if damage > 0:
            #Make the target take some damage
            #Create a list of messages to return to the console, so the player knows whats going on
            #This needs to be an list, as the potential death message needs to be on its own line
            message = [['success', self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' damage!',
                        libtcod.white]]

            #If the fighter has not died, this will return None, otherwise it returns the death message
            death_string = target.fighter.take_damage(damage, self)
            if death_string is not None:
                message.append(death_string)
                #Return the messages array to print to the console
            return message
        else:
            #Create a message array to return to the console
            return [['success', self.owner.name.capitalize() + ' attacks ' + target.name + ', but it has no effect!',
                     libtcod.white]]

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