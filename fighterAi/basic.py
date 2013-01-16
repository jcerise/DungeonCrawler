import libtcodpy as libtcod

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