import logging

from programmingtheiot.cda.connection.CoapClientConnector import CoapClientConnector
from programmingtheiot.cda.connection.MqttClientConnector import MqttClientConnector
from programmingtheiot.cda.system.ActuatorAdapterManager import ActuatorAdapterManager
from programmingtheiot.cda.system.SensorAdapterManager import SensorAdapterManager
from programmingtheiot.cda.system.SystemPerformanceManager import SystemPerformanceManager

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum

from programmingtheiot.data.DataUtil import DataUtil
from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData
from programmingtheiot.cda.connection.CoapServerAdapter import CoapServerAdapter

class ISystemPerformanceDataListener:
    def handleSystemPerformanceMessage(self, data):
        pass

class ITelemetryDataListener:
    def handleTelemetryData(self, data):
        pass

class DeviceDataManager(IDataMessageListener):
    def __init__(self):
        self.configUtil = ConfigUtil()
        self.enableSystemPerf = self.configUtil.getBoolean(section=ConfigConst.CONSTRAINED_DEVICE, key=ConfigConst.ENABLE_SYSTEM_PERF_KEY)
        self.enableSensing = self.configUtil.getBoolean(section=ConfigConst.CONSTRAINED_DEVICE, key=ConfigConst.ENABLE_SENSING_KEY)
        self.enableActuation = True  # For local testing
        
        self.sysPerfMgr = SystemPerformanceManager() if self.enableSystemPerf else None
        self.sensorAdapterMgr = SensorAdapterManager() if self.enableSensing else None
        self.actuatorAdapterMgr = ActuatorAdapterManager(dataMsgListener=self) if self.enableActuation else None

        if self.sysPerfMgr:
            self.sysPerfMgr.setDataMessageListener(self)
            logging.info("Local system performance tracking enabled")
        
        if self.sensorAdapterMgr:
            self.sensorAdapterMgr.setDataMessageListener(self)
            logging.info("Local sensor tracking enabled")
        
        if self.actuatorAdapterMgr:
            logging.info("Local actuation capabilities enabled")

        self.handleTempChangeOnDevice = self.configUtil.getBoolean(ConfigConst.CONSTRAINED_DEVICE, ConfigConst.HANDLE_TEMP_CHANGE_ON_DEVICE_KEY)
        self.triggerHvacTempFloor = self.configUtil.getFloat(ConfigConst.CONSTRAINED_DEVICE, ConfigConst.TRIGGER_HVAC_TEMP_FLOOR_KEY)
        self.triggerHvacTempCeiling = self.configUtil.getFloat(ConfigConst.CONSTRAINED_DEVICE, ConfigConst.TRIGGER_HVAC_TEMP_CEILING_KEY)
        
        self.enableMqttClient = self.configUtil.getBoolean(section=ConfigConst.CONSTRAINED_DEVICE, key=ConfigConst.ENABLE_MQTT_CLIENT_KEY)
        
        self.mqttClient = None
        if self.enableMqttClient:
            self.mqttClient = MqttClientConnector()
            self.mqttClient.setDataMessageListener(self)
            
        self.enableCoapClient = \
        self.configUtil.getBoolean( \
            section = ConfigConst.CONSTRAINED_DEVICE, key = ConfigConst.ENABLE_COAP_CLIENT_KEY)
        if self.enableCoapClient :
            self.coapClient = CoapClientConnector(dataMsgListener = self)    
        self.configUtil = ConfigUtil()

        # Enable or disable the CoAP server based on config
        self.enableCoapServer = self.configUtil.getBoolean(ConfigConst.CONSTRAINED_DEVICE, ConfigConst.ENABLE_COAP_SERVER_KEY)

        if self.enableCoapServer:
            self.coapServer = CoapServerAdapter(dataMsgListener=self)
            

    def getLatestActuatorDataResponseFromCache(self, name: str = None) -> ActuatorData:
        # Implement caching logic here
        return None
        
    def getLatestSensorDataFromCache(self, name: str = None) -> SensorData:
        # Implement caching logic here
        return None
    
    def getLatestSystemPerformanceDataFromCache(self, name: str = None) -> SystemPerformanceData:
        # Implement caching logic here
        return None
    
    def handleActuatorCommandMessage(self, data: ActuatorData) -> ActuatorData:
        if data is not None:
            logging.info("Processing actuator command message: %s", data)
            return self.actuatorAdapterMgr.sendActuatorCommand(data)
        else:
            logging.warning("Incoming actuator command is invalid (null). Ignoring.")
            return None
        if data:
            logging.info("Processing actuator command message.")
        
        # TODO: add further validation before sending the command
            return self.actuatorAdapterMgr.sendActuatorCommand(data)
        else:
            logging.warning("Received invalid ActuatorData command message. Ignoring.")
            return None
    
    def handleActuatorCommandResponse(self, data: ActuatorData = None) -> bool:
        if data:
            logging.debug("Actuator response received: %s", data)
            actuatorMsg = DataUtil().actuatorDataToJson(data)
            resourceName = ResourceNameEnum.CDA_ACTUATOR_RESPONSE_RESOURCE
            self._handleUpstreamTransmission(resource=resourceName, msg=actuatorMsg)
            return True
        else:
            logging.warning("Incoming actuator response is invalid (null). Ignoring.")
            return False
    
    def handleIncomingMessage(self, resourceEnum: ResourceNameEnum, msg: str) -> bool:
        logging.info("Incoming message: %s", msg)
        return True
    
    def handleSensorMessage(self, data: SensorData = None) -> bool:
        if data:
            logging.debug("Incoming sensor data received: %s", data)
            self._handleSensorDataAnalysis(data)
            return True
        else:
            logging.warning("Incoming sensor data is invalid (null). Ignoring.")
            return False
        if data:
            logging.info("Incoming sensor data received (from sensor manager): " + str(data))
            
            # Optionally handle analytics
            self._handleSensorDataAnalysis(data)
            
            # Convert `SensorData` to JSON
            jsonData = DataUtil().sensorDataToJson(data=data)
            
            # Send to GDA using the appropriate protocol
            self._handleUpstreamTransmission(resource=ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE, msg=jsonData)
            
            return True
        else:
            logging.warning("Incoming sensor data is invalid (null). Ignoring.")
            return False

    
    def handleSystemPerformanceMessage(self, data: SystemPerformanceData = None) -> bool:
        if data:
            logging.debug("Incoming system performance message received: %s", data)
            return True
        else:
            logging.warning("Incoming system performance data is invalid (null). Ignoring.")
            return False
        if data:
            logging.info("Incoming system performance data received: " + str(data))
            
            # Convert `SystemPerformanceData` to JSON
            jsonData = DataUtil().systemPerformanceDataToJson(data=data)
            
            # Send to GDA using the appropriate protocol
            self._handleUpstreamTransmission(resource=ResourceNameEnum.CDA_SYSTEM_PERF_MSG_RESOURCE, msg=jsonData)
            
            return True
        else:
            logging.warning("Incoming system performance data is invalid (null). Ignoring.")
            return False
    
    def setSystemPerformanceDataListener(self, listener: ISystemPerformanceDataListener = None):
        pass
            
    def setTelemetryDataListener(self, name: str = None, listener: ITelemetryDataListener = None):
        pass
            
    def startManager(self):
        logging.info("Starting DeviceDataManager...")
        if self.sysPerfMgr:
            self.sysPerfMgr.startManager()
        if self.sensorAdapterMgr:
            self.sensorAdapterMgr.startManager()
        logging.info("Started DeviceDataManager.")
        
        if self.mqttClient:
            self.mqttClient.connectClient()
            self.mqttClient.subscribeToTopic(ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE, callback=None, qos=ConfigConst.DEFAULT_QOS)
        if self.coapServer:
            self.coapServer.startServer()   
    def stopManager(self):
        logging.info("Stopping DeviceDataManager...")
        if self.sysPerfMgr:
            self.sysPerfMgr.stopManager()
        if self.sensorAdapterMgr:
            self.sensorAdapterMgr.stopManager()
        logging.info("Stopped DeviceDataManager.")
        
        if self.mqttClient:
            self.mqttClient.unsubscribeFromTopic(ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE)
            self.mqttClient.disconnectClient()
        if self.coapServer:
            self.coapServer.stopServer()
    def _handleIncomingDataAnalysis(self, msg: str):
        pass
        
    def _handleSensorDataAnalysis(self, data: SensorData = None):
        if self.handleTempChangeOnDevice and data and data.getTypeID() == ConfigConst.TEMP_SENSOR_TYPE:
            logging.info("Handling temperature change: %s - type ID: %s", self.handleTempChangeOnDevice, data.getTypeID())
            ad = ActuatorData(typeID=ConfigConst.HVAC_ACTUATOR_TYPE)
            if data.getValue() > self.triggerHvacTempCeiling:
                ad.setCommand(ConfigConst.COMMAND_ON)
                ad.setValue(self.triggerHvacTempCeiling)
            elif data.getValue() < self.triggerHvacTempFloor:
                ad.setCommand(ConfigConst.COMMAND_ON)
                ad.setValue(self.triggerHvacTempFloor)
            else:
                ad.setCommand(ConfigConst.COMMAND_OFF)
            self.handleActuatorCommandMessage(ad)
        
    def _handleUpstreamTransmission(self, resource: ResourceNameEnum = None, msg: str = None):
        logging.info("Upstream transmission invoked. Checking communication's integration.")
        
        # Use MQTT if enabled
        if self.mqttClient:
            if self.mqttClient.publishMessage(resource=resource, msg=msg):
                logging.debug("Published incoming data to resource (MQTT): %s", str(resource))
            else:
                logging.warning("Failed to publish incoming data to resource (MQTT): %s", str(resource))
        
        # Use CoAP if enabled
        if self.coapClient:
            if self.coapClient.sendPutRequest(resource=resource, payload=msg):
                logging.debug("Put incoming message data to resource (CoAP): %s", str(resource))
            else:
                logging.warning("Failed to put incoming message data to resource (CoAP): %s", str(resource))

