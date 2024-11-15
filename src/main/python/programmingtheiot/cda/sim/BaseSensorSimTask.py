import random
import logging  # Import the logging module
import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.data.SensorData import SensorData

class BaseSensorSimTask:
    def __init__(self, name: str, typeID: int, dataSet=None, minVal=0.0, maxVal=100.0):
        self.name = name
        self.typeID = typeID
        self.dataSet = dataSet
        self.dataSetIndex = 0
        self.latestSensorData = None
        self.useRandomizer = dataSet is None
        self.minVal = minVal
        self.maxVal = maxVal

    def generateTelemetry(self) -> SensorData:
        sensorData = SensorData(typeID=self.typeID, name=self.name)
        sensorVal = ConfigConst.DEFAULT_VAL
        
        if self.useRandomizer:
            sensorVal = random.uniform(self.minVal, self.maxVal)
        else:
            sensorVal = self.dataSet.getDataEntry(index=self.dataSetIndex)
            self.dataSetIndex += 1
            
            # Wrap around if the index exceeds the dataset
            if self.dataSetIndex >= self.dataSet.getDataEntryCount():
                self.dataSetIndex = 0
                
        sensorData.setValue(sensorVal)
        self.latestSensorData = sensorData  # Set the latest sensor data
        
        return self.latestSensorData

    def getTelemetryValue(self) -> float:
        if self.latestSensorData is None:
            self.generateTelemetry()
        
        # Ensure that the latestSensorData is valid before accessing its value
        if self.latestSensorData is not None:
            return self.latestSensorData.getValue()
        else:
            logging.error("No sensor data available.")
            return None  # or some default value
