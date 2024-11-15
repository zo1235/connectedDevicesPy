import logging
import asyncio
import threading
import aiocoap
from threading import Thread
from time import sleep
import traceback

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum
from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.cda.connection.handlers.GetTelemetryResourceHandler import GetTelemetryResourceHandler
from programmingtheiot.cda.connection.handlers.UpdateActuatorResourceHandler import UpdateActuatorResourceHandler
from programmingtheiot.cda.connection.handlers.GetSystemPerformanceResourceHandler import GetSystemPerformanceResourceHandler

class CoapServerAdapter:
    """
    Definition for a CoAP communications server, with embedded test functions.
    """

    def __init__(self, dataMsgListener=None):
        # Load configuration
        self.config = ConfigUtil()
        self.dataMsgListener = dataMsgListener
        self.enableConfirmedMsgs = False

        # Configuration for host and port
        self.host = self.config.getProperty(ConfigConst.COAP_GATEWAY_SERVICE, ConfigConst.HOST_KEY, ConfigConst.DEFAULT_HOST)
        self.port = self.config.getInteger(ConfigConst.COAP_GATEWAY_SERVICE, ConfigConst.PORT_KEY, ConfigConst.DEFAULT_COAP_PORT)

        # Server and task references
        self.coapServer = None
        self.coapServerTask = None

        # If using aiocoap, set this
        self.rootResource = None

        # If using CoAPthon3, set this
        self.listenTimeout = 30

        logging.info("CoAP server configured for host and port: coap://%s:%s", self.host, str(self.port))

    def _initServer(self):
        """
        Initialize the CoAP server by registering resource handlers.
        """
        try:
            # Create the root resource for the server
            self.rootResource = aiocoap.resource.Site()

            # Register the well-known core resource
            self.rootResource.add_resource(
                ['.well-known', 'core'], 
                aiocoap.resource.WKCResource(self.rootResource.get_resources_as_linkheader)
            )

            # Register the actuator command handler
            self.addResource(
                resourcePath=ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE,
                endName=ConfigConst.HUMIDIFIER_ACTUATOR_NAME,
                resource=UpdateActuatorResourceHandler(dataMsgListener=self.dataMsgListener)
            )

            # Register the system performance handler
            sysPerfDataListener = GetSystemPerformanceResourceHandler()
            self.addResource(
                resourcePath=ResourceNameEnum.CDA_SYSTEM_PERF_MSG_RESOURCE,
                resource=sysPerfDataListener
            )

            # TODO: Register other telemetry resource handlers (e.g., for SensorData)
            # For example: 
            # sensorDataListener = GetTelemetryResourceHandler()
            # self.addResource(
            #    resourcePath=ResourceNameEnum.CDA_SENSOR_DATA_RESOURCE,
            #    resource=sensorDataListener
            # )

            # Register callbacks with data message listener
            self.dataMsgListener.setSystemPerformanceDataListener(listener=sysPerfDataListener)

            logging.info("CoAP server created with default resources.")
        
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            logging.warning("Failed to create CoAP server.")

    def addResource(self, resourcePath: ResourceNameEnum = None, endName: str = None, resource=None):
        """
        Add a resource to the CoAP server.
        """
        if resourcePath and resource:
            uriPath = resourcePath.value

            # Append the endpoint name to the URI path if provided
            if endName:
                uriPath = uriPath + '/' + endName
            
            resourceList = uriPath.split('/')

            # If root resource is not created, create it
            if not self.rootResource:
                self.rootResource = aiocoap.resource.Site()

            # Add resource to the site (server)
            self.rootResource.add_resource(resourceList, resource)
        else:
            logging.warning("No resource provided for path: " + str(resourcePath.value))

    def startServer(self):
        """
        Start the CoAP server in a separate thread.
        """
        if not self.coapServer:
            logging.info("Starting Async CoAP server...")
            try:
                # Start the CoAP server in a separate thread
                threading.Thread(target=self._runServerTask, daemon=True).start()
                logging.info("\n\n***** Async CoAP server STARTED. *****\n\n")
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                logging.warning("Failed to start Async CoAP server.")

    def stopServer(self):
        """
        Stop the CoAP server.
        """
        if self.coapServer:
            logging.info("Shutting down CoAP server...")
            self._shutdownServerTask()

    def setDataMessageListener(self, listener: IDataMessageListener = None) -> bool:
        """
        Set the data message listener.
        """
        self.dataMsgListener = listener
        return True

    def _shutdownServerTask(self):
        """
        Shutdown the CoAP server task.
        """
        asyncio.run(self._shutdownServer())

    async def _shutdownServer(self):
        """
        Shutdown the CoAP server asynchronously.
        """
        try:
            await self.coapServer.shutdown()
            logging.info("\n\n***** Async CoAP server SHUTDOWN. *****\n\n")
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            logging.warning("Failed to shutdown Async CoAP server.")

    def _runServerTask(self):
        """
        Run the CoAP server asynchronously.
        """
        asyncio.run(self._runServer())

    async def _runServer(self):
        """
        Run the CoAP server loop and bind it to the host and port.
        """
        if self.rootResource:
            logging.info('Creating server context...')
            bindTuple = (self.host, self.port)
            self.coapServer = await aiocoap.Context.create_server_context(site=self.rootResource, bind=bindTuple)
            logging.info('Starting running loop - asyncio create_future()...')
            await asyncio.get_running_loop().create_future()
        else:
            logging.warning("Root resource not yet created. Can't start server.")
