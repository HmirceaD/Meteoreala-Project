from setuptools import setup, find_packages

setup(name="meteoreala",
      version='0.1',
      description="Meteor detection",
      url='https://HmirceaD@bitbucket.org/HmirceaD/meteoreala.git',
      author='Mircea Dan',
      install_requires=['flask', 'jinja2', 'py4j', 'astropy', 'matplotlib', 'psutil', 'pymongo', 'numpy', 'opencv-python'],
      author_email='mircea_dan97@yahoo.com',
      entry_points={
            'console_scripts': [
                  'start_meteoreala = server.meteoreala_server:start_server',
                  'reset_config = helper.create_config:init_config',

            ]},
      packages=find_packages())
