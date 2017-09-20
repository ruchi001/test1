# -*- coding: utf-8 -*-
import io
import json
import time
import copy
from datetime import datetime
import requests
import traceback
from Logging import logger
import paho.mqtt.client as mqtt
from ConfigParser import SafeConfigParser
from pymodbus.client.sync import ModbusSerialClient as ModbusSERIALClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
from pymodbus.client.sync import ModbusTcpClient
import fileUploader

global sleepTime, uploadData, triggerSMS, smsUrl, fileUploaderObj
smsUrl = "http://localhost:9000/sendSMS"


class Monitor:

    def __init__(self):
        print ("Inside Init")
        self.dataJson = {}
        self.dataJson["collectors"] = {}
        self.readConfig()
        self.uploafFlag = 0
        self.finalDataJson = {}
        self.previousDataJson = ""
        self.connectivity = False
        self.uploadHistorical = False

    def connectServer(self):
        self.mqttc = mqtt.Client("python_pub")
        try:
            #self.mqttc.username_pw_set()
            self.connectionFailed = self.mqttc.connect(self.uploadIp, int(self.uploadPort))
            return True
        except Exception as e:
            print "Unable to connect to the server trying to reconnect. "
            logger.exception(e)
            traceback.print_exc()
            self.connectionFailed = 1
            return False

    def disconnectServer(self):
        try:
            self.mqttc.disconnect()
        except Exception as e:
            logger.exception(e)
            print "Failed to disconnect from server"

    def _decode_list(self, data):
        rv = []
        for item in data:
            if isinstance(item, unicode):
                item = item.encode('utf-8')
            elif isinstance(item, list):
                item = self._decode_list(item)
            elif isinstance(item, dict):
                item = self._decode_dict(item)
            rv.append(item)
        return rv

    def _decode_dict(self, data):
        rv = {}
        for key, value in data.iteritems():
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            if isinstance(value, unicode):
                value = value.encode('utf-8')
            elif isinstance(value, list):
                value = self._decode_list(value)
            elif isinstance(value, dict):
                value = self._decode_dict(value)
            rv[key] = value
        return rv

    def readConfig(self):
        parser = SafeConfigParser()
        global sleepTime, uploadData, triggerSMS
        parser.read("setup.conf")
        try:
            self.uploadIp = parser.get("siteSettings", "uploadIp")
            self.dataDumpJsonFilename = parser.get("siteSettings", "jsonFilename")      # file to upload temporary data during offline state
            self.uploadPort = parser.get("siteSettings", "uploadPort")
            self.serviceUrl = parser.get("siteSettings", "serviceUrl")
            self.totalCollector = int(parser.get("siteSettings", "totalCollectors"))
            self.totalParamteters = int(parser.get("siteSettings", "totalParameters"))
            self.topic = parser.get("siteSettings", "topic")
            self.compare = int(parser.get("siteSettings", "compare"))
            self.dbserver = parser.get("siteSettings", "dbserver")
            self.dataFormat = parser.get("siteSettings", "dataFormat")
            sleepTime = int(parser.get("siteSettings", "sleepTime"))
            uploadData = int(parser.get("siteSettings", "uploadData"))
            try:
                self.numbers = parser.get("siteSettings", "numbers")
                triggerSMS = int(parser.get("siteSettings", "triggerSMS"))
            except:
                self.numbers = ""
                triggerSMS = 0
        except Exception as e:
            traceback.print_exc()
            logger.debug("Exception in reading siteSettings")
            logger.exception(e)

        try:
            self.stationId = parser.get("siteDetails", "stationId")
            self.subStationId = parser.get("siteDetails", "subStationId")
            self.siteLocation = parser.get("siteDetails", "siteLocation")
            self.dataJson["stationId"] = self.stationId
            self.dataJson["siteLocation"] = self.siteLocation
        except Exception as e:
            traceback.print_exc()
            logger.debug("Exception in reading siteDetails")
            logger.exception(e)

        for i in range(1, self.totalCollector + 1):
            try:
                tempCollectorId = parser.get("Collector"+str(i), "CollectorId")
                tempCollectorType = parser.get("Collector"+str(i), "CollectorType")
                deviceIp = parser.get("Collector"+str(i), "deviceIp")
                start = parser.get("Collector"+str(i), "start")
                proxy = parser.get("Collector"+str(i), "proxy")
                comPort = parser.get("Collector"+str(i), "comPort")
                deviceId = parser.get("Collector"+str(i), "deviceId")
                totalRegister = parser.get("Collector"+str(i), "totalRegister")
                baudRate = parser.get("Collector"+str(i), "baudRate")
                self.dataJson["collectors"][tempCollectorId] = {}
                self.dataJson["collectors"][tempCollectorId]["CollectorId"] = tempCollectorId
                self.dataJson["collectors"][tempCollectorId]["CollectorType"] = tempCollectorType
                self.dataJson["collectors"][tempCollectorId]["deviceIp"] = deviceIp
                self.dataJson["collectors"][tempCollectorId]["start"] = start
                self.dataJson["collectors"][tempCollectorId]["comPort"] = comPort
                self.dataJson["collectors"][tempCollectorId]["deviceId"] = deviceId
                self.dataJson["collectors"][tempCollectorId]["proxy"] = proxy
                self.dataJson["collectors"][tempCollectorId]["totalRegister"] = totalRegister
                self.dataJson["collectors"][tempCollectorId]["baudRate"] = baudRate
                self.dataJson["collectors"][tempCollectorId]["parameters"] = {}
            except Exception as e:
                traceback.print_exc()
                logger.exception(e)

        for i in range(1, self.totalParamteters + 1):
            try:

                tempParameterId = parser.get("Parameter"+str(i), "parameterId")
                tempParameterName = parser.get("Parameter"+str(i), "parameterName")
                dataType = parser.get("Parameter"+str(i), "dataType")
                channelNo = parser.get("Parameter"+str(i), "channelNo")
                collector = parser.get("Parameter"+str(i), "collector")
                coeffA = parser.get("Parameter"+str(i), "coeffA")
                coeffB = parser.get("Parameter"+str(i), "coeffB")
                feeder = str(parser.get("Parameter"+str(i), "feeder")).strip()
                self.dataJson["collectors"][collector]["parameters"]["parameter"+str(i)] = {}
                self.dataJson["collectors"][collector]["parameters"]["parameter"+str(i)]["parameterId"] = tempParameterId
                self.dataJson["collectors"][collector]["parameters"]["parameter"+str(i)]["parameterName"] = tempParameterName
                self.dataJson["collectors"][collector]["parameters"]["parameter"+str(i)]["dataType"] = dataType
                self.dataJson["collectors"][collector]["parameters"]["parameter"+str(i)]["feeder"] = feeder
                self.dataJson["collectors"][collector]["parameters"]["parameter"+str(i)]["channelNo"] = channelNo
                self.dataJson["collectors"][collector]["parameters"]["parameter"+str(i)]["coeffA"] = coeffA
                self.dataJson["collectors"][collector]["parameters"]["parameter"+str(i)]["coeffB"] = coeffB
                self.dataJson["collectors"][collector]["parameters"]["parameter"+str(i)]["value"] = ""
                #self.dataJson["collectors"][collector]["parameters"][tempParameterId]["value"] = ""

            except Exception as e:
                traceback.print_exc()
                logger.exception(e)
        #print self.dataJson
        logger.debug("DataJson: ")
        logger.debug(self.dataJson)

    def readEventJson(self, deviceIp, collectorType):
        data = requests.get("http://" + deviceIp + "/event_log.json")
        data = json.loads(data.text)
        return data

    def readDataJson(self, deviceIp, collectorType):
        data = requests.get("http://" + deviceIp + "/data_" + str(collectorType.lower()).split("_")[1] + ".json")
        data = self._decode_dict(json.loads(data.text))
        return data

    def readData(self):
        self.dataJson["timeStamp"] = str(datetime.now()).split(".")[0]
        for everyCollector in self.dataJson["collectors"]:
            #print self.dataJson["collectors"][everyCollector]
            collectorType = self.dataJson["collectors"][everyCollector]["CollectorType"]
            deviceIp = self.dataJson["collectors"][everyCollector]["deviceIp"]
            # totalRegister = self.dataJson["collectors"][everyCollector]["totalRegister"]
            # start = self.dataJson["collectors"][everyCollector]["start"]

            if "dl8-event" in collectorType.lower():
                data = self.readEventJson(deviceIp, collectorType)
            elif "dl8-datajson" in collectorType.lower():
                data = self.readDataJson(deviceIp, collectorType)

            client = None
            if "modbus" in collectorType.lower():
                try:
                    collector = self.dataJson["collectors"][everyCollector]
                    if "-rtu" in collectorType.lower():
                        client = ModbusSERIALClient(method="rtu", port=collector["comPort"], stopbits=1, bytesize=8,
                                                    parity='N', baudrate=int(collector["baudRate"]))
                    elif "-tcp" in collectorType.lower():
                        client = ModbusTcpClient(host=deviceIp, port=502)
                    if "-hr" in collectorType.lower():
                        data = self.readModbus_HR(collector, client)
                    elif "-ir" in collectorType.lower():
                        data = self.readModbus_IR(collector, client)
                    elif "-cs" in collectorType.lower():
                        data = self.readModbus_CS(collector, client)
                    elif "-is" in collectorType.lower():
                        data = self.readModbus_IS(collector, client)
                    try:
                        client.close()
                    except Exception as e:
                        print "Exception while closing the connection"
                        logger.exception(e)
                except Exception as e:
                    logger.exception(e)
                    print "Unable to connect to Modbus Server"

            try:

                for everyParameter in self.dataJson["collectors"][everyCollector]["parameters"]:
                    try:
                        dataType = self.dataJson["collectors"][everyCollector]["parameters"][everyParameter]["dataType"]
                        channelData = data[dataType]
                    except Exception as e:
                        #logger.exception(e)
                        channelData = data
                    coeffA = self.dataJson["collectors"][everyCollector]["parameters"][everyParameter]["coeffA"]
                    coeffB = self.dataJson["collectors"][everyCollector]["parameters"][everyParameter]["coeffB"]
                    channelno = self.dataJson["collectors"][everyCollector]["parameters"][everyParameter]["channelNo"]
                    feeder = self.dataJson["collectors"][everyCollector]["parameters"][everyParameter]["feeder"]
                    parameterId = self.dataJson["collectors"][everyCollector]["parameters"][everyParameter]["parameterId"]
                    parameterId = feeder + "&"+ parameterId

                    try:
                        if feeder == "":
                            print "Feeder not Defined"
                            raise Exception
                        if coeffA == "" and coeffB == "":
                            if "-bit" in collectorType.lower():
                                bitdata = str(bin(channelData[int(str(channelno).split("-")[0])])[2:]).zfill(16)[::-1]
                                print bitdata
                                self.dataJson["collectors"][everyCollector]["parameters"][everyParameter]["value"] = bitdata[int(str(channelno).split("-")[1])]
                            else:
                                self.dataJson["collectors"][everyCollector]["parameters"][everyParameter]["value"] = str(
                                    channelData[int(channelno)])
                        else:
                            tempValue = float(channelData[int(channelno)])
                            tempValue = tempValue * float(coeffA)
                            tempValue = round(tempValue + float(coeffB), 2)
                            self.dataJson["collectors"][everyCollector]["parameters"][everyParameter]["value"] = str(tempValue)
                        self.finalDataJson[parameterId] = \
                        self.dataJson["collectors"][everyCollector]["parameters"][everyParameter]["value"]
                    except Exception as e:
                        traceback.print_exc()
                        logger.debug("invalid channel number for parameter: ")
            except Exception as e:
                print e.message
                traceback.print_exc()
                logger.exception(e)
        logger.debug("FinalData: ")
        logger.debug(self.dataJson)
        #print "FinalJson: ", self.dataJson

    def compareJson(self, jsonA, jsonB):
        try:
            for everyElement in jsonA:
                if jsonA[everyElement] != jsonB[everyElement]:
                    return False
            return True
        except:
            return False

    def uploadData(self):
        try:
            finalData = {}
            finalData["stationId"] = self.stationId
            finalData["subStationId"] = self.subStationId
            finalData["data"] = self.finalDataJson
            finalData["timestamp"] = str(datetime.now()).split(".")[0]

            jsonFileObj = open(self.dataDumpJsonFilename, "r+")
            try:
                jsonDumpData = json.load(jsonFileObj)
            except:
                jsonDumpData = []

            #print "FinalData: ", finalData
            #print "finaldatajson: ", str(finalData["data"])
            #print "previousData : ", str(self.previousDataJson)
            if self.compare == 1:
                if not self.compareJson(finalData["data"],self.previousDataJson):

                    try:
                        tempDataJson = copy.deepcopy(finalData["data"])
                        for everyItem in tempDataJson:
                            if self.previousDataJson!= '' and finalData["data"][everyItem] == self.previousDataJson[everyItem]:
                                finalData["data"].pop(everyItem)
                    except Exception as e:
                        traceback.print_exc()
                        print e
                        pass
                    print "Uploading: ", str(finalData).replace("ON", "T").replace("OFF", "F").replace("True", "T").replace("False", "F")

                    try:
                        resp = requests.post(self.serviceUrl + "updateCircuit",
                                         data=str(finalData).replace("ON", "T").replace("OFF", "F").replace("True", "T").replace("False", "F"))
                        logger.debug(resp)
                    except:
                        # store the finalDataJson until connectivity returns and gets pushed back to the server
                        pass

                    if self.connectServer():
                        MQTTresponse = self.mqttc.publish(self.topic, str(self.finalDataJson).replace("ON", "T").replace("OFF", "F").replace("True", "T").replace("False", "F"))
                        if not MQTTresponse.is_published():
                            self.mqttc.reconnect()
                            MQTTresponse = self.mqttc.publish(self.topic,
                                                              str(self.finalDataJson).replace("ON", "T").replace("OFF", "F").replace("True", "T").replace("False", "F"))
                        logger.debug(MQTTresponse.is_published())
                        self.mqttc.loop(2)  # timeout = 2s
                        self.previousDataJson = copy.deepcopy(finalData["data"])
                        print "Uploaded: ", MQTTresponse.is_published()
                        self.connectivity = True         # use this flag to check for internet connectivity
                    else:
                        print "Failed to connect to mqtt"
                        logger.debug("Error while uploading to the mqtt server")
                        logger.debug("Failed to connect to the mqtt server")
                        self.connectivity = False        # use this flag to check for internet connectivity
                        # in that case, store the finalDataJson until connectivity returns and gets pushed back to the server
                        # write JSON into the file
                        jsonFileObj.seek(0)
                        jsonDumpData.append(finalData)
                        json.dump(jsonDumpData, jsonFileObj)
                        fileUploaderObj.writeintoJSON(finalData, self.stationId)
                        self.uploadHistorical = True

            else:
                tempData = {}
                tempData["values"] = self.finalDataJson
                tempData["stationId"] = self.stationId
                tempData["subStationId"] = self.subStationId
                tempData["timeStamp"] = int(time.mktime(datetime.now().timetuple()))
                data = json.dumps(tempData).replace("ON", "T").replace("OFF", "F").replace("True", "T").replace("False", "F")

                print "data:", data
                if self.connectServer():
                    self.mqttc.publish(self.topic, data)
                    self.mqttc.loop(2)  # timeout = 2s
                    self.disconnectServer()
                    self.previousDataJson = copy.deepcopy(finalData["data"])
                    print ("Uploaded")
                    self.connectivity = True  # use this flag to check for internet connectivity
                else:
                    print "Failed to connect to mqtt"
                    logger.debug("Error while uploading to the mqtt server")
                    logger.debug("Failed to connect to the mqtt server")
                    self.connectivity = False  # use this flag to check for internet connectivity
                    # if device fails to transmit the data, save it into a JSON for future publication
                    # write JSON into the file
                    logger.info("Writing data into json")
                    jsonFileObj.seek(0)
                    jsonDumpData.append(tempData)
                    json.dump(jsonDumpData, jsonFileObj)
                    fileUploaderObj.writeintoJSON(finalData, self.stationId)
                    self.uploadHistorical = True         # True if data dump from json file is required

        except Exception as e:
            traceback.print_exc()
            print "Exception"
            logger.exception(e)
            try:
                self.mqttc.disconnect()
                self.connectionFailed = 1
            except Exception as e:
                traceback.print_exc()
                logger.exception(e)
                self.connectionFailed = 1
        finally:
            try:
                jsonFileObj.close()
            except:
                pass


    def updateDB(self):
        finalJson = {}
        finalJson["stationId"] = self.stationId
        finalJson["subStationId"] = self.subStationId
        finalJson["timeStamp"] = int(time.mktime(datetime.now().timetuple()))
        finalJson["data"] = self.finalDataJson
        try:
            print self.dbserver
            response = requests.post(self.dbserver+"updateDB", json=finalJson, timeout=5)
            print response
            logger.debug(response.text)
        except Exception as e:
            traceback.print_exc()
            print "Failed to upload"
            logger.exception(e)


    def sendSMS(self):
        file = open("lastSMS.json", "r")
        lastSMS = file.read()
        try:
            lastSMS = json.loads(lastSMS)
        except:
            lastSMS = {}
        file.close()
        currentTime = int(time.mktime(datetime.now().timetuple()))
        for everyItem in self.finalDataJson.keys():
            if int(self.finalDataJson[everyItem]) == 1:
                try:
                    if currentTime - int(lastSMS[everyItem]) > 300:
                        tempdata = {
                            "numbers": self.numbers,
                            "message": str(everyItem) + " tripped",
                            "sender": "ILENSS",
                            "authKey": ""
                        }
                        resp = requests.post(smsUrl, data=json.dumps(tempdata))
                        print resp.text
                        logger.debug(resp.text)
                        if "Success" in resp.text:
                            print "sms sent"
                except:
                    lastSMS[everyItem] = str(currentTime)
                    tempdata = {
                        "numbers": self.numbers,
                        "message": str(everyItem) + " tripped",
                        "sender": "ILENSS",
                        "authKey": ""
                    }
                    resp = requests.post(smsUrl, data=json.dumps(tempdata))
                    print resp.text
                    logger.debug(resp.text)
                    if "Success" in resp.text:
                        print "sms sent"
        file = open("lastSMS.json", "w")
        file.write(json.dumps(lastSMS))
        file.close()

    def simpleFloat(self, response):
        floatReading = []
        try:
            length = len(response) / 2
            for channelNo in range(0, length):
                icount = channelNo * 2
                temp_data = []
                temp_data.append(response[icount])
                temp_data.append(response[icount + 1])
                decoder = BinaryPayloadDecoder.fromRegisters(temp_data, endian=Endian.Big)
                value = decoder.decode_32bit_float()
                floatReading.append(value)
            logger.debug("Float: " + str(floatReading))
            return floatReading
        except Exception as e:
            traceback.print_exc()
            print e
            print e.message

    def swappedFloat(self, response):
        floatReading = []
        try:
            length = len(response) / 2
            for channelNo in range(0, length):
                icount = channelNo * 2
                temp_data = []
                temp_data.append(response[icount + 1])
                temp_data.append(response[icount])
                decoder = BinaryPayloadDecoder.fromRegisters(temp_data, endian=Endian.Big)
                value = decoder.decode_32bit_float()
                floatReading.append(value)
            #print "Swapped Float: " + str(floatReading)
            logger.debug("Swapped Float: " + str(floatReading))
            return floatReading
        except Exception as e:
            traceback.print_exc()
            print e
            print e.message

    def longInteger(self, response):
        longIntReading = []
        try:
            length = len(response) / 2
            for channelNo in range(0, length):
                icount = channelNo * 2
                temp_data = []
                temp_data.append(response[icount+1])
                temp_data.append(response[icount])
                decoder = BinaryPayloadDecoder.fromRegisters(temp_data, endian=Endian.Big)
                value = decoder.decode_32bit_int()
                longIntReading.append(value)
            logger.debug("LongInt: " + str(longIntReading))
            return longIntReading
        except Exception as e:
            traceback.print_exc()
            print e
            print e.message

    def readModbus_HR(self, collector, client):
        data = []
        print "calling tcp client"
        try:

            connect_status = client.connect()
            logger.debug("connect_status: " + str(connect_status))
            response = client.read_holding_registers(int(collector["start"]), int(collector["totalRegister"]), unit=int(collector["deviceId"]))
            logger.debug("raw response: " + str(response))
            logger.debug("registers: " + str(response.registers))
            data = response.registers
            if "-sf" in str(collector["CollectorType"]).lower():
                data = self.swappedFloat(response.registers)
            elif "-float" in str(collector["CollectorType"]).lower():
                data = self.simpleFloat(response.registers)
            client.close()
        except Exception as e:
            client.close()
            traceback.print_exc()
            print "Some error Occured:" + str(e)
            print e.message
        return data

    def readModbus_IR(self, collector, client):
        data = []
        print "calling rtu client"
        try:
            connect_status = client.connect()
            logger.debug("connect_status: "+ str(connect_status))
            response = client.read_input_registers(int(collector["start"]), int(collector["totalRegister"]), unit=int(collector["deviceId"]))
            logger.debug("raw response: " + str(response))
            logger.debug("registers: " + str(response.registers))
            data = response.registers
            if "-sf" in str(collector["CollectorType"]).lower():
                data = self.swappedFloat(response.registers)
            elif "-float" in str(collector["CollectorType"]).lower():
                data = self.simpleFloat(response.registers)
            elif "-li" in str(collector["CollectorType"]).lower():
                data = self.longInteger(response.registers)
            client.close()
        except Exception as e:
            client.close()
            traceback.print_exc()
            print "Some error Occured:" + str(e)
            print e.message
        return data

    def readModbus_CS(self, collector, client):
        data = []
        print "calling tcp client"
        try:
            connect_status = client.connect()
            logger.debug("connect_status: "+ str(connect_status))
            response = client.read_coils(int(collector["start"]), int(collector["totalRegister"]), unit=int(collector["deviceId"]))
            logger.debug("raw response: " + str(response))
            logger.debug("registers: " + str(response.bits))
            data = response.bits
            if "-sf" in str(collector["CollectorType"]).lower() or "float" in str(collector["CollectorType"]).lower():
                logger.debug("Float or sFloat is not available for this collector")
            client.close()
        except Exception as e:
            client.close()
            traceback.print_exc()
            print "Some error Occured:" + str(e)
            print e.message
        return data

    def readModbus_IS(self, collector, client):
        data = []
        print "calling rtu client"
        try:
            connect_status = client.connect()
            logger.debug("connect_status: "+ str(connect_status))
            response = client.read_discrete_inputs(int(collector["start"]), int(collector["totalRegister"]), unit=int(collector["deviceId"]))
            logger.debug("raw response: " + str(response))
            logger.debug("registers: " + str(response.bits))
            data = response.registers
            if "sfloat" in str(collector["CollectorType"]).lower():
                data = self.swappedFloat(response.bits)
            elif "float" in str(collector["CollectorType"]).lower():
                data = self.simpleFloat(response.bits)
            client.close()
        except Exception as e:
            client.close()
            traceback.print_exc()
            print "Some error Occured:" + str(e)
            print e.message
        return data




Object = Monitor()
fileUploaderObj = fileUploader.uploadData()
while True:
    try:
        global sleepTime, uploadData, triggerSMS
        Object.readData()
        if uploadData == 1:
            Object.uploadData()
            if len(Object.dbserver) > 5:
                Object.updateDB()
        if triggerSMS == 1:
            Object.sendSMS()
        if Object.connectivity and Object.uploadHistorical:
            print "Uploading historical data ..."
            if fileUploaderObj.uploadMqtt():
                Object.uploadHistorical = False
                print "Historical data uploaded"
            else:
                print "Failed to upload historical data on MQTT"
    except Exception as e:
        traceback.print_exc()
        print e.message
        logger.exception(e)
    time.sleep(int(sleepTime))

