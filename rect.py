class Rect:
    #A rectangle on the map, used to represent a room
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return (center_x, center_y)

    def intersect(self, other):
        #Check if this rect intersects (overlaps) another rect
        #if the top left corner is less than the bottom right corner of the other rect,
        #and the bottom right corner is greater than the top right of the other rect,
        #the rects intersect
        return(self.x1 <= other.x2 and self.x2 >= other.x1 and
               self.y1 <= other.y2 and self.y2 >= other.y1)