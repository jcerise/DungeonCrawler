import libtcodpy as libtcod
from fighterAi.confused import *
from fighterAi.enraged import *


class Spell:
    #Defines a spell that can be cast directly from an object (via an item, or an action (learned spell))
    #Also contains all the targeting code for spells to properly find targets
    def __init__(self, caster):
        self.caster = caster

    def cast_spell(self, spell, value, range, caster, objects, fov_map):
        #Cast a spell, as specified by the value of spell
        spell_to_cast = getattr(self, spell)
        message = spell_to_cast(value, range, caster, objects, fov_map)
        return message

    #####################
    # Spell Definitions
    #####################

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

    def cast_enrage(self, damage, range, caster, objects, fov_map):
        enemy = self.closest_enemy(range, caster, objects, fov_map)
        if enemy is None:
            message = [['cancelled', 'No enemy is close enough to enrage...', libtcod.red]]
            return message
            #Replace the enemies AI with a enraged one. This will revert after a few turns
        old_ai = enemy.ai
        enemy.ai = EnragedMonster(old_ai, damage)
        enemy.ai.owner = enemy
        message = [['success', 'You feel a faint warming in the air as you read the scroll, as if the temperature' +
                               ' in the room has increased. Suddenly, the ' + enemy.name + ' tenses up, and lets out' +
                               ' an angry noise! It begins brutally laying into anything that it lays eyes on!',
                    libtcod.light_orange]]
        return message

    ######################
    # Targetting functions
    ######################

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
