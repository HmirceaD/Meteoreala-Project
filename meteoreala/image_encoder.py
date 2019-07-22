"""run length encoding and decoding"""

import numpy as np


def pairwise(iterable):
    a = iter(iterable)
    return zip(a, a)


def split_bits(np_elem, num):
    """
    vectorized function for the np.array to return an array
    of the n-th bit of all values
    :param np_elem: np.array element
    :param num: n
    """
    return ("0" * (8 - len(bin(np_elem)[2:])) + bin(np_elem)[2:])[num]


def run_length_encoding(fits_file, new_save_path):
    """
    apply a run length encoding on the image
    """

    rle = []
    pixels = np.array(fits_file.data).flatten()

    temp_pixels = []
    avg_pixel = 0
    k = 1

    for ind, num in enumerate(pixels):
        try:
            if abs(pixels[ind] - pixels[ind+1]) < 20:
                temp_pixels.append(pixels[ind])
                k += 1
            else:
                if len(temp_pixels) != 0:

                    avg_pixel = sum(temp_pixels) // len(temp_pixels)
                    temp_pixels.clear()
                else:
                    avg_pixel = pixels[ind]

                rle.extend([k, avg_pixel])
                k = 1

        except IndexError:
            rle.extend([k, avg_pixel])

    fits_file.change_data(np.array(rle, dtype=np.uint16))
    fits_file.save_image(new_save_path)

    return fits_file.saved_path


def run_length_decoding(fits_file, new_save_path):
    """
    Take the run-length encoded image an decode it
    into a normal ndarray
    """

    pixels = []
    for num, val in pairwise(fits_file.data):
        for i in range(num):
            pixels.append(val)

    new_data = np.array(pixels, dtype=np.uint16)
    new_data = new_data.reshape((966, 1296))

    fits_file.change_data(new_data)
    fits_file.save_image(new_save_path)

    return fits_file.saved_path


def get_bit_planes(fits_file):
    """
    take an image and create 8 matrices each with
    the n-th bit of all values in the array (n[1-8])
    """
    normalized_data = fits_file.convert_to_8bit()

    bit_planes = np.ndarray((8, 966, 1296), dtype=np.uint8)

    fa = np.vectorize(split_bits)

    for plane in range(8):
        bit_planes[plane] = fa(normalized_data, plane)

    return bit_planes
