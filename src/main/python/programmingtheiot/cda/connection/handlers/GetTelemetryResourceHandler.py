import logging
import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.data.DataUtil import DataUtil
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.common.ITelemetryDataListener import ITelemetryDataListener
from coapthon.resources.resource import Resource
from coapthon import defines

class GetTelemetryResourceHandler(Resource, ITelemetryDataListener):
    def __init__(self, name: str = ConfigConst.SENSOR_MSG, coap_server=None):
        super(GetTelemetryResourceHandler, self).__init__(
            name, coap_server, visible=True, observable=True, allow_children=True
        )

        # Configuration settings
        self.pollCycles = ConfigUtil().getInteger(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.POLL_CYCLES_KEY,
            defaultVal=ConfigConst.DEFAULT_POLL_CYCLES
        )
        self.sensorData = None  # Will hold the latest sensor data
        self.dataUtil = DataUtil()

        # For testing purposes
        self.payload = "GetSensorData"
        logging.info("GetTelemetryResourceHandler initialized")

    def render_GET_advanced(self, request, response):
        if request:
            response.code = defines.Codes.CONTENT.number

            if not self.sensorData:
                response.code = defines.Codes.EMPTY.number
                self.sensorData = SensorData()  # Retrieve the latest data

            # Convert sensor data to JSON
            jsonData = DataUtil().sensorDataToJson(self.sensorData)

            response.payload = jsonData
            response.max_age = self.pollCycles

            # Optional: Indicate that the resource has changed
            self.changed = False

        return self, response

    def render_PUT(self, request, response):
        logging.info(f"PUT request received with payload: {request.payload.decode()}")
        response.code = defines.Codes.CHANGED.number
        return self, response

    def render_POST(self, request, response):
        logging.info(f"POST request received with payload: {request.payload.decode()}")
        response.code = defines.Codes.CREATED.number
        return self, response

    def render_DELETE(self, request, response):
        logging.info("DELETE request received")
        response.code = defines.Codes.DELETED.number
        return self, response

    def onSensorDataUpdate(self, data: SensorData = None) -> bool:
        """
        This method will be called to update the sensor data.
        It will notify the CoAP framework that the resource has been updated.
        """
        logging.info("SensorData update received")
        self.sensorData = data
        self.changed = True  # Mark the resource as updated
        # No need to call self.updated(), just set self.changed = True
        return True
