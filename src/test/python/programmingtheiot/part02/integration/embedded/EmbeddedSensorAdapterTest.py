import logging
import unittest
from time import sleep
from programmingtheiot.cda.system.SensorAdapterManager import SensorAdapterManager
from programmingtheiot.common.DefaultDataMessageListener import DefaultDataMessageListener

class EmbeddedSensorAdapterTest(unittest.TestCase):
    """
    This test case class contains unit tests for the SensorAdapterManager
    that uses the I2C sensor adapter tasks.
    
    NOTE: Ensure that the necessary hardware or emulator is available 
    for the test to run correctly.
    """

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(format='%(asctime)s:%(module)s:%(levelname)s:%(message)s', level=logging.DEBUG)
        logging.info("Testing SensorAdapterManager class [using I2C sensors]...")
        
        cls.defaultMsgListener = DefaultDataMessageListener()
        cls.sensorAdapterMgr = SensorAdapterManager()
        cls.sensorAdapterMgr.setDataMessageListener(cls.defaultMsgListener)

    def setUp(self):
        # Any setup before each test can go here
        pass

    def tearDown(self):
        # Clean up after each test can go here
        pass

    def testRunAllSensors(self):
        """Test running all sensors for a short duration."""
        self.sensorAdapterMgr.startManager()
        
        # Allow some time for the sensors to generate telemetry
        sleep(20)
        
        self.sensorAdapterMgr.stopManager()

if __name__ == "__main__":
    unittest.main()
