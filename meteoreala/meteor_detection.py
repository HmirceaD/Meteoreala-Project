"""All of the meteor detection and analysing happens here"""

import cv2
import numpy as np
from meteoreala import star_calculator
import math
import configparser
import os
import re
from meteoreala.constelations import MeteorShower
from meteoreala import meteor_database
from math import acos, cos, sin

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT_DIR, 'config.ini')


def get_meteor_info(fits_file, visible_stars):
    """returns the analysed information"""
    data, lines = check_meteor_lines(fits_file)

    return check_meteor(lines, data.shape, fits_file, visible_stars)


def check_meteor_lines(fits_file):
    """checks to see if there are meteor lines in the image"""
    config_file = configparser.ConfigParser()
    config_file.read(CONFIG_PATH)

    data = np.uint8(fits_file.data)

    denoised = cv2.GaussianBlur(data, (5, 5), 0)

    canny2 = cv2.Canny(denoised, 100, 200, apertureSize=3)

    dilu2 = cv2.dilate(canny2, np.ones((2, 2), np.uint8), iterations=1)

    dilu2 = cv2.flip(dilu2, 0)
    
    lines = cv2.HoughLinesP(dilu2, 1,
                            np.pi / 180, int(config_file['METEOR_DETECTION']['HOUGH_LINES_THRESHOLD']),
                            int(config_file['METEOR_DETECTION']['HOUGH_LINES_MAX_LINE_GAP']),
                            int(config_file['METEOR_DETECTION']['HOUGH_LINES_MIN_LINE_LENGTH']))

    data = cv2.flip(data, 0)

    return data, lines


def check_meteor(lines, shape, fits_file, visible_stars):
    """checks if any of the meteor lines detected are error lines from nearby light sources"""
    error_lines = meteor_database.get_error_lines()

    start_point = shape
    end_point = (0, 0)

    if lines is not None:

        for line in lines:
            for x1, y1, x2, y2 in line:

                ok = True
                for err in error_lines:
                    if abs(int(err['line'][0]) - x1) < 35 and \
                            abs(int(err['line'][1]) - y1) < 35 and \
                            abs(int(err['line'][2]) - x2) < 35 and \
                            abs(int(err['line'][3]) - y2) < 35:
                        ok = False

                if ok:
                    start_point = min(start_point, (x1, y1), (x2, y2))
                    end_point = max(end_point, (x1, y1), (x2, y2))

        if start_point == shape and end_point == (0, 0):
            return {}
        else:

            return analyze_meteor(fits_file, end_point, start_point, visible_stars)
    else:
        return {}


def get_angular_distance(end_point, start_point):
    """
    Calculates the angular distance of the meteor
    """
    st_ra = start_point[0] * 15 * math.pi / 180
    st_dec = start_point[1] * math.pi / 180
    end_ra = end_point[0] * 15 * math.pi / 180
    end_dec = end_point[1] * math.pi / 180

    return math.acos(math.sin(st_dec)*math.sin(end_dec)
                     + math.cos(st_dec)*math.cos(end_dec)*math.cos(st_ra - end_ra)) * 180/math.pi


def array_difference(arr1, arr2):
    """helper function for difference of two arrays"""
    new_arr = []
    for i in arr1:
        if i not in arr2:
            new_arr.append(i)

    for j in arr2:
        if j not in arr1 and j not in new_arr:
            new_arr.append(j)

    return new_arr


def get_list_of_tuples(list1):
    """yep"""
    return [tuple(l) for l in list1]


def get_sum_of_pixels(data, pixel_arr):
    """calculates the sum of pixels in a region"""
    sum = 0
    for pixel in pixel_arr:
        sum += data[pixel[0], pixel[1]]
    return sum


def get_average_of_pixels(data, pixel_arr):
    """calculates the average of pixels in a region"""
    return get_sum_of_pixels(data, pixel_arr) / len(pixel_arr)


def get_meteor_magnitude(fits_file, end_point, start_point):
    """calculate the meteor magnitude"""
    data = np.uint8(fits_file.data)

    aperture_pixels, background_pixels = get_aperture_and_background(data, end_point, start_point)

    return get_sum_of_pixels(data, aperture_pixels) - \
           len(aperture_pixels) * get_average_of_pixels(data, background_pixels)


def get_aperture_and_background(data, end_point, start_point):
    """constructs the areas of interest for the formula of magnitude"""
    data2 = np.array(data)

    out_of_line_pixels = get_list_of_tuples(np.ndarray.tolist(np.argwhere(data2 == 0)))
    cv2.line(data2, (start_point[0], 966 - start_point[1]), (end_point[0], 966 - end_point[1]), 0, 4)

    all_pixels = get_list_of_tuples(np.ndarray.tolist(np.argwhere(data2 == 0)))
    aperture_pixels = array_difference(out_of_line_pixels, all_pixels)

    cv2.line(data2, (start_point[0], 966 - start_point[1]), (end_point[0], 966 - end_point[1]), 0, 9)
    aperture_and_background = get_list_of_tuples(np.ndarray.tolist(np.argwhere(data2 == 0)))

    background_pixels = array_difference(aperture_pixels, aperture_and_background)

    return aperture_pixels, background_pixels


def possible_shower(shower_obj, end, start, fits_file):
    """using the spherical cosine formula it checks if the meteor is part of the meteor shower"""
    config_file = configparser.ConfigParser()
    config_file.read(CONFIG_PATH)

    meteor_date = fits_file.header['DATE'][5:10].split("-")[::-1]

    if int(shower_obj.start_date[1]) <= int(meteor_date[1]) and int(shower_obj.end_date[1]) >= int(meteor_date[1]):

        a = get_angular_distance(end, start) * math.pi/180
        try:

            meteor_coords = [float(shower_obj.RA), float(shower_obj.DEC)]

        except ValueError:

            import unicodedata
            meteor_coords = [float(unicodedata.normalize('NFKD', shower_obj.RA).encode('ascii','ignore')),
                             float(unicodedata.normalize('NFKD', shower_obj.DEC).encode('ascii','ignore'))]

            if shower_obj.RA[0] not in '0123456789':
                meteor_coords[0] *= -1
            if shower_obj.DEC[0] not in '0123456789':
                meteor_coords[1] *= -1

        b = get_angular_distance(end, meteor_coords) * math.pi/180
        c = get_angular_distance(start, meteor_coords) * math.pi/180

        angle = acos((-cos(a)*cos(b) + cos(c))/(sin(a)*sin(b)))
        angle = angle * 180/math.pi

        if angle is not None and int(angle) <= int(config_file['METEOR_DETECTION']['METEOR_SHOWER_ACCURACY']):
            return angle
        else:
            return None
    else:
        return None


def calculate_meteor_shower(meteor_showers, end, start, fits_file):
    """calculates the possible meteor showers where the meteor might have come"""
    origin_shower = []

    for meteor_shower in meteor_showers:
        shower_name = meteor_shower[0].replace("-", " ")
        shower_start_date = meteor_shower[1].split('-')
        shower_end_date = meteor_shower[2].split('-')

        shower_obj = MeteorShower(shower_name, shower_start_date, shower_end_date)

        if len(meteor_shower) > 3:

            shower_longitude = meteor_shower[3]
            shower_RA = meteor_shower[4]
            shower_DEC = meteor_shower[5]
            shower_obj.set_params(shower_longitude, shower_RA, shower_DEC)

        shower1_angle = possible_shower(shower_obj, end, start, fits_file)
        shower2_angle = possible_shower(shower_obj, start, end, fits_file)
        if shower1_angle is not None:
            origin_shower.append([shower_obj.name, shower1_angle])
        if shower2_angle is not None:
            origin_shower.append([shower_obj.name, shower2_angle])

    if origin_shower == []:
        return "Sporadic"
    else:
        posible_shower = None
        min1 = 20
        for shower in origin_shower:
            print(shower)
            if shower[1] < min1:
                posible_shower = shower[0]
                min1 = shower[1]
        return str(posible_shower)


def get_meteor_shower(fits_file, end_point, start_point):
    """retrieves the information of the meteor showers"""
    meteor_showers = meteor_showers_list(os.path.join(ROOT_DIR, "meteoreala", "data_files", "meteor_showers.txt"))

    shower = calculate_meteor_shower(meteor_showers, end_point, start_point, fits_file)

    return shower


def analyze_meteor(fits_file, end_point, start_point, visible_stars):
    """
    calls all of the analysing methods and builds the dict with meteor information
    end, start == coordinates
    end_point, start_point == pixels
    :param fits_file:
    :param end_point:
    :param start_point:
    :param visible_stars:
    :return:
    """
    meteor_info = {'coordinates': {'start_point': [], 'end_point': []}, 'magnitude': "", "meteor_shower": "",
                   "image_location": {"start_pixels": [], "end_pixels": []}}

    end, start = get_coords_from_pix(fits_file, end_point, start_point)
    angular_distance = get_angular_distance(end, start)
    magnitude = get_meteor_magnitude(fits_file, end_point, start_point)
    meteor_shower = get_meteor_shower(fits_file, end, start)
    print(meteor_shower)
    meteor_info['coordinates'] = {
        'start_point': {'start_point_ra': start[0], 'start_point_dec': start[1]},
        'end_point': {'end_point_ra': end[0], 'end_point_dec': end[1]}}

    meteor_info['angular_distance'] = angular_distance
    meteor_info['magnitude'] = magnitude
    meteor_info['meteor_shower'] = meteor_shower

    # .item() converts from numpy int32 to python int
    meteor_info['image_location'] = {
        'start_pixels': {'start_pixels_x': start_point[0].item(), 'start_pixels_y': start_point[1].item()},
        'end_pixels': {'end_pixels_x': end_point[0].item(), 'end_pixels_y': end_point[1].item()}}

    return meteor_info


def meteor_showers_list(star_file_path):
    """get all of the meteor showers"""
    with open(star_file_path, "r", encoding="utf8") as f:
        meteor_showers = [re.split(',|\s', x.strip().replace("+","")) for x in f.readlines()]

        for meteor_show in meteor_showers:
            for info in meteor_show:
                if info == "":
                    meteor_show.remove(info)

        return meteor_showers


def get_coords_from_pix(image, end_point, start_point):
    """calls the methods for getting real world coordinates from pixels"""
    star_calc = star_calculator.StarCalculator(image)
    ra1, dec1 = star_calc.pix_to_ra_dec(start_point)
    ra2, dec2 = star_calc.pix_to_ra_dec(end_point)

    return (ra1, dec1), (ra2, dec2)


def get_detected_lines(fits_file):
    """get all of the detected lines"""
    new_lines = []
    data, lines = check_meteor_lines(fits_file)

    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                new_lines.append({"line":[str(x1), str(y1), str(x2), str(y2)]})
    return new_lines
