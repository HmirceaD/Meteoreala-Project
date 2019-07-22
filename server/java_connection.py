import os
import sys
from subprocess import Popen
from platform import system
from psutil import process_iter
from signal import SIGTERM

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def start_java_gateway(config_file):
    """starts the java gateway server with the correct script depending on the os"""
    check_port(config_file)

    os.chdir(os.path.join(ROOT_DIR, 'Stacker'))

    if system() == "Windows":
        Popen("start_stacker.bat", executable=os.path.join(ROOT_DIR, 'Stacker', "start_stacker.bat"))
        os.chdir(os.path.join(".."))
    elif system() == "Linux" or system() == "Darwin":

        Popen("start_stacker.sh", executable=os.path.join(ROOT_DIR, 'Stacker', "start_stacker.sh"))
        os.chdir(os.path.join(".."))
    else:

        print("I don't know what operating system this is")
        sys.exit(1)


def check_port(config_file):
    """checks if the java gateway server port is in use and if it is it kill it"""
    for proc in process_iter():
        for conns in proc.connections(kind='inet'):
            if conns.laddr.port == int(config_file['JAVA_SERVER']['java_gateway_port']):
                proc.send_signal(SIGTERM)
                continue
