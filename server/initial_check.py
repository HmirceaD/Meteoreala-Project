import os
import configparser

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT_DIR, 'config.ini')


def check_config_file():
    """
    checks if the config.ini is in order
    :return:
    """
    error = 0

    if not os.path.isfile(CONFIG_PATH):
        error = 1
    else:
        config_file = configparser.ConfigParser()
        config_file.read(CONFIG_PATH)

        for sections in config_file:
            for value in config_file[sections]:
                if config_file[sections][value] == "":
                    error = 2

    return error


def perform_setup():
    """
    setups the dirs from the config.ini correctly if they are not already correct
    :return:
    """
    config_file = configparser.ConfigParser()
    config_file.read(CONFIG_PATH)

    dirs = [config_file['GENERAL']['fitsimagepaths'],
            config_file['GENERAL']['fitsfilepaths'],
            config_file['GENERAL']['imagefilepaths']]

    for dir in dirs[:2]:
        if not os.path.isdir(dir):
            os.mkdir(dir)

    if not os.path.isdir(dirs[2]):
        os.mkdir(dirs[2])
    else:
        locations = config_file['CAMERAS']['location_names'].split(",")
        for location in locations:
            location_path = os.path.join(dirs[2], location)
            if not os.path.isdir(location_path):
                os.mkdir(location_path)


def check_all_the_stuff():
    """checks all the stuff"""
    error_code = check_config_file()

    if error_code == 0:
        perform_setup()
        return error_code
    else:
        return error_code
