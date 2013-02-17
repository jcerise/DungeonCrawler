import libtcodpy as libtcod
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

    def setup_monsters(self):
        #Figure out which monsters to include on this level, and load them all
        #TODO: For each level, the player can encounter monsters from the previous level, as well as the next level
        #There is a 50% decrease in encounter chances for previous level monsters
        #There is a 75% decrease in encounter chances for next level monsters
        #This will keep the chance of difficult monsters a possibility on any level

        monster_tree = ET.parse('monsters/level-0.xml')
        monster_root = monster_tree.getroot()

        monsters = []

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
            m.append(monster.find('encounter-chance').text)
            m.append(monster.find('xp').text)

            #Add the newly created monster list to the list of monsters
            monsters.append(m)

        #Next, build a list with just the monster appearance chances, so we can figure out later how often each monster will
        #show up. The index of the chance in this list directly corresponds to the index of the monster in the monsters list
        monster_appearance_chances = []

        for appearing_monster in monsters:
            monster_appearance_chances.append(int(appearing_monster[10]))

        return (monsters, monster_appearance_chances)

    def setup_items(self):
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
            i = []
            i.append(item.get('name'))
            i.append(item.find('type').text)
            i.append(item.find('use').text)
            i.append(item.find('value').text)
            i.append(item.find('range').text)
            i.append(item.find('character').text)
            i.append(item.find('color-r').text)
            i.append(item.find('color-g').text)
            i.append(item.find('color-b').text)
            i.append(item.find('encounter-chance').text)
            i.append(item.find('targeting').text)


            #Add the newly created monster list to the list of monsters
            items.append(i)

        #Next, build a list with just the item appearance chances, so we can figure out later how often each item will
        #show up. The index of the chance in this list directly corresponds to the index of the item in the item list
        item_appearance_chances = []

        for appearing_item in items:
            item_appearance_chances.append(int(appearing_item[9]))

        return (items, item_appearance_chances)

