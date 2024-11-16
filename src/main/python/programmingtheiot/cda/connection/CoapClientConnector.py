import logging
import socket
import traceback

from coapthon.client.helperclient import HelperClient
from coapthon import defines
from coapthon.utils import generate_random_token

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum
from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.cda.connection.IRequestResponseClient import IRequestResponseClient
from programmingtheiot.data.DataUtil import DataUtil  # Ensure this is available in your codebase

class CoapClientConnector(IRequestResponseClient):
    """
    Shell representation of class for student implementation.
    """

    def __init__(self):
        # Initialize the configuration and properties
        self.config = ConfigUtil()
        self.dataMsgListener = None
        self.enableConfirmedMsgs = False
        self.coapClient = None
        self.observeRequests = {}

        # Retrieve host and port from configuration
        self.host = self.config.getProperty(ConfigConst.COAP_GATEWAY_SERVICE, ConfigConst.HOST_KEY, ConfigConst.DEFAULT_HOST)
        self.port = self.config.getInteger(ConfigConst.COAP_GATEWAY_SERVICE, ConfigConst.PORT_KEY, ConfigConst.DEFAULT_COAP_PORT)
        self.uriPath = f"coap://{self.host}:{self.port}/"

        logging.info('Host:Port: %s:%s', self.host, str(self.port))
        
        # Resolve host and initialize client
        try:
            tmpHost = socket.gethostbyname(self.host)
            if tmpHost:
                self.host = tmpHost
                self._initClient()
            else:
                logging.error("Can't resolve host: %s", self.host)
        except socket.gaierror:
            logging.error("Failed to resolve host: %s", self.host)

    def _initClient(self):
        try:
            # Create the CoAP client instance
            self.coapClient = HelperClient(server=(self.host, self.port))
            logging.info('Client created. Will invoke resources at: %s', self.uriPath)
        except Exception as e:
            logging.error("Failed to create CoAP client for URI path: %s", self.uriPath)
            traceback.print_exception(type(e), e, e.__traceback__)

    def sendDiscoveryRequest(self, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
        logging.info("Discovering remote resources...")
        return self.sendGetRequest(resource=None, name='.well-known/core', enableCON=False, timeout=timeout)

    def sendGetRequest(self, resource: ResourceNameEnum = None, name: str = None, enableCON: bool = False, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
        if resource or name:
            resourcePath = self._createResourcePath(resource, name)
            logging.info("Issuing GET with path: %s", resourcePath)

            request = self.coapClient.mk_request(defines.Codes.GET, path=resourcePath)
            request.token = generate_random_token(2)

            if not enableCON:
                request.type = defines.Types["NON"]

            response = self.coapClient.send_request(request=request, timeout=timeout)
            self._onGetResponse(response=response, resourcePath=resourcePath)
            return True
        else:
            logging.warning("Can't test GET - no path or path list provided.")
            return False

    def sendDeleteRequest(self, resource: ResourceNameEnum = None, name: str = None, enableCON: bool = False, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
        if resource or name:
            resourcePath = self._createResourcePath(resource, name)
            logging.info("Issuing DELETE with path: %s", resourcePath)

            request = self.coapClient.mk_request(defines.Codes.DELETE, path=resourcePath)
            request.token = generate_random_token(2)

            if not enableCON:
                request.type = defines.Types["NON"]

            self.coapClient.send_request(request=request, callback=self._onDeleteResponse, timeout=timeout)
            return True
        else:
            logging.warning("Can't test DELETE - no path or path list provided.")
            return False

    def sendPostRequest(self, resource: ResourceNameEnum = None, name: str = None, enableCON: bool = False, payload: str = None, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
        if resource or name:
            resourcePath = self._createResourcePath(resource, name)
            logging.info("Issuing POST with path: %s", resourcePath)

            request = self.coapClient.mk_request(defines.Codes.POST, path=resourcePath)
            request.token = generate_random_token(2)
            request.payload = payload

            if not enableCON:
                request.type = defines.Types["NON"]

            self.coapClient.send_request(request=request, callback=self._onPostResponse, timeout=timeout)
            return True
        else:
            logging.warning("Can't test POST - no path or path list provided.")
            return False

    def sendPutRequest(self, resource: ResourceNameEnum = None, name: str = None, enableCON: bool = False, payload: str = None, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
        if resource or name:
            resourcePath = self._createResourcePath(resource, name)
            logging.info("Issuing PUT with path: %s", resourcePath)

            request = self.coapClient.mk_request(defines.Codes.PUT, path=resourcePath)
            request.token = generate_random_token(2)
            request.payload = payload

            if not enableCON:
                request.type = defines.Types["NON"]

            self.coapClient.send_request(request=request, callback=self._onPutResponse, timeout=timeout)
            return True
        else:
            logging.warning("Can't test PUT - no path or path list provided.")
            return False

    def setDataMessageListener(self, listener: IDataMessageListener = None) -> bool:
        self.dataMsgListener = listener
        return True

    def startObserver(self, resource: ResourceNameEnum = None, name: str = None, ttl: int = IRequestResponseClient.DEFAULT_TTL) -> bool:
        if resource or name:
            resourcePath = self._createResourcePath(resource, name)

            if resourcePath in self.observeRequests:
                logging.warning("Already observing resource %s. Ignoring start observe request.", resourcePath)
                return False

            self.observeRequests[resourcePath] = None

            try:
                self.coapClient.observe(path=resourcePath, callback=self._onGetResponse)
                logging.info("Started observing resource: %s", resourcePath)
                return True
            except Exception as e:
                logging.warning("Failed to observe path: %s", resourcePath)
                traceback.print_exception(type(e), e, e.__traceback__)
                return False
        else:
            logging.warning("Can't start observer - no path or path list provided.")
            return False

    def stopObserver(self, resource: ResourceNameEnum = None, name: str = None, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
        if resource or name:
            resourcePath = self._createResourcePath(resource, name)

            if resourcePath not in self.observeRequests:
                logging.warning("Resource %s not being observed. Ignoring stop observe request.", resourcePath)
                return False

            response = self.observeRequests[resourcePath]

            try:
                self.coapClient.cancel_observing(response=response, send_rst=True)
                del self.observeRequests[resourcePath]
                logging.info("Canceled observe for resource: %s", resourcePath)
                return True
            except Exception as e:
                logging.warning("Failed to cancel observe for resource: %s", resourcePath)
                traceback.print_exception(type(e), e, e.__traceback__)
                return False
        else:
            logging.warning("Can't stop observer - no path or path list provided.")
            return False

    def _createResourcePath(self, resource: ResourceNameEnum = None, name: str = None) -> str:
        resourcePath = ""
        hasResource = False
        if resource:
            resourcePath += resource.value
            hasResource = True
        if name:
            if hasResource:
                resourcePath += '/'
            resourcePath += name
        return resourcePath

    def _onGetResponse(self, response, resourcePath: str = None):
        if not response:
            logging.warning('GET response invalid. Ignoring.')
            return
        
        logging.info('GET response received.')
        jsonData = response.payload
        locationPath = resourcePath.split('/')
        
        if len(locationPath) > 2:
            dataType = locationPath[2]
            
            if dataType == ConfigConst.ACTUATOR_CMD:
                logging.info("ActuatorData received: %s", jsonData)
                try:
                    ad = DataUtil().jsonToActuatorData(jsonData)
                    if self.dataMsgListener:
                        self.dataMsgListener.handleActuatorCommandMessage(ad)
                except Exception:
                    logging.warning("Failed to decode actuator data. Ignoring: %s", jsonData)
            else:
                logging.info("Response data received. Payload: %s", jsonData)
        else:
            logging.info("Response data received. Payload: %s", jsonData)

    def _onPutResponse(self, response):
        if not response:
            logging.warning('PUT response invalid. Ignoring.')
            return
        
        logging.info('PUT response received: %s', response.payload)
        
    def _onPostResponse(self, response):
        if not response:
            logging.warning('POST response invalid. Ignoring.')
            return
        
        logging.info('POST response received: %s', response.payload)
        
    def _onDeleteResponse(self, response):
        if not response:
            logging.warning('DELETE response invalid. Ignoring.')
            return
        
        logging.info('DELETE response received: %s', response.payload)
        
        
class HandleActuatorEvent:
    def __init__(self, listener: IDataMessageListener = None, resourcePath: str = None, requests=None):
        self.listener = listener
        self.resourcePath = resourcePath
        self.observeRequests = requests
    
    def handleActuatorResponse(self, response):
        if response:
            jsonData = response.payload
            self.observeRequests[self.resourcePath] = response  # Store the response
            
            logging.info("Received actuator command response to resource %s: %s", self.resourcePath, jsonData)
            
            if self.listener:
                try:
                    data = DataUtil().jsonToActuatorData(jsonData=jsonData)
                    self.listener.handleActuatorCommandMessage(data)
                except Exception:
                    logging.warning("Failed to decode actuator data for resource %s. Ignoring: %s", self.resourcePath, jsonData)

