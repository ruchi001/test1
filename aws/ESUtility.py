_Author__ = 'Sivaram'
from elasticsearch import Elasticsearch
import json
from Logging import logger


def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv

def _decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        rv[key] = value
    return rv

class ESUtility(object):

    def __init__(self, es_url, port = 9200, auth=False, ssl=False):
        try:
            global BASEPATH
            global LOG_FILE
            global logger
            #self.__ES_URL__ = "http://52.3.163.36:9500"
            self.__ES_URL__ = es_url
            self.__ES_OBJ__ = Elasticsearch(self.__ES_URL__, port=int(port), use_ssl=ssl)
        except Exception,e:
            print e

    def addDocumentElasticSearch(self, indexName, indexType, addJson, indexID):
        ES_Response = self.__ES_OBJ__.index(index=indexName, doc_type=indexType, id=indexID, body=addJson)
        json_ES_ResponseObject = json.loads(json.dumps(ES_Response), object_hook=_decode_dict)
        return json_ES_ResponseObject

    def updateElasticSearch(self,indexName,indexType,indexId,finalJson):
        if indexId == "":
            ES_Response = self.__ES_OBJ__.index(index=indexName, doc_type=indexType, body=finalJson)
        else:
            ES_Response = self.__ES_OBJ__.index(index=indexName, doc_type=indexType, id=indexId, body=finalJson)
        json_ES_ResponseObject = json.loads(json.dumps(ES_Response), object_hook=_decode_dict)
        return json_ES_ResponseObject["_id"]

    # for partial update
    def partialUpdateElasticSearch(self, indexName, indexType, indexId, updateJson):
        body = {"doc": updateJson, "doc_as_upsert" : True}
        ES_Response = self.__ES_OBJ__.update(index=indexName, doc_type=indexType, id=indexId, body=body)
        json_ES_ResponseObject = json.loads(json.dumps(ES_Response), object_hook=_decode_dict)
        return json_ES_ResponseObject["_id"]

    def queryElasticSearch(self,indexName,indexType,size=100000000):
        try:
            ES_Response = self.__ES_OBJ__.search(index = indexName, doc_type = indexType, size = size,timeout=60)
        except:
            logger.exception("Index not found in Elastic Search. " + "Index -->" + indexName + " indexType-->" + indexType)
            ES_Response = {}
        json_ES_ResponseObject =  json.loads(json.dumps(ES_Response), object_hook=_decode_dict)
        return json_ES_ResponseObject

    def queryElasticSearchById(self,indexName,indexType,indexId):
        try:
            ES_Response = self.__ES_OBJ__.get(index=indexName, doc_type=indexType, id=indexId)['_source']
        except:
            logger.exception("Index not found in Elastic Search. " + "Index -->" + indexName + " indexType-->" + indexType + " indexId-->" + indexId)
            ES_Response = {}
        json_ES_ResponseObject =  json.loads(json.dumps(ES_Response), object_hook=_decode_dict)
        return json_ES_ResponseObject

    def queryElasticSearchByBody(self,indexName, indexType, bodyQuery,size=10):
        try:
            ES_Response = self.__ES_OBJ__.search(index=indexName, doc_type=indexType, body=bodyQuery, size=size)
        except Exception as e:
            print e
            print "Index not found in Elastic Search. " + "Index -->" + indexName + " indexType-->" + indexType
            print "Exception occurred in queryElasticSearchByBody() : "
            ES_Response = {}
        json_ES_ResponseObject = json.loads(json.dumps(ES_Response), object_hook=_decode_dict)
        return json_ES_ResponseObject

    def countElasticSearchByBody(self,indexName, indexType, bodyQuery,size=100000000):
        totalRecords = 0
        try:
            ES_Response = self.__ES_OBJ__.search(index=indexName, doc_type=indexType, body=bodyQuery, size=size)
            json_ES_ResponseObject = json.loads(json.dumps(ES_Response), object_hook=_decode_dict)
            totalRecords = json_ES_ResponseObject["hits"]["total"]
            return totalRecords
        except:
            print "Index not found in Elastic Search. " + "Index -->" + indexName + " indexType-->" + indexType
            print "Exception occurred in countElasticSearchByBody() : "
        return totalRecords

    def deleteElasticSerarchById(self,indexName,indexType,indexId):
        ES_Response = self.__ES_OBJ__.delete(index=indexName, doc_type=indexType, id=indexId, ignore=[400, 404])
        json_ES_ResponseObject = json.loads(json.dumps(ES_Response), object_hook=_decode_dict)
        return json_ES_ResponseObject

    def fetchRecordsFromESJson(self,jsonObj):
        recordList = []
        try:
            tempJsonObj = jsonObj["hits"]["hits"]
            for record in tempJsonObj:
                recordList.append(record["_source"])
        except:
            logger.exception("Exception in fetchRecordsFromESJson")
        return recordList

    def fetchBucketsFromESJson(self, jsonObj, query_name):
        tempJsonObj = jsonObj["aggregations"][query_name]["buckets"]
        recordList = []
        for record in tempJsonObj:
            recordList.append(record["key"].title())
        return recordList


   




