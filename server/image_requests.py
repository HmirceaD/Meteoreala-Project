"""constant loop that checks for the """
from meteoreala import meteor_handler
import os
import threading

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT_DIR, 'config.ini')


def uploaded_fits_files(config_file, paths):
    """
    starts the analysis algorithm for the uploaded uploaded fits frames
    :param config_file:
    :param paths:
    :return:
    """
    meteor_handler.analyze_image_stream(paths, config_file)
    for path in paths:
        os.remove(path)


def meteor_check(location_path, config_file):
    """
    starts the analysis algorithm for the fits frames
    :param location_path:
    :param config_file:
    :return:
    """
    paths = get_image_paths(location_path)

    if paths != []:
        meteor_handler.analyze_image_stream(paths, config_file)

        for path in paths:
            os.remove(path)


def get_image_paths(location_path):
    """
    gets the absolute paths of the fits frames from the files
    :param location_path:
    :return:
    """
    paths = []
    for dirpath, _, filenames in os.walk(location_path):
        for f in filenames:
            paths.append(os.path.abspath(os.path.join(dirpath, f)))
    return paths


def correct_analyze_image_stream(config_file):
    """
    starts the threads for fits frame analysis from the camera folders
    :param config_file:
    :return:
    """
    locations = config_file['CAMERAS']['location_names'].split(",")

    location_path = [os.path.join(config_file['GENERAL']['imagefilepaths'],
                                  location_path) for location_path in locations]

    camera_threads = []
    for l_path in location_path:

        camera_threads.append(threading.Thread(target=meteor_check, args=(l_path, config_file,)))

    for thr in camera_threads:
        thr.start()
        thr.join()

    threading.Timer(float(config_file['CAMERAS']['analysis_check']),
                    correct_analyze_image_stream, args=(config_file,)).start()


def error_lines_build(config_file):
    """
    starts the threads for fits frame analysis for the error lines
    :param config_file:
    :return:
    """
    locations = config_file['CAMERAS']['location_names'].split(",")

    location_path = [os.path.join(config_file['GENERAL']['imagefilepaths'],
                                  location_path) for location_path in locations]

    all_paths = []
    for loc_path in location_path:
        all_paths.append(get_image_paths(loc_path)[0])

    if all_paths != []:
        meteor_handler.build_error_lines(all_paths)
