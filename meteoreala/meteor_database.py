import os
from astropy.io import fits as ft
import configparser
import pymongo
from bson.objectid import ObjectId
import bson


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT_DIR, 'config.ini')


def get_db_client():
    """Establish connection to the mongo database"""
    config_file = configparser.ConfigParser()
    config_file.read(CONFIG_PATH)
    db_client = pymongo.MongoClient("mongodb://{}:{}/"
                                    .format(config_file['MONGODB']['mongo_ip'],
                                            config_file['MONGODB']['mongo_port']))
    return db_client


def save_fits_file(fits_file):
    """saves the resulting fits file on disk"""
    config_file = configparser.ConfigParser()
    config_file.read(CONFIG_PATH)

    save_path = os.path.join(config_file['GENERAL']['fitsfilepaths'], fits_file.header['FILENAME'])
    hdu = ft.PrimaryHDU(data=fits_file.data, header=fits_file.header)
    hdu.writeto(save_path, overwrite=True)

    return save_path


def save_to_db(fits_file, meteor_info):
    """saves a dict with the detected meteor information somewhere on disk"""
    db_client = get_db_client()

    meteors_col = db_client['meteors']['confirmed']

    meteor_info['save_path'] = save_fits_file(fits_file)

    with ft.open(meteor_info['save_path']) as hdu:
        meteor_info['location'] = hdu[0].header['TELESCOP']
        meteor_info['date'] = hdu[0].header['DATE'][:10]

    del fits_file

    insert = meteors_col.insert_one(meteor_info)


def get_meteor_by_id(meteor_id):
    """searches for a meteor entry with a specific mongo id"""
    db_client = get_db_client()

    meteors_col = db_client['meteors']['confirmed']

    try:
        meteor = [meteor for meteor in meteors_col.find({"_id": ObjectId(meteor_id)})]
    except bson.errors.InvalidId:
        meteor = []

    return meteor


def get_meteors_from_filters(filer_dict):
    """searches for the meteor by specific location and date"""
    db_client = get_db_client()

    meteors_col = db_client['meteors']['confirmed']

    return [dict(meteor) for meteor in meteors_col.find(filer_dict)]


def get_meteors():
    """queries all detected meteors"""
    db_client = get_db_client()

    meteors_col = db_client['meteors']['confirmed']

    return [dict(meteor) for meteor in meteors_col.find({})]


def save_error_lines(error_lines):
    """cleans and saves the detected error lines"""
    db_client = get_db_client()

    error_lines_col = db_client['meteors']['error_lines']
    delete = error_lines_col.delete_many({})
    insert = error_lines_col.insert_many(error_lines)


def get_error_lines():
    """retrieves all of the error lines"""
    db_client = get_db_client()

    error_lines_col = db_client['meteors']['error_lines']

    return [dict(error_line) for error_line in error_lines_col.find({})]



