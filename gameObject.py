import libtcodpy as libtcod
import math

class Object:
    #Represents a generic object within the game; A chair, a player, an orc, stairs
    #This object is always represented by a character on the screen
    def __init__(self, x, y, char, name, color, blocks = False, fighter = None, ai = None, item = None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.alive = True

        self.fighter = fighter
        if self.fighter:
            self.fighter.owner = self

        self.ai = ai
        if self.ai:
            self.ai.owner = self

        self.item = item
        if self.item:
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

    def distance_to(self, other):
        #Return the distance to another object
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy **2)

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

class Fighter:
    #A component that forms the basis for anything in the game that can fight, such as a monster, the player,
    #or an NPC.
    #Each action method (take_damage, attack, etc, returns a list of messages that will be printed to the console,
    #so the player knows whats going on. Each message has a color associated with it
    def __init__(self, hp, defense, power, death_function = None):
        self.hp = hp
        self.max_hp = hp
        self.defense = defense
        self.power = power
        self.death_function = death_function

    def take_damage(self, damage):
        #apply damage if possible
        if damage > 0:
            self.hp -= damage

        #If the player has died, call the appropriate (previously defined at object creation) death function
        if self.hp <= 0:
            function = self.death_function
            if function is not None:
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
            death_string = target.fighter.take_damage(damage)
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
        monster.fighter = None
        monster.ai = None
        message = ['success', 'You have slain the ' + monster.name.capitalize(), libtcod.orange]
        monster.name = 'Remains of ' + monster.name
        return message


class BasicMonster:
    #Defines a basic monster, extends the Fighter component
    #Returns a list of messages to be printed to the console, outlining this monsters turn
    def take_turn(self, gameMap, fovMap, player, objects):
        messages = []
        #If you can see the monster, the monster can see you
        monster = self.owner
        if libtcod.map_is_in_fov(fovMap, monster.x, monster.y):
            #Move towards the player
            if monster.distance_to(player) >= 2:
                monster.move_towards(gameMap, objects, player.x, player.y)
            elif player.fighter.hp > 0:
                #The monster is close enough, attempt an attack on the player
                messages.extend(monster.fighter.attack(player))
        return messages
class ConfusedMonster:
    #AI for a confused monster
    def __init__(self, old_ai, confuse_num_turns):
        self.old_ai = old_ai
        self.confuse_num_turns = confuse_num_turns

    def take_turn(self, gameMap, fovMap, player, objects):
        if self.confuse_num_turns > 0:
            x = libtcod.random_get_int(0, -1, 1)
            y = libtcod.random_get_int(0, -1, 1)
            blocked = self.owner.is_blocked(self.owner.x + x, self.owner.y + y, gameMap, objects)
            self.owner.move(gameMap, x, y, blocked)
            self.confuse_num_turns -= 1
            message = [['success', 'The ' + self.owner.name + ' wanders around, obviously confused about whats going on',
                       libtcod.light_orange]]
        else:
            self.owner.ai =self.old_ai
            message = [['success', 'The ' + self.owner.name + ' is no longer confused!', libtcod.light_red]]

        return message

class Item:
    #Defines an item that can be picked up and used
    def __init__(self, value = 0, range = 0, use_function = None):
        #The value of an item determines how much it does of whatever it does (healing, damage, fatigue restore etc)
        self.value = value
        self.range = range
        self.use_function = use_function

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

    def use(self, inventory, object, objects, fov_map):
        #Call the use_function defined on object creation
        if self.use_function is None:
            #No usage defined for this item, it cannot be used
            message = [['The ' + self.owner.name + ' cannot be used at this time.', libtcod.white]]
        else:
            messages = self.use_function(self, self.value, self.range, object, objects, fov_map)
            if messages[0][0] != 'cancelled':
                #Destroy the object, removing it from the players inventory
                inventory.remove(self.owner)

        return messages

    def cast_heal(self, amount, range, caster, objects, fov_map):
        #Heal the object (player, monster, whatever)
        message = caster.fighter.heal(amount)
        return message

    def cast_lightning(self, damage, range, caster, objects, fov_map):
        #Cast a lightning bolt at the nearest enemy (player cannot target this spell)
        enemy = self.closest_enemy(range, caster, objects, fov_map)
        if enemy is None:
            #No enemy has been found in range
            message = [['cancelled', 'No enemy is close enough for the lightning to reach...', libtcod.red]]
            return message

        #There is a target in range, zap it to a crispy shell of its previous self
        message = [['success', 'A loud clap of thunder booms out, as a bolt of white hot lightning issues forth!' +
                              'It strikes the ' + enemy.name + ' with a crack, dealing ' + str(damage) + ' damage!',
                              libtcod.light_blue]]
        message += [enemy.fighter.take_damage(damage)]
        return message

    def cast_confuse(self, damage, range, caster, objects, fov_map):
        enemy = self.closest_enemy(range, caster, objects, fov_map)
        if enemy is None:
            message = [['cancelled', 'No enemy is close enough to confuse...', libtcod.red]]
            return message
        #Replace the enemies AI with a confused one. This will revert after a few turns
        old_ai = enemy.ai
        enemy.ai = ConfusedMonster(old_ai, damage)
        enemy.ai.owner = enemy
        message = [['success', 'There is a faint hiss as the spell triggers. The eyes of the ' + enemy.name +
                               ' suddenly look vacant, as if it has forgotten its purpose. It begins to wander' +
                               'aimlessly around...', libtcod.light_green]]
        return message

    def closest_enemy(self, range, caster, objects, fov_map):
        #Find the closest enemy, up to (range) tiles away, and within the players FOV
        closest_enemy = None
        #Start with slightly more than maximum range
        closest_dist = range + 1

        for object in objects:
            if object.fighter and not object == caster and libtcod.map_is_in_fov(fov_map, caster.x, caster.y):
                #Calculate distance between this object and the caster
                dist = caster.distance_to(object)
                if dist < closest_dist:
                    closest_enemy = object
                    closest_dist = dist
        return closest_enemy





