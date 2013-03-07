import libtcodpy as libtcod
from objectComponent.fighter import *
from objectComponent.equipment import *
from fighterAi.basic import *
from gameObject import *
import xml.etree.ElementTree as ET


class AbstractMapGenerator():

    def setup_map(self):
        raise NotImplementedError

    def place_objects(self):
        raise NotImplementedError

    def random_choice_index(self, chances):
        #Choose an option from a list of chances
        #Roll a die, which will land somewhere between 1 and the total of the chances list
        #Then, we simply need to figure out what range in the list that number falls under
        dice = libtcod.random_get_int(0, 1, sum(chances))

        running_sum = 0
        choice = 0
        #Go through all chances, keeping the total so far
        for w in chances:
            running_sum += w

            #Check if the die roll is smaller or equal to the current total.
            #If it is, we know the chance range the roll fell into
            if dice <= running_sum:
                return choice
            choice += 1

    def is_blocked(self, map, objects, x, y):
        #Test the map tile at the coordinates to see if it is blocked or not
        if map[x][y].blocked:
            return True

        #Then, check through all objects and see if any of them are blocking
        for object in objects:
            if object.blocks and object.x == x and object.y == y:
                return True

        #There is no object or tile blocking this position
        return False

    def setup_monsters(self, level):
        #Figure out which monsters to include on this level, and load them all
        #TODO: For each level, the player can encounter monsters from the previous level, as well as the next level
        #There is a 50% decrease in encounter chances for previous level monsters
        #There is a 75% decrease in encounter chances for next level monsters
        #This will keep the chance of difficult monsters a possibility on any level

        #Figure out the level, and load the monsters accordingly
        current_level_file = 'monsters/level-' + str(level) + '.xml'
        monster_lists = [current_level_file]

        if level + 1 <= 3:
            monster_lists.append('monsters/level-' + str(level + 1) + '.xml')
        if level - 1 >= 1:
            monster_lists.append('monsters/level-' + str(level - 1) + '.xml')

        monsters = []

        index_counter = 0

        for list in monster_lists:
            monster_tree = ET.parse(list)
            monster_root = monster_tree.getroot()

            #Create a list with all the applicable monsters for this floor
            for monster in monster_root.findall('monster'):
                m = []
                m.append(monster.get('name'))
                m.append(monster.find('type').text)
                m.append(monster.find('ai-type').text)
                m.append(monster.find('hit-points').text)
                m.append(monster.find('defense').text)
                m.append(monster.find('attack-power').text)
                m.append(monster.find('character').text)
                m.append(monster.find('color-r').text)
                m.append(monster.find('color-g').text)
                m.append(monster.find('color-b').text)

                #Check for other levelled lists, an dif appropriate, add their monsters encounter chances at a
                #reduced chance (25% for harder, and 50% for easier)
                if index_counter == 1:
                    chance = int(monster.find('encounter-chance').text) * .25
                    m.append(chance)
                elif index_counter == 2:
                    chance = int(monster.find('encounter-chance').text) * .50
                    m.append(chance)
                else:
                    m.append(monster.find('encounter-chance').text)

                m.append(monster.find('xp').text)

                #Add the newly created monster list to the list of monsters
                monsters.append(m)
            index_counter += 1;

        # Next, build a list with just the monster appearance chances, so we can figure out later how often each monster
        # will show up. The index of the chance in this list directly corresponds to the index of the monster in the
        # monsters list
        monster_appearance_chances = []

        for appearing_monster in monsters:
            monster_appearance_chances.append(int(appearing_monster[10]))

        return monsters, monster_appearance_chances

    def setup_items(self, level):
        #Figure out which items to include on this level, and load them all
        #TODO: For each level, the player can encounter items from the previous level, as well as the next level
        #There is a 50% decrease in encounter chances for previous level items
        #There is a 75% decrease in encounter chances for next level items
        #This will keep the items semi-random on any level

        item_tree = ET.parse('items/level-0.xml')
        item_root = item_tree.getroot()

        items = []

        #Create a list with all the applicable monsters for this floor
        for item in item_root.findall('item'):
            i = {}
            i['name'] = item.get('name')
            i['type'] = item.find('type').text

            if item.find('type').text == 'equipment':
                #We have a slightly different set of attributes for equipment
                i['use'] = item.find('use').text
                i['attack'] = item.find('attack').text
                i['range'] = item.find('range').text
                i['slot'] = item.find('slot').text
            else:
                #This is a standard item, find the appropriate attributes
                i['use'] = item.find('use').text
                i['value'] = item.find('value').text
                i['range'] = item.find('range').text
                i['targeting'] = item.find('targeting').text

            i['character'] = item.find('character').text
            i['color-r'] = item.find('color-r').text
            i['color-g'] = item.find('color-g').text
            i['color-b'] = item.find('color-b').text
            i['encounter-chance'] = item.find('encounter-chance').text

            #Add the newly created monster list to the list of monsters
            items.append(i)

        #Next, build a list with just the item appearance chances, so we can figure out later how often each item will
        #show up. The index of the chance in this list directly corresponds to the index of the item in the item list
        item_appearance_chances = []

        for appearing_item in items:
            item_appearance_chances.append(int(appearing_item['encounter-chance']))

        return items, item_appearance_chances

    def generate_monster(self, x, y, appearance_chances, monsters):
        #Choose a monster to spawn from the list of applicable monsters
        spawn = self.random_choice_index(appearance_chances)

        #Choose the monster based on the spawn chance
        monster = monsters[spawn]

        #Create a death function for the monster
        monster_death = getattr(Fighter, 'monster_death')

        #Create a component for the monster based on the monster type
        if monster[1] == 'fighter':
            fighter_component = Fighter(hp=int(monster[3]), defense=int(monster[4]), power=int(monster[5]),
                                        xp=int(monster[11]), death_function=monster_death)

        #Create an AI component for the monster based on its AI type
        if monster[2] == 'basic':
            ai_component = BasicMonster()

        #Finally, create the monster
        monster = Object(x, y, char=monster[6], name=monster[0], color=libtcod.Color(int(monster[7]),
                         int(monster[8]), int(monster[9])), blocks=True, fighter=fighter_component,  ai=ai_component)

        return monster

    def generate_item(self, x, y, appearance_chances, items):
        #Choose an item to create from the list of applicable items
        item_choice = self.random_choice_index(appearance_chances)

        #Choose the item based on the spawn chance
        item = items[item_choice]

        #Find the use function for this object, and apply it to the item
        item_use_function = item['use']

        if item['type'] == 'equipment':
            #This is a piece of equipment, so create equipment instead of a standard item
            equipment = Equipment(item['slot'])

            item = Object(x, y, item['character'], item['name'], color=libtcod.Color(int(item['color-r']),
                          int(item['color-g']), int(item['color-b'])),equipment=equipment)
        else:
            #Create an object and item component from the loaded values
            item_component = Item(value=int(item['value']), range=int(item['range']), use_function=item_use_function,
                                  targeting=item['targeting'])

            item = Object(x, y, item['character'], item['name'], color=libtcod.Color(int(item['color-r']),
                          int(item['color-g']), int(item['color-b'])), item=item_component)

        return item

