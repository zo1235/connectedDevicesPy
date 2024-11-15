# RedisClientAdapterTest.py
import unittest
from programmingtheiot.cda.connection.RedisPersistenceAdapter import RedisPersistenceAdapter
from programmingtheiot.data.SensorData import SensorData  # Ensure this path is correct
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum  # Ensure this path is correct

class RedisClientAdapterTest(unittest.TestCase):

    def setUp(self):
        """Set up the test case, run before every test."""
        self.adapter = RedisPersistenceAdapter()
        self.adapter.connectClient()  # Ensure the client is connected before each test

    def tearDown(self):
        """Clean up after each test."""
        self.adapter.disconnectClient()  # Disconnect after each test

    def testConnectClient(self):
        """Test connecting to Redis."""
        result = self.adapter.connectClient()
        self.assertTrue(result, "Should successfully connect to Redis.")

    def testDisconnectClient(self):
        """Test disconnecting from Redis."""
        self.adapter.connectClient()  # Make sure it's connected before disconnecting
        result = self.adapter.disconnectClient()
        self.assertTrue(result, "Should successfully disconnect from Redis.")

    def testStoreSensorData(self):
        """Test storing sensor data."""
        resource = ResourceNameEnum.SENSOR_TYPE  # Replace with actual enum value
        data = SensorData()  # Create a new SensorData object with necessary attributes
        data.value = 42  # Replace with your actual data attributes

        result = self.adapter.storeData(resource, data)
        self.assertTrue(result, "Should successfully store sensor data.")

if __name__ == '__main__':
    unittest.main()
