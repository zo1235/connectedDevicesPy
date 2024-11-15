import logging
import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.data.DataUtil import DataUtil
from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData
from programmingtheiot.common.ISystemPerformanceDataListener import ISystemPerformanceDataListener
from coapthon.resources.resource import Resource
from coapthon import defines

class GetSystemPerformanceResourceHandler(Resource, ISystemPerformanceDataListener):
    def __init__(self, name: str = ConfigConst.SYSTEM_PERF_MSG, coap_server=None):
        super(GetSystemPerformanceResourceHandler, self).__init__(
            name, coap_server, visible=True, observable=True, allow_children=True
        )

        # Configuration settings
        self.pollCycles = ConfigUtil().getInteger(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.POLL_CYCLES_KEY,
            defaultVal=ConfigConst.DEFAULT_POLL_CYCLES
        )
        self.sysPerfData = None  # Will hold the latest system performance data
        self.dataUtil = DataUtil()

        # For testing purposes
        self.payload = "GetSysPerfData"
        logging.info("GetSystemPerformanceResourceHandler initialized")

    def render_GET_advanced(self, request, response):
        if request:
            response.code = defines.Codes.CONTENT.number

            if not self.sysPerfData:
                response.code = defines.Codes.EMPTY.number
                self.sysPerfData = SystemPerformanceData()  # Retrieve the latest data

            # Convert system performance data to JSON
            jsonData = DataUtil().systemPerformanceDataToJson(self.sysPerfData)

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

    def onSystemPerformanceDataUpdate(self, data: SystemPerformanceData) -> bool:
        """
        This method will be called to update the system performance data.
        It will notify the CoAP framework that the resource has been updated.
        """
        logging.info("SystemPerformanceData update received")
        self.sysPerfData = data
        self.changed = True
        self.updated()  # Notify the CoAP framework that the resource has been updated
        return True
