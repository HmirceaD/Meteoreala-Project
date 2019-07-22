# Description

Meteoreala is a project that contains a server running on an ip address and port bound to your computer,
it takes fits files, stacks them and checks them resulting image for meteor trails,
it then analysis the meteors and saves the result in a db

# How to use it

1. If you do not have the 'pip' package installer for Python then install it (https://pip.pypa.io/en/stable/installing/)
2. Run one of the deployment scripts (windows_deploy.bat for windows users and linux_deploy.sh for linux),
this will install the project and any prerequisite python libraries
3. An instance of a mongodb database, if you don't have mongodb installed you can download it here:
    - windows: https://docs.mongodb.com/v3.2/tutorial/install-mongodb-on-windows/
    - linux: https://docs.mongodb.com/v3.2/administration/install-on-linux/
   by default, the db will be bound to localhost on your computer and port 27017
4. The project will create a config.ini folder, this file should remain at the base level of the project,
   if you want to change anything in it
   then you should read first what each values in the config file does
5. Start the project by running 'meteoreala_server' in your terminal
6. The server will start running, it will check a folder that you chose on your computer to take the images from cameras and start
   the analysis process, you should have a constant supply of images to those folders (by default the server checks every 10 seconds),
   you can do this by having a script that moves the files into that folder constantly (the fits files get removed after they have been read).
7. You can connect to a rest api by connecting through the browser to the ip and port the server is bound to. There you can see all of
   the analysed images and more information on the meteors

# Config Values

**All values in the config file have to be filled in for the server to start, if you want to modify values start the server first**
**If you deleted some values in the file and do not know what to add instead you can do 'reset_config' in your terminal and a default config.ini will be created**

These are the all of the values in the config.ini file and what they do:
- GENERAL tab:  * fitsimagepaths: the path to the folder where the plots of the images with stars, constellations and the meteor will be highlited
                * fitsfilepaths: the path to the folder where resulting (stacked) fits files will be saved
                * imagefilepaths: the path to the folder where the images will be supplied, here the server checks for the .fits images,
                                  this will be filled in with folders with the same name as the location names attributes in the CAMERAS tab, by the server.

- IMAGES tab:   * imagewidth: the width of the fits image
                * imageheight: the height of the fits image

- PERFORMANCE tab:   * numberofcores: the number of cores the program will use in the image stacking process (if you have a regular 8 core processor it is recommended you use a value between 2 and 5)

- SERVER tab:   * server_ip: the ip to which the server will be bound to
                * port: the port to which the server will be bound to

- JAVA_SERVER tab:   * java_gateway_port: the port to the gateway server through which the server and the stacking algorithm communicate, it is recommended you leave the default value of 25333

- MONGODB tab:   * mongo_ip: the ip to which the mongodb database will be bound to
                 * mongo_port: the port to which the mongodb database will be bound to

- METEOR_DETECTION tab:   * these values are used in detecting the meteor tail in the image, in general, the lower these values, the more sensitive the detection algorithm will be to detect meteors,
                            lowering it too much might mean more false positives detected, increasing it too much might mean some smaller meteors will not be detected
                          * HOUGH_LINES_MIN_LINE_LENGTH: the minimal amount of straight, white pixels needed to be considered a meteor tail (aprox. range: 20 - 200)
                          * HOUGH_LINES_MAX_LINE_GAP: the maximal amount of non-white pixels between points in a potential line, for it to be considered a line (aprox. range: 20 - 200)
                          * HOUGH_LINES_THRESHOLD: don't really understand what this does, and opencv's documentation doesn't really explain it, probably best to leave it between 15 and 150
                          * METEOR_SHOWER_ACCURACY: the degree to how close the meteor will come to a meteor shower, for it to be considered it's origin meteor shower (aprox. around 5)

- CAMERAS tab:   * location_names: the names of the locations where the fits images where taken, these will be the names the of the folders the server will create in the imagefilepaths folder
                 * analysis_check: how often (in seconds) the server checks the folders for fits files
                 * error_lines_hour: the hour (from 0-23) the server will create an entry of the incorrect lines detected from different the locations
                 * error_lines_minutes: the minute (from 0-59) [...]