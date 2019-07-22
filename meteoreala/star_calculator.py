import math
from astropy.wcs import WCS
from astropy.io import fits as ft
import datetime
from meteoreala.constelations import Star
from meteoreala.constelations import ConstName
from meteoreala.constelations import ConstLine
from meteoreala.constelations import ConstBounds
import re
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_rev(lst):

    rv = lst - ((int(lst) // 360) * 360)

    if rv < 0:
        rv += 360

    return rv


def get_obj_from_file(star_file_path):
    """
    Read the astronomic objects from the .dat files
    :param star_file_path:
    :return:
    """
    with open(star_file_path, "r") as f:
        return [re.split(',|\s', x.strip().replace("+","")) for x in f.readlines()]


def get_date_time_header(header):
    """dates from the fits header"""
    date_string = re.split('[T\-:]', header['DATE-OBS'])
    return datetime.datetime(year=int(date_string[0]),
                             month=int(date_string[1]),
                             day=int(date_string[2]),
                             hour=int(date_string[3]),
                             minute=int(date_string[4]),
                             second=int(float(date_string[5])))


class StarCalculator:

    def __init__(self, fits_file):

        self.image_time = get_date_time_header(fits_file.header)

        self.stars = get_obj_from_file(os.path.join(ROOT_DIR, "meteoreala", "data_files", "constellation-lines-2.csv"))
        self.const = get_obj_from_file(os.path.join(ROOT_DIR, "meteoreala", "data_files", "conlines.dat"))
        self.const_names = get_obj_from_file(os.path.join(ROOT_DIR, "meteoreala", "data_files", "cnames.dat"))
        self.const_bounds = get_obj_from_file(os.path.join(ROOT_DIR, "meteoreala", "data_files", "const_bounds_18.dat"))

        self.long = fits_file.header["SITELONG"]
        self.lat = fits_file.header["SITELAT"]

        self.lst = self.get_lst()

        self.RADS_RA = math.pi / 180 * 15.04107
        self.RADS_DEC = math.pi / 180
        self.DEG_90 = math.pi / 2  # 90 degrees
        self.glat = self.lat * math.pi / 180

    def get_astometry_objects(self):
        """
        get all the visible stars/constelation
        lines/constelation names in the current image
        """
        visible_stars = self.get_visible_stars()
        visible_lines = self.get_lines()
        constellation_names = self.get_constelation_names()
        constellation_bounds = self.get_constelation_bounds()

        return visible_stars, visible_lines, constellation_names, constellation_bounds

    def get_constelation_bounds(self):
        """
        Get lines and points that map the bounds
        of each visible constelation
        """

        temp_cbounds = []
        name = self.const_bounds[0][2]
        bound = ConstBounds(name=name)

        for point in self.const_bounds:

            if name != point[2] and point[2] != '00.00000':
                # got to next constellation
                name = point[2]
                bound.points_to_lines()
                temp_cbounds.append(bound)
                bound = ConstBounds(name=name)

            try:
                z, x, y = self.astro_object_coords(ra=float(point[0]), dec=float(point[1]))

                if z < math.pi / 2:
                    bound.add_point(x, y)

            except ValueError:
                continue

        return temp_cbounds

    def get_lines(self):
        """
        Calculates the segments of the constelation lines and checks if
        they are above the horizon ( < 90 deg)
        """

        temp_lines = []

        for line in self.const:

            z1, x1, y1 = self.astro_object_coords(ra=float(line[1])/1000, dec=float(line[2])/100)
            z2, x2, y2 = self.astro_object_coords(ra=float(line[3])/1000, dec=float(line[4])/100)

            if z1 < math.pi/2 and z2 < math.pi/2:
                temp_lines.append(ConstLine(x1, x2, y1, y2))

        return temp_lines

    def get_visible_stars(self):
        """
        Calculates the positions of stars and checks if they are above
        the horizon
        ra = Right Ascension
        dec = Declination
        """
        temp_stars = []
        for star in self.stars:

            if star[2] != "" and star[3] != "":

                z, x, y = self.astro_object_coords(ra=float(star[2]), dec=float(star[3]))

                if z < math.pi/2:
                    temp_stars.append(Star(star[0], x, y))

        return temp_stars

    def get_constelation_names(self):
        """
        get the x,y coordinates along with then names
        of constelations
        """
        temp_names = []

        for name in self.const_names:

            z, x, y = self.astro_object_coords(ra=float(name[0])/1000, dec=float(name[1])/100)

            if z < math.pi/2:
                temp_names.append(ConstName(x, y, name[2]))

        return temp_names

    def astro_object_coords(self, ra, dec):
        """
        Calculate the x,y pixels of the object
        :param dec: declination of obj
        :param ra: right ascension of obj
        :return: the coordinates to where the object should be plotted on the picture
        """

        ra *= self.RADS_RA
        dec *= self.RADS_DEC

        z = math.acos(math.sin(dec) * math.sin(self.glat) + math.cos(dec)
                      * math.cos(self.glat) * math.cos(ra - self.lst))
        k = z / math.sin(z)
        x = (k * math.cos(dec) * math.sin(ra - self.lst)) * 280 + 648
        y = (k * math.sin(dec) * math.cos(self.glat) - math.cos(dec) *
             math.cos(ra - self.lst) * math.sin(self.glat)) * 350 + 483

        return z, x, y

    def pix_to_ra_dec(self, point):
        """
        Converts the values of pixels into stellar coordinates
        """
        y = 966 - point[1]
        x = (point[0] - 648) / 280
        y = (y - 483) / 350

        ang_dist = math.sqrt(x**2 + y**2)

        dec = math.asin(math.cos(ang_dist) * math.sin(self.glat)
                        + (y * math.sin(ang_dist) * math.cos(self.glat)) / ang_dist)
        dec = dec * 180 / math.pi

        ra = (self.lst + math.atan((x*math.sin(ang_dist)) / (ang_dist * math.cos(self.glat) * math.cos(ang_dist) - y
                                                             * math.sin(self.glat) * math.sin(ang_dist)))) * 180/math.pi

        ra = get_rev(ra) / 15.04107

        return ra, dec

    def get_lst(self):
        """
        Get local sidereal time
        days_passed = days that passed since 1 Jan 2000
        """

        days_passed = self.get_days_passed()
        time = self.get_time()

        lst = get_rev(100.46 + 0.985647 * days_passed + self.long + time * 15.04107)
        lst *= math.pi / 180

        return lst

    def get_time(self):
        """
        get regular time
        :return:
        """
        time = (self.image_time.hour + self.image_time.minute / 60 + self.image_time.second / 3600)
        return time

    def get_days_passed(self):
        """
        get the number of days that have passed since the date in the .fits file
        :return:
        """
        return 367 * self.image_time.year - (7 * (self.image_time.year + ((self.image_time.month + 9) / 12))) / 4 \
               + (275 * self.image_time.month) / 9 + self.image_time.day - 730530
