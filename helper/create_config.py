import configparser
import os

config = configparser.ConfigParser()
crr_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def init_config():
    """create a default config.ini file"""

    config['GENERAL'] = {'fitsimagepaths':"--PATH HERE--",
                         'fitsfilepaths':"--PATH HERE--",
                         'imagefilepaths': "{}\\cameras".format(crr_dir)}

    config['IMAGES'] = {"imagewidth": "1296",
                        "imageheight": "966"}

    config['PERFORMANCE'] = {'numberofcores': "3"}

    config['SERVER'] = {"server_ip": "localhost",
                        "port": "5000"}

    config['JAVA_SERVER'] = {'java_gateway_port': "25333"}

    config['MONGODB'] = {"mongo_ip": "localhost",
                         "mongo_port": "27017"}

    config['METEOR_DETECTION'] = {'HOUGH_LINES_MIN_LINE_LENGTH': "20",
                                  'HOUGH_LINES_MAX_LINE_GAP': "20",
                                  'HOUGH_LINES_THRESHOLD': "15",
                                  'METEOR_SHOWER_ACCURACY': "5"}

    config['METEOR_DETECTION'] = {'location_names': "Galati,Barlad",
                                  'analysis_check': "10",
                                  'error_lines_hour': "22",
                                  "error_lines_minutes":"00"}

    config['IMPORTANT'] = {'If you intend to modify the values in the config.ini'
                           ' then read the README.md first at the base of the project': "true"}

    with open("config.ini", 'w') as config_file:
        config.write(config_file)
