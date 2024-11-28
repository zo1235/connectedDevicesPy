import logging
import paho.mqtt.client as mqttClient
import ssl
import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum
from programmingtheiot.cda.connection.IPubSubClient import IPubSubClient
from programmingtheiot.data.DataUtil import DataUtil  # Added as per instructions

class MqttClientConnector(IPubSubClient):
    """
    Implementation of MQTT client connector.
    """

    def __init__(self, clientID: str = None):
        self.config = ConfigUtil()
        self.dataMsgListener = None  # Added per instructions

        self.host = self.config.getProperty(
            ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.HOST_KEY, ConfigConst.DEFAULT_HOST)

        self.port = self.config.getInteger(
            ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.PORT_KEY, ConfigConst.DEFAULT_MQTT_PORT)

        self.keepAlive = self.config.getInteger(
            ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.KEEP_ALIVE_KEY, ConfigConst.DEFAULT_KEEP_ALIVE)

        self.defaultQos = self.config.getInteger(
            ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.DEFAULT_QOS_KEY, ConfigConst.DEFAULT_QOS)

        self.enableEncryption = self.config.getBoolean(
            ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.ENABLE_CRYPT_KEY)

        self.pemFileName = self.config.getProperty(
            ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.CERT_FILE_KEY)

        self.mqttClient = None

        if not clientID:
            self.clientID = self.config.getProperty(
                ConfigConst.CONSTRAINED_DEVICE, ConfigConst.DEVICE_LOCATION_ID_KEY)
        else:
            self.clientID = clientID

        logging.info(f'MQTT Client ID: {self.clientID}')
        logging.info(f'MQTT Broker Host: {self.host}')
        logging.info(f'MQTT Broker Port: {self.port}')
        logging.info(f'MQTT Keep Alive: {self.keepAlive}')
        logging.info(f'Encryption Enabled: {self.enableEncryption}')

    def setDataMessageListener(self, listener: IDataMessageListener = None):  # Added method
        if listener:
            self.dataMsgListener = listener

    def connectClient(self) -> bool:
        if not self.mqttClient:
            self.mqttClient = mqttClient.Client(client_id=self.clientID, clean_session=True)

            try:
                if self.enableEncryption:
                    logging.info("Enabling TLS encryption...")
                    self.port = self.config.getInteger(
                        ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.SECURE_PORT_KEY, ConfigConst.DEFAULT_MQTT_SECURE_PORT)

                    self.mqttClient.tls_set(
                        self.pemFileName, tls_version=ssl.PROTOCOL_TLS_CLIENT)

            except Exception as e:
                logging.warning(f"Failed to enable TLS encryption. Using unencrypted connection. Error: {e}")

            self.mqttClient.on_connect = self.onConnect
            self.mqttClient.on_disconnect = self.onDisconnect
            self.mqttClient.on_message = self.onMessage
            self.mqttClient.on_publish = self.onPublish
            self.mqttClient.on_subscribe = self.onSubscribe

        if not self.mqttClient.is_connected():
            logging.info(f'MQTT client connecting to broker at host: {self.host}')
            self.mqttClient.connect(self.host, self.port, self.keepAlive)
            self.mqttClient.loop_start()
            return True
        else:
            logging.warning('MQTT client is already connected. Ignoring connect request.')
            return False

    def disconnectClient(self) -> bool:
        if self.mqttClient.is_connected():
            logging.info('Disconnecting MQTT client from broker.')
            self.mqttClient.loop_stop()
            self.mqttClient.disconnect()
            return True
        else:
            logging.warning('MQTT client already disconnected.')
            return False

    def onConnect(self, client, userdata, flags, rc):  # Updated
        logging.info('[Callback] Connected to MQTT broker. Result code: ' + str(rc))
        
        # Subscribing to actuator command topic
        self.mqttClient.subscribe(
            topic=ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE.value, qos=self.defaultQos)
        
        # Adding specific callback
        self.mqttClient.message_callback_add(
            sub=ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE.value,
            callback=self.onActuatorCommandMessage
        )

    def onDisconnect(self, client, userdata, rc):
        logging.info('MQTT client disconnected.')

    def onMessage(self, client, userdata, msg):
        payload = msg.payload
        if payload:
            logging.info(f'MQTT message received with payload: {payload.decode("utf-8")}')
        else:
            logging.info('MQTT message received with no payload.')

    def onPublish(self, client, userdata, mid):
        logging.info('MQTT message published.')

    def onSubscribe(self, client, userdata, mid, granted_qos):
        logging.info('MQTT subscription granted.')

    def onActuatorCommandMessage(self, client, userdata, msg):  # Added method
        logging.info('[Callback] Actuator command message received. Topic: %s.', msg.topic)
        
        if self.dataMsgListener:
            try:
                # Convert incoming payload to ActuatorData
                actuatorData = DataUtil().jsonToActuatorData(msg.payload.decode('utf-8'))
                self.dataMsgListener.handleActuatorCommandMessage(actuatorData)
            except:
                logging.exception("Failed to convert incoming actuation command payload to ActuatorData: ")

    def publishMessage(self, resource: ResourceNameEnum = None, msg: str = None, qos: int = ConfigConst.DEFAULT_QOS) -> bool:  # Updated
        if not resource:
            logging.warning('No topic specified. Cannot publish message.')
            return False

        if not msg:
            logging.warning(f'No message specified. Cannot publish message to topic: {resource.value}')
            return False

        if qos < 0 or qos > 2:
            qos = ConfigConst.DEFAULT_QOS

        msgInfo = self.mqttClient.publish(topic=resource.value, payload=msg, qos=qos)
        # Commented to avoid blocking as per instructions
        # msgInfo.wait_for_publish()
        return True

    def subscribeToTopic(self, resource: ResourceNameEnum = None, callback=None, qos: int = ConfigConst.DEFAULT_QOS) -> bool:
        if not resource:
            logging.warning('No topic specified. Cannot subscribe.')
            return False

        if qos < 0 or qos > 2:
            qos = ConfigConst.DEFAULT_QOS

        self.mqttClient.subscribe(resource.value, qos)
        return True

    def unsubscribeFromTopic(self, resource: ResourceNameEnum = None):
        if not resource:
            logging.warning('No topic specified. Cannot unsubscribe.')
            return False

        self.mqttClient.unsubscribe(resource.value)
        return True
