#####
# 
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
# 
# Copyright (c) 2020 by Andrew D. King
# 

import logging
import aiocoap
from aiocoap import Code
from aiocoap.resource import Resource

from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.data.DataUtil import DataUtil
from programmingtheiot.data.ActuatorData import ActuatorData

class UpdateActuatorResourceHandler(Resource):
    def __init__(self, dataMsgListener: IDataMessageListener = None):
        self.dataMsgListener = dataMsgListener
        self.dataUtil = DataUtil()
        logging.info("UpdateActuatorResourceHandler initialized")

    async def render_put(self, request):
        try:
            logging.info(f"PUT request received with payload: {request.payload.decode()}")
            
            # Validate and convert payload to ActuatorData
            actuatorCmdData = self.dataUtil.jsonToActuatorData(request.payload)
            
            # Create and return response
            return self._createResponse(actuatorCmdData)
        except Exception as e:
            logging.warning(f"Failed to validate and convert actuator command: {e}")
            return aiocoap.Message(code=Code.NOT_ACCEPTABLE)

    def _createResponse(self, data: ActuatorData = None):
        responseCode = Code.CHANGED
        
        # Process actuator command
        actuatorResponseData = self.dataMsgListener.handleActuatorCommandMessage(data)
        
        if not actuatorResponseData:
            actuatorResponseData = ActuatorData()
            actuatorResponseData.updateData(data)
            actuatorResponseData.setAsResponse()
            actuatorResponseData.setStatusCode(-1)
            
            responseCode = Code.PRECONDITION_FAILED
        
        jsonData = self.dataUtil.actuatorDataToJson(actuatorResponseData)
        return aiocoap.Message(code=responseCode, payload=jsonData.encode('ascii'))
       
		