from py4j.java_gateway import JavaGateway
from py4j.java_gateway import GatewayParameters
import sys
import logging
from meteoreala.fits_image import FitsImage


class ImageStacker:
    """
    'Bridge' between python and java image stacker
    """

    def __init__(self, config_file):
        """
        initialise the gateway to the java image stacker
        """
        gateway = JavaGateway(gateway_parameters=GatewayParameters(auto_convert=True))
        self.java_image_stacker = gateway.entry_point.getImageStacker()

        self.config_parse = config_file

    def convert_from_paths(self, paths):
        """
        Take paths of fits images and send them to the
        java image stacker to process into one image
        """

        image_path = self.java_image_stacker.stackImageFromPaths(paths,
                                                                 self.config_parse["GENERAL"]["fitsimagepaths"],
                                                                 int(self.config_parse["PERFORMANCE"]["numberofcores"]))

        if image_path is not None:
            return FitsImage(image_path=image_path)
        else:
            logging.error("Stack of images couldn't be saved to disk")
            sys.exit(3)
