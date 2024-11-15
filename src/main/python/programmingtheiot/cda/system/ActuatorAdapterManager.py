import logging

from programmingtheiot.common.ConfigUtil import ConfigUtil
import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.data.ActuatorData import ActuatorData

from programmingtheiot.cda.sim.HvacActuatorSimTask import HvacActuatorSimTask
from programmingtheiot.cda.sim.HumidifierActuatorSimTask import HumidifierActuatorSimTask


class ActuatorAdapterManager(object):
    """
    Shell representation of the class for student implementation.
    """

    def __init__(self, dataMsgListener=None):
        self.dataMsgListener = dataMsgListener

        # Retrieve configuration values
        self.configUtil = ConfigUtil()
        self.useSimulator = self.configUtil.getBoolean(
            section=ConfigConst.CONSTRAINED_DEVICE, key=ConfigConst.ENABLE_SIMULATOR_KEY
        )
        self.useEmulator = self.configUtil.getBoolean(
            section=ConfigConst.CONSTRAINED_DEVICE, key=ConfigConst.ENABLE_EMULATOR_KEY
        )
        self.deviceID = self.configUtil.getProperty(
            section=ConfigConst.CONSTRAINED_DEVICE, key=ConfigConst.DEVICE_LOCATION_ID_KEY, defaultVal=ConfigConst.NOT_SET
        )
        self.locationID = self.configUtil.getProperty(
            section=ConfigConst.CONSTRAINED_DEVICE, key=ConfigConst.DEVICE_LOCATION_ID_KEY, defaultVal=ConfigConst.NOT_SET
        )

        # Initialize actuators
        self.humidifierActuator = None
        self.hvacActuator = None
        self.ledDisplayActuator = None

        # Log if using emulator or simulator
        if self.useSimulator:
            logging.info("Using simulators for actuator management.")
        else:
            logging.info("Using emulators for actuator management.")

        # Initialize environmental actuation tasks
        self._initEnvironmentalActuationTasks()

    def _initEnvironmentalActuationTasks(self):
        if self.useSimulator:
            # Load the environmental tasks for simulated actuation
            self.humidifierActuator = HumidifierActuatorSimTask()
            # Create the HVAC actuator
            self.hvacActuator = HvacActuatorSimTask()
        else:
            logging.info("Using emulators. No simulation tasks initialized.")

    def sendActuatorCommand(self, data: ActuatorData) -> ActuatorData:
        if data and not data.isResponseFlagEnabled():
            # First check if the actuation event is destined for this device
            if data.getLocationID() == self.locationID:
                logging.info("Actuator command received for location ID %s. Processing...", str(data.getLocationID()))

                aType = data.getTypeID()
                responseData = None

                # Handle the appropriate actuator type
                if aType == ConfigConst.HUMIDIFIER_ACTUATOR_TYPE and self.humidifierActuator:
                    responseData = self.humidifierActuator.updateActuator(data)
                elif aType == ConfigConst.HVAC_ACTUATOR_TYPE and self.hvacActuator:
                    responseData = self.hvacActuator.updateActuator(data)
                else:
                    logging.warning("No valid actuator type. Ignoring actuation for type: %s", data.getTypeID())

                # Return response data (will be used in a later lab)
                return responseData
            else:
                logging.warning("Location ID doesn't match. Ignoring actuation: (me) %s != (you) %s", str(self.locationID), str(data.getLocationID()))
        else:
            logging.warning("Actuator request received. Message is empty or a response. Ignoring.")

        return None

    def setDataMessageListener(self, listener) -> bool:
        if listener:
            self.dataMsgListener = listener
            logging.info("DataMessageListener set successfully.")
            return True
        else:
            logging.warning("Invalid DataMessageListener provided. Listener not set.")
            return False
