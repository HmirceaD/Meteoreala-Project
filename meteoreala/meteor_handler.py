"""mid point between meteor analysing and server"""
from meteoreala import process_image
from meteoreala import image_stacking
from meteoreala.fits_image import FitsImage
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def analyze_image_stream(paths, config_file):
    """creates single image from fits files and starts analysing"""

    img_stacker = image_stacking.ImageStacker(config_file)
    fits_file = img_stacker.convert_from_paths(paths)

    process_image.analyze_image(fits_file)


def build_error_lines(all_paths):
    """create the error lines"""
    camera_fits_files = []
    for camera_path in all_paths:
        print(camera_path)
        camera_fits_files.append(FitsImage(camera_path))

    process_image.process_error_lines(camera_fits_files)

if __name__ == '__main__':
    process_image.analyze_image(FitsImage("E:\Programare\Licenta\Proiect\Meteoreala\Meteoreala\\fitsImages\Galati_2018_07_08T19_30_27_UT.fit"))