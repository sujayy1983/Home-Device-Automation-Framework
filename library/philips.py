"""
Author: Sujayyendhiren Ramarao
Description: Philips light controls are implemented here
"""

import json
import requests

from collections import defaultdict
from library.Utility import Utility

class Philips(object):
    
    def __init__(self):
        pass
    
    @staticmethod
    def get_basic_info():
        """ Get info about lights """
        url = Philips.philips_baseurl()

        print("Phillips info URL: {0}".format(url))
        lightinfo = defaultdict(dict)
        response = requests.get(url, data=json.dumps({}))
        jdata = json.loads(response.text)

        for devid in jdata:
            print("ID: {0}".format(devid))
            lightinfo[devid]["state"] = jdata[devid]["state"]["on"]
            lightinfo[devid]["name"] = jdata[devid]["name"]
            lightinfo[devid]["modelid"] = jdata[devid]["modelid"]
            lightinfo[devid]["swversion"] = jdata[devid]["swversion"] 

            if jdata[devid]["state"]["on"] is True:
                lightinfo[devid]["color"] = 'success'
            else:
                lightinfo[devid]["color"] = 'warning'

        return lightinfo

    @staticmethod
    def philips_baseurl():
        """ Format baseurl for Phillips Hue bridge """
        huebridgeip = None; devices = Utility.cache("devices", "read")
        
        for device in devices:
            if 'hue' in device.lower() and 'philips' in device.lower():
                huebridgeip = devices[device]['ip']

        config = Utility.read_configuration('PHILLIPS')

        username = config['username']
        return config['baseuri'].format(username=username,\
                            phillipsbridgeip=huebridgeip)

    @staticmethod
    def philips_light_colors(devid, color, hue, bri=254, sat=254):
        """ Philips light - Change colors """    
        data = {"on": True, 
                "hue": color,
                "bri": bri, 
                "sat": sat}

        hue['msghead'] = "Request fulfilled"; hue["status"] = 'success'

        baseurl = Philips.philips_baseurl()
        url = "{0}/{1}/state".format(baseurl, devid)

        response = requests.put(url, data=json.dumps(data))
        print("URL: {0} Resp code: {1}".format(url, response.status_code))

    @staticmethod
    def philips_light_switch(toggle, hue):
        """ Philips light - Toggle ON/OFF """    
        data = {"on": True}
        hue['msghead'] = "Request fulfilled"; hue["status"] = 'success'

        baseurl = Philips.philips_baseurl()
        url = "{0}/{1}/state".format(baseurl, int(toggle/10))

        if toggle & 0x1 != 0x1:
            data["on"] = False

        print("URL: {0}".format(url))
        response = requests.put(url, data=json.dumps(data))

        if response.status_code != 200:
            hue['msghead'] = "Failure"
            hue['status']  = 'danger'

        try:
            hue['message'] = json.loads(response.text)[0]["success"]
        except:
            hue['message'] = response.text
