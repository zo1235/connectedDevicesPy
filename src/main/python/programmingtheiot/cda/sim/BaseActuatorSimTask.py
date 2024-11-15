import logging
import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.data.ActuatorData import ActuatorData

class BaseActuatorSimTask:
    """
    Shell representation of class for student implementation.
    """

    def __init__(self, name: str = ConfigConst.NOT_SET, 
                 typeID: int = ConfigConst.DEFAULT_ACTUATOR_TYPE, 
                 simpleName: str = "Actuator"):
        # Initialize actuator response
        self.latestActuatorResponse = ActuatorData(typeID=typeID, name=name)
        self.latestActuatorResponse.setAsResponse()

        # Set class-scoped variables
        self.name = name
        self.typeID = typeID
        self.simpleName = simpleName
        self.lastKnownCommand = ConfigConst.DEFAULT_COMMAND
        self.lastKnownValue = ConfigConst.DEFAULT_VAL

    def getLatestActuatorResponse(self) -> ActuatorData:
        """
        Returns the current ActuatorData response instance.
        """
        return self.latestActuatorResponse

    def getSimpleName(self) -> str:
        """
        Returns the simple name of the actuator.
        """
        return self.simpleName

    def updateActuator(self, data: ActuatorData) -> ActuatorData:
        """
        Processes commands to update the actuator state.
        """
        if data and self.typeID == data.getTypeID():
            statusCode = ConfigConst.DEFAULT_STATUS
            curCommand = data.getCommand()
            curVal = data.getValue()

            # Check for command and value repetition
            if curCommand == self.lastKnownCommand and curVal == self.lastKnownValue:
                logging.debug("New actuator command and value is a repeat. Ignoring: %s %s", curCommand, curVal)
            else:
                logging.debug("New actuator command and value to be applied: %s %s", curCommand, curVal)

                if curCommand == ConfigConst.COMMAND_ON:
                    statusCode = self._activateActuator(data.getValue(), data.getStateData())
                elif curCommand == ConfigConst.COMMAND_OFF:
                    statusCode = self._deactivateActuator(data.getValue(), data.getStateData())
                else:
                    logging.warning("ActuatorData command is unknown. Ignoring: %s", curCommand)
                    statusCode = -1

                # Update last known command and value
                self.lastKnownCommand = curCommand
                self.lastKnownValue = curVal

                # Create response
                actuatorResponse = ActuatorData()
                actuatorResponse.updateData(data)
                actuatorResponse.setStatusCode(statusCode)
                actuatorResponse.setAsResponse()

                self.latestActuatorResponse.updateData(actuatorResponse)

                return actuatorResponse

        return None

    def _activateActuator(self, val: float = ConfigConst.DEFAULT_VAL, stateData: str = None) -> int:
        """
        Simulates activating the actuator.
        """
        msg = f"\n*******\n* O N *\n*******\n{self.name} VALUE -> {val}\n======="
        logging.info("Simulating %s actuator ON: %s", self.name, msg)
        return 0

    def _deactivateActuator(self, val: float = ConfigConst.DEFAULT_VAL, stateData: str = None) -> int:
        """
        Simulates deactivating the actuator.
        """
        msg = "\n*******\n* OFF *\n*******"
        logging.info("Simulating %s actuator OFF: %s", self.name, msg)
        return 0
