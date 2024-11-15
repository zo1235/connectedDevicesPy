'''
Created on Oct 16, 2024

@author: zohera
'''


# RedisPersistenceAdapter.py
import redis
import logging
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum

DATA_GATEWAY_SERVICE = 'Data.GatewayService'

class RedisPersistenceAdapter:
    def __init__(self):
        # Retrieve host and port from configuration
        config = ConfigUtil.getConfig(DATA_GATEWAY_SERVICE)
        self.host = config.get('host')
        self.port = config.get('port')
        self.redis_client = None
        self.is_connected = False
        logging.info("Initialized RedisPersistenceAdapter.")

    def connectClient(self) -> bool:
        if self.is_connected:
            logging.warning("Already connected to Redis.")
            return True
        try:
            self.redis_client = redis.StrictRedis(host=self.host, port=self.port, decode_responses=True)
            self.redis_client.ping()  # Check connection
            self.is_connected = True
            logging.info("Connected to Redis successfully.")
            return True
        except Exception as e:
            logging.error(f"Failed to connect to Redis: {str(e)}")
            return False

    def disconnectClient(self) -> bool:
        if not self.is_connected:
            logging.warning("Already disconnected from Redis.")
            return True
        try:
            self.redis_client = None
            self.is_connected = False
            logging.info("Disconnected from Redis successfully.")
            return True
        except Exception as e:
            logging.error(f"Failed to disconnect from Redis: {str(e)}")
            return False

    def storeData(self, resource: ResourceNameEnum, data: SensorData) -> bool:
        if not self.is_connected:
            logging.error("Cannot store data, Redis client is not connected.")
            return False

        topic = str(resource)  # Convert enum to string
        try:
            self.redis_client.set(topic, data.to_json())  # Assuming SensorData has a method to convert to JSON
            logging.info(f"Stored data for {topic}.")
            return True
        except Exception as e:
            logging.error(f"Failed to store data for {topic}: {str(e)}")
            return False

