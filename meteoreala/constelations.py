"""all of the classes for astronomic objects are here, all have the
pixel coordinates that will be mapped on the image"""


class ConstLine:
    """class for the lines of a constellation"""
    def __init__(self, x1, x2, y1, y2):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2


class Star:
    """class for the stars"""
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y

    def get_star_pos(self):
        return self.x, self.y


class ConstName:
    """class for the names of the constellations"""
    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.name = name


class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_point(self):
        return [self.x, self.y]


class MeteorShower:
    """class for the meteor shower"""
    def __init__(self, name, start_date, end_date):
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.longitude = 0
        self.RA = '0'
        self.DEC = '0'

    def set_params(self, longitude, RA, DEC):
        self.longitude = longitude
        self.RA = RA
        self.DEC = DEC


class ConstBounds:
    """class for the constellation bounds"""
    def __init__(self, name):

        self.name = name
        self.points = []
        self.lines = []

    def add_point(self, x, y):
        self.points.append(Point(x, y))

    def points_to_lines(self):

        for ind in range(len(self.points)):
            try:
                self.lines.append(ConstLine(x1=self.points[ind].get_point()[0],
                                            x2=self.points[ind+1].get_point()[0],
                                            y1=self.points[ind].get_point()[1],
                                            y2=self.points[ind+1].get_point()[1]))
            except IndexError:
                continue
