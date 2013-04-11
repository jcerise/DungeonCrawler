import random
import libtcodpy as libtcod


class CombatResolver:

    def __init__(self, sides):
        #Set the number of sides to include on the open ended die rolls
        self.diceSides = sides

    def makeOEDRoll(self):
        #Make an open ended D6 roll. Roll one D6, if the result is 6, add to the total and roll again. Repeat this
        #until the result of the roll is not 6. Since the mechanics of the game involve comparing two stats + a OED,
        #this system allows for anything to be possible (a rat landing a critical hit on a heavily armored knight),
        #although they may be very improbable. Basically, nothing is impossible.
        totalRoll = 0

        dieResult = random.randint(1,6)
        while dieResult == 6:
            #subtract one from the roll (always 6, in this case)
            totalRoll += dieResult - 1
            dieResult = random.randint(1,6)

        totalRoll += dieResult

        return totalRoll

    def initiateCombat(self, attacker, defender):
        #Combat happens in two rounds. The first determines if the attacker has successfully hit the defender. The
        #second round (only if the attacker hits) determines how much damage is dealt by the attacker to the defender.

        messages = []

        attackerAttack = attacker.base_attack + attacker.base_accuracy + self.makeOEDRoll()
        defenderDefence = defender.fighter.base_defence + defender.fighter.base_agility + self.makeOEDRoll()

        #Compare the two values. if the attackers is larger, the attacker hits. If not, the defender has dodged the blow
        if attackerAttack > defenderDefence:
            result = self.resolveDamage(attacker, defender)
            messages.append(result[0])
            damageDealt = result[1]
        else:
            messages.append(['success', defender.name.capitalize() + ' has evaded the attack by  ' + attacker.owner.name,
                             libtcod.lighter_blue])
            damageDealt = 0

        return messages, damageDealt

    def resolveDamage(self, attacker, defender):
        #At this point, the attacker has successfully connected an attack on the defender. Damage is now calculated.
        #This is a combination of the attackers strength, with any equipment bonus added in.
        totalDamage = attacker.damage + self.makeOEDRoll()
        totalProtection = defender.fighter.protection + self.makeOEDRoll()

        dealtDamage = totalDamage - totalProtection

        if dealtDamage <= 0:
            dealtDamage = 0

        #If no damage was dealt, make the message white, so as not to draw as much attention to it
        if dealtDamage is 0:
            color = libtcod.white
        else:
            color = libtcod.light_red

        return [['success', attacker.owner.name.capitalize() + ' hits the ' + defender.name + ' for ' + str(dealtDamage) +
                           ' damage!', color], dealtDamage]
