from astropy.io import fits as ft
import cv2


class FitsImage:
    """class that holds the information of the fits image"""
    def __init__(self, image_path):

        self.saved_path = image_path

        with ft.open(image_path) as hdu:
            self.data = hdu[0].data
            self.header = hdu[0].header

    def convert_to_8bit(self):
        return cv2.convertScaleAbs(self.data)

    def change_data(self, new_data):

        self.data = new_data

    def change_header(self, header):

        self.header = header

    def save_image(self, new_path):

        ft.PrimaryHDU(header=self.header, data=self.data)\
            .writeto(new_path, overwrite=True)

        self.saved_path = new_path

    def close(self):

        hdu = ft.open(self.saved_path)
        hdu.close()
