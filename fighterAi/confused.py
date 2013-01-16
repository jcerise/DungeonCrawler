import libtcodpy as libtcod

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