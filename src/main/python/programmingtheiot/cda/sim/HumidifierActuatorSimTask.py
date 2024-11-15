#####
# 
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
# 
# Copyright (c) 2020 by Andrew D. King
# 
import programmingtheiot.common.ConfigConst as ConfigConst
import logging
from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.cda.sim.BaseActuatorSimTask import BaseActuatorSimTask

class HumidifierActuatorSimTask(BaseActuatorSimTask):
    """
    This is a simple wrapper for an Actuator abstraction - it provides
    a container for the actuator's state, value, name, and status. A
    command variable is also provided to instruct the actuator to
    perform a specific function (in addition to setting a new value
    via the 'val' parameter.
    """
    def updateActuator(self, data: ActuatorData):
        command = data.getCommand()
        if command == 1:  # ON
            logging.info("Emulating HUMIDIFIER actuator ON: \n*******\n* O N *\n*******")
            logging.info("HUMIDIFIER VALUE -> 50.0")
            return data  # Return appropriate response
        elif command == 0:  # OFF
            logging.info("Emulating HUMIDIFIER actuator OFF: \n*******\n* OFF *\n*******")
            return data  # Return appropriate response

    def __init__(self):
        super(HumidifierActuatorSimTask, self).__init__(
            name=ConfigConst.HUMIDIFIER_ACTUATOR_NAME,
            typeID=ConfigConst.HUMIDIFIER_ACTUATOR_TYPE,
            simpleName="HUMIDIFIER"
        )
