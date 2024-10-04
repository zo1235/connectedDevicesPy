#####
# 
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
# 
# You may find it more helpful to your design to adjust the
# functionality, constants and interfaces (if there are any)
# provided within in order to meet the needs of your specific
# Programming the Internet of Things project.
# 

import logging
import time
from programmingtheiot.cda.system.SystemPerformanceManager import SystemPerformanceManager
from time import sleep

logging.basicConfig(format='%(asctime)s:%(name)s:%(levelname)s:%(message)s', level=logging.DEBUG)

class ConstrainedDeviceApp:
    """
    Definition of the ConstrainedDeviceApp class.
    """

    def __init__(self):
        """
        Initialization of class.
        """
        logging.info("Initializing CDA...")
        self.sysPerfManager = SystemPerformanceManager()
        
        # TODO: Load configuration logic here

    def startApp(self):
        """
        Start the CDA. Calls startManager() on the SystemPerformanceManager instance.
        """
        logging.info("Starting CDA...")
        self.sysPerfManager.startManager()
        logging.info("CDA started.")

    def stopApp(self, code: int):
        """
        Stop the CDA. Calls stopManager() on the device data manager instance.
        """
        logging.info("CDA stopping...")
        self.sysPerfManager.stopManager()
        logging.info("CDA stopped with exit code %s.", str(code))
        
    def parseArgs(self, args):
        """
        Parse command line args.
        """
        logging.info("Parsing command line args...")

def main():
    """
    Main function definition for running client as application.
    Current implementation runs for 65 seconds then exits.
    """
    cda = ConstrainedDeviceApp()
    cda.startApp()
    
    # Run for 65 seconds - this can be changed as needed
    sleep(65)
    
    # Optionally stop the app - this can be removed if needed
    cda.stopApp(0)

if __name__ == '__main__':
    """
    Attribute definition for when invoking as app via command line
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
    main()
