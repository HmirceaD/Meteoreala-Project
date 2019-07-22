"""flask server for the meteoreala project"""

from flask import Flask
from flask import render_template
import sys
import os
import configparser
from datetime import datetime
from threading import Timer
from server import image_requests
from server import java_connection
from meteoreala import meteor_database
from astropy.io import fits as ft
from flask import request
from flask import redirect
from werkzeug.utils import secure_filename
from threading import Thread
from server import initial_check

APP = Flask(__name__, template_folder='templates')
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT_DIR, 'config.ini')
UPLOAD_DIR = os.path.join(ROOT_DIR, 'server', 'static')
SERVER_DIR = os.path.join(ROOT_DIR, 'server')
FITS_FILE_DIR = os.path.join(ROOT_DIR, 'server', 'temp_fits')

error_dict = {1: "config file does not exist",
              2: "One or more config values are not set or one of the folder paths in the config file does not exist"}


def check_config():
    """checks the config file"""
    if os.path.isfile(CONFIG_PATH):

        config_file = configparser.ConfigParser()
        config_file.read(CONFIG_PATH)
        return config_file

    else:
        print("No config file")
        sys.exit(0)


def check_error_lines(config_file):
    """analysis error lines"""
    image_requests.error_lines_build(config_file=config_file)


def time_from_config(config_file):
    """gets the time from the config file"""
    try:
        hour = abs(int(config_file['CAMERAS']['error_lines_hour']))
        minutes = abs(int(config_file['CAMERAS']['error_lines_minutes']))
    except ValueError:
        hour = 22
        minutes = 0

    if hour > 23:
        hour %= 23

    if minutes > 59:
        minutes %= 59

    return hour, minutes


def error_lines_thread(config_file):
    """starts the thread for the config file that will be checked everyday at a certain hour"""
    x = datetime.today()

    hour, minutes = time_from_config(config_file)

    y = x.replace(day=x.day + 1, hour=hour, minute=minutes, second=0, microsecond=0)
    delta_t = y - x
    secs = delta_t.seconds + 1

    t = Timer(secs, check_error_lines, args=(config_file,))
    t.start()


def start_server():
    """
    starts the server
    :return:
    """
    config_file = check_config()

    check_up = initial_check.check_all_the_stuff()

    if check_up == 0:
        pass
    else:
        print(error_dict[check_up])
        sys.exit(1)

    java_connection.start_java_gateway(config_file)
    error_lines_thread(config_file=config_file)

    Thread(target=image_requests.correct_analyze_image_stream, args=(config_file,)).start()

    APP.run(config_file['SERVER']['server_ip'],
            int(config_file['SERVER']['port']))


@APP.route('/', methods=['GET'])
def index_route():
    """index route, checks if the http request has any get parameters"""

    if request.args.get("databaseId") != "" and request.args.get("databaseId") is not None:
        return redirect("/{}".format(request.args.get("databaseId")))

    if (request.args.get("location") == "" and request.args.get("date") == "") or \
            (request.args.get("location") is None and request.args.get("date") is None):

        meteor_arr = meteor_database.get_meteors()

        return render_template('index.html', meteors=meteor_arr)

    else:
        filter_dict = {}

        if request.args.get("location") != "":
            filter_dict["location"] = request.args.get("location")

        if request.args.get("date") != "":
            filter_dict["date"] = request.args.get("date")

        return render_template('index.html', meteors=meteor_database.get_meteors_from_filters(filter_dict))


@APP.route('/uploader', methods=["POST", "GET"])
def uploader_route():
    """handles the uploaded fits frames and redirects"""
    if request.method == "POST":
        files = request.files.getlist("files")
        paths = []

        for file in files:
            fits_path = os.path.join(FITS_FILE_DIR, secure_filename(file.filename))
            paths.append(fits_path)
            file.save(fits_path)

        config_file = check_config()

        thread = Thread(target=image_requests.uploaded_fits_files, args=(config_file, paths))
        thread.start()
        thread.join()

        return redirect("/")
    else:
        return redirect("/upload")


@APP.route('/upload')
def upload_route():
    """renders the template for upload"""
    return render_template('upload.html')


@APP.route('/<id>')
def meteor_route(id):
    """renders the template for a specific document in the mongodb"""
    meteor = meteor_database.get_meteor_by_id(id)

    if meteor == []:
        meteor = ""
    else:

        meteor = meteor[0]
        with ft.open(meteor['save_path']) as hdu:
            meteor['location'] = hdu[0].header['TELESCOP']
            meteor['date'] = hdu[0].header['DATE']

    return render_template('meteor.html', meteor=meteor)


@APP.errorhandler(404)
def page_not_found(e):
    """404 error route"""
    return render_template('error404.html'), 404


start_server()