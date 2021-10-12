import json
from typing import Collection, Text
from pymongo import MongoClient
import requests
from types import SimpleNamespace
import base64

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DB_NAME = 'gojamfdb'
COLLECTION_NAME = 'gogoJamfComDetail'
mongodbConnection = MongoClient(MONGODB_HOST, MONGODB_PORT)
mongodbCollection = mongodbConnection[DB_NAME][COLLECTION_NAME]


class CallingJamf():
 def __init__(self, apiUser, apiPass):
    #UAPI Credentials  
    self.string = apiUser + ":" + apiPass
    self.base64Encode = base64.b64encode(bytes(self.string, 'utf-8'))
    self.base64Encode = str(self.base64Encode)
    print(self.base64Encode)
    
    # refers to https://www.base64encode.org/

    self.jss_token_url = "https://goanimate.jamfcloud.com/uapi/auth/tokens"
    self.jss_CN_detail_url = "https://goanimate.jamfcloud.com/api/v1/computers-inventory-detail/"
    
    self.tokenObj= requests.post(self.jss_token_url, headers={'Accept': 'application/json',"Authorization": "Basic" + self.base64Encode})
    print(self.tokenObj.text) 
    
    self.jss_token_str = json.loads(self.tokenObj.text, object_hook=lambda d: SimpleNamespace(**d))
    print(self.jss_token_str)

    self.jss_base_url = "https://goanimate.jamfcloud.com/api/v1/computers-inventory?section=GENERAL&page=0&page-size=1000&sort=id%3Aasc" 
    self.response = requests.get(self.jss_base_url, headers= {"Authorization": "Bearer " + self.jss_token_str.token})
    
    if self.response.status_code == requests.codes.ok:
             print("Request Successfully, return code:" + " " + str(self.response.status_code))
             # Create Python Object from JSON String data
             self.jss_json_dictionary = json.loads(self.response.text)
    else:
        print("Request Computer Inventory (General) Failed, return code:" + " " + str(self.response.status_code))


    return None

 def LoopEachComputers(self):
        
        r_Json_Array = self.jss_json_dictionary
        li = [item.get('id') for item in r_Json_Array['results']]
        print(li)
        all_roles = []
        index = 0
        while index < len(li):
            element=str(li[index])
            jss_CNsearch_url = self.jss_CN_detail_url + element
            index += 1

            #print(jss_CNsearch_url)
            jss_CN_response = requests.get( jss_CNsearch_url, headers= {"Authorization": "Bearer " + self.jss_token_str.token})
            # Create Python Object from JSON String data
            jss_json_CN_dictionary = json.loads(jss_CN_response.text) 
            
            post = {
                    "_id": jss_json_CN_dictionary['id'], 
                    "Name": jss_json_CN_dictionary['general']['name'],
                    "Model": jss_json_CN_dictionary['hardware']['model'],
                    "Mac_OS_Verison": jss_json_CN_dictionary["operatingSystem"]['version'],
                    "CPU_Processor": jss_json_CN_dictionary['hardware']['processorType'],
                    "Total_RAM_Size": jss_json_CN_dictionary['hardware']['totalRamMegabytes'],
                    "Serial_Number": jss_json_CN_dictionary['hardware']['serialNumber'],
                    "udid": jss_json_CN_dictionary['udid'],
                    "mac_address": jss_json_CN_dictionary['hardware']['macAddress'],
                    "ip_address": jss_json_CN_dictionary['general']['lastIpAddress'],
                    "last_reported_ip": jss_json_CN_dictionary['general']['lastReportedIp'],
                    "Jamf_Pro_Version": jss_json_CN_dictionary['general']['jamfBinaryVersion']
                    }

            #print(type(jss_CN_response)) return <class 'requests.models.Response'>
            #print(type(jss_json_CN_dictionary)) return <class 'dict'>, json dictionary
            #print(type(post)) return <class 'dict'>
            
            mongodbCollection.insert_one(post)
            all_roles.append(post)

        else:
         return all_roles


 def checkOSversion(self):
        #Find OS version not equal to 11.6.0
        verCheck = mongodbCollection.find({"Mac_OS_Verison": {"$ne" : '11.6.0'}})     
        return verCheck


#def updateAttribute(self):






