from programmingtheiot.data.SensorData import SensorData
import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.cda.sim.BaseSensorSimTask import BaseSensorSimTask
from pisense import SenseHAT

class HumiditySensorEmulatorTask(BaseSensorSimTask):
    """
    Shell representation of class for student implementation.
    """

    def __init__(self, dataSet=None):
        super(HumiditySensorEmulatorTask, self).__init__(
            name=ConfigConst.HUMIDITY_SENSOR_NAME,
            typeID=ConfigConst.HUMIDITY_SENSOR_TYPE
        )
        
        enableEmulation = ConfigUtil().getBoolean(
            ConfigConst.CONSTRAINED_DEVICE, ConfigConst.ENABLE_EMULATOR_KEY
        )
        
        self.sh = SenseHAT(emulate=enableEmulation)

    def generateTelemetry(self) -> SensorData:
    # Access the attributes directly instead of using getName() and getTypeID()
        sensorData = SensorData(name=self.name, typeID=self.typeID)
        sensorVal = self.sh.environ.humidity
        
        sensorData.setValue(sensorVal)
        self.latestSensorData = sensorData
        
        return sensorData
