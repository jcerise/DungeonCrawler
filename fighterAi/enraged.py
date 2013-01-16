import libtcodpy as libtcod

class EnragedMonster:
    #AI for an enraged object. This object will attack any fighter in sight, not just the player
    def __init__(self, old_ai, enraged_num_turns):
        self.old_ai = old_ai
        self.enraged_num_turns = enraged_num_turns

    def take_turn(self, gameMap, fovMap, player, objects):
        messages = []

        if self.enraged_num_turns > 0:
            aiObject = self.owner
            #Find the closest fighter object, this is the target. This can be a monster or the player
            target = self.owner.closest_fighter(objects);
            if aiObject.distance_to(target) >= 2:
                #Not close enough to target, move closer
                aiObject.move_towards(gameMap, objects, target.x, target.y)
                messages += [['success', 'The ' + self.owner.name + ' charges the ' + target.name + '!',
                                    libtcod.light_orange]]
            elif target.fighter.hp > 0:
                #The target is close enough, attempt an attack on the target
                messages += [['success', 'The ' + self.owner.name + ' attacks the ' + target.name + ' in a blind fury!',
                                    libtcod.light_orange]]
                messages.extend(aiObject.fighter.attack(target))

            #Reduce the number of turns to remain enraged
            self.enraged_num_turns -= 1
        else:
            #No longer enraged, revert the AI to what it originally was
            self.owner.ai =self.old_ai
            messages += [['success', 'The ' + self.owner.name + ' is no longer enraged!', libtcod.light_red]]

        return messages