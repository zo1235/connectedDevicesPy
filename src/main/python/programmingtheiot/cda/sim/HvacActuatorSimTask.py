#####
# 
# This class is part of the Programming the Internet of Things project.
# 
# It is provided as a simple shell to guide the student and assist with
# implementation for the Programming the Internet of Things exercises,
# and designed to be modified by the student as needed.
#
import programmingtheiot.common.ConfigConst as ConfigConst
import logging
import random

from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.cda.sim.BaseActuatorSimTask import BaseActuatorSimTask

class HvacActuatorSimTask(BaseActuatorSimTask):
    def updateActuator(self, data: ActuatorData):
        command = data.getCommand()
        if command == 1:  # ON
            logging.info("Emulating HVAC actuator ON: \n*******\n* O N *\n*******")
            logging.info("HVAC VALUE -> 22.5")
            return data  # Return appropriate response
        elif command == 0:  # OFF
            logging.info("Emulating HVAC actuator OFF: \n*******\n* OFF *\n*******")
            return data  # Return appropriate response

    def __init__(self):
        super(HvacActuatorSimTask, self).__init__(
            name=ConfigConst.HVAC_ACTUATOR_NAME,
            typeID=ConfigConst.HVAC_ACTUATOR_TYPE,
            simpleName="HVAC"
        )