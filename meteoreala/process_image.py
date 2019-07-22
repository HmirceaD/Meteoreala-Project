from matplotlib.colors import LogNorm
from astropy.visualization import astropy_mpl_style
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from meteoreala import meteor_database
from meteoreala import meteor_detection
from meteoreala import star_calculator
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_png_name(fits_file):
    """name of the final png image"""
    return fits_file.header['FILENAME'].replace('.fit', '.png')


def analyze_image(fits_file):
    """plots the image and displays the output on the screen
    then saves the plot """

    star_calc = star_calculator.StarCalculator(fits_file)
    visible_stars, visible_lines, const_names, const_bounds = star_calc.get_astometry_objects()

    meteor_info = meteor_detection.get_meteor_info(fits_file, visible_stars)

    if meteor_info != {}:

        meteor_info['plot_name'] = plot_image(fits_file, const_bounds, const_names,
                                              visible_lines, visible_stars, meteor_info)

        meteor_database.save_to_db(fits_file, meteor_info)


def process_error_lines(camera_fits_files):
    """process of error lines"""
    error_lines = []
    for fits_file in camera_fits_files:

        temp_lines = meteor_detection.get_detected_lines(fits_file)

        if temp_lines != []:
            for lines in temp_lines:
                error_lines.append(lines)

    meteor_database.save_error_lines(error_lines)


def plot_image(fits_file, const_bounds, const_names,
               visible_lines, visible_stars, meteor_info):
    """plots the image and the found astronomic objects on it using mathplotlib, in greyscale"""

    plt.style.use(astropy_mpl_style)
    plt.figure(num=None, figsize=(17, 9), dpi=80)

    plt.imshow(fits_file.data, cmap='gray', norm=LogNorm())
    cbar = plt.colorbar(ticks=[5.e3, 1.e4, 2.e4])
    cbar.ax.set_yticklabels(['5,000', '10,000', '20,000'])

    highlight_plot(const_bounds, const_names, meteor_info, visible_lines, visible_stars)

    plt.savefig(os.path.join(ROOT_DIR, "server", "static", get_png_name(fits_file)))
    # plt.show()

    return os.path.join("static", get_png_name(fits_file))


def highlight_plot(const_bounds, const_names, meteor_info, visible_lines, visible_stars):
    """adds the astronomic objects to the plot"""
    highlight_stars(plt, visible_stars)
    highlight_lines(plt, visible_lines)
    highlight_names(plt, const_names)
    highlight_bounds(plt, const_bounds)
    #highlight_meteor(plt, meteor_info)
    #highlight_additional_info(plt, meteor_info)


def highlight_meteor(plt, meteor_info):
    """add the meteor"""
    start = (966-meteor_info['image_location']['start_pixels']['start_pixels_x'], 966-meteor_info['image_location']['end_pixels']['end_pixels_x'])
    end = (meteor_info['image_location']['start_pixels']['start_pixels_y'], meteor_info['image_location']['end_pixels']['end_pixels_y'])

    plt.plot(start, end, linestyle='-', linewidth=3, color='g')


def highlight_additional_info(plt, meteor_info):
    """add the legend"""

    legend_elements = [Patch(facecolor='white', edgecolor='w',
                             label='Start Point Ra Dec:{}, {}'
                             .format(format(meteor_info['coordinates']['start_point']['start_point_ra'], '.2f'),
                                     format(meteor_info['coordinates']['start_point']['start_point_dec'], '.2f'))),

                       Patch(facecolor='white', edgecolor='w',
                             label='End Point Ra Dec:{}, {}'
                             .format(format(meteor_info['coordinates']['end_point']['end_point_ra'], '.2f'),
                                     format(meteor_info['coordinates']['end_point']['end_point_dec'], '.2f'))),

                       Patch(facecolor='white', edgecolor='w',
                             label='Angular distance:{}'.format(format(meteor_info['angular_distance'], '.2f'))),

                       Patch(facecolor='white', edgecolor='w',
                             label='Magnitude:{}'.format(format(meteor_info['magnitude'], '.2f'))),

                       Patch(facecolor='white', edgecolor='w',
                             label='Meteor Shower:{}'.format(meteor_info['meteor_shower']))
                       ]

    plt.legend(["1", "2", "3"], handles=legend_elements,loc='upper right', bbox_to_anchor=(0, 0.5))


def highlight_stars(plot, visible_stars):
    """Find the stars in the image and highlight them in the final picture"""

    circles = [plot.Circle((star.x, star.y), 5, fill=False, color="r") for star in visible_stars]

    ax = plt.gcf().gca()

    for circle in circles:
        ax.add_artist(circle)


def highlight_lines(plot, visible_lines):
    """add the constellation lines"""
    for line in visible_lines:
        line1 = [line.x1, line.x2]
        line2 = [line.y1, line.y2]
        plot.plot(line1, line2, linestyle='-', linewidth=1.5, color='r')


def highlight_names(plot, const_names):
    """add the constellation names"""
    for name in const_names:
        plot.text(name.x, name.y, name.name)


def highlight_bounds(plot, const_bounds):
    """add the constellation bounds"""
    for c in const_bounds:

        try:
            if len(c.lines) != 0:
                for line in c.lines:
                    plot.plot([line.x1, line.x2], [line.y1, line.y2], linestyle="--", linewidth=2, color="y")
        except IndexError:
            continue
