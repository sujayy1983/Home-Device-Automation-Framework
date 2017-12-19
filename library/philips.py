"""
Author: Sujayyendhiren Ramarao
Description: Philips light controls are implemented here
"""

import json
from collections import defaultdict

import requests
from library.Utility import Utility


class Philips(object):
    """ Light class"""

    __HUEBRIDGE__ = None

    def __init__(self):
        """ Initialization if required """
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
        devices = Utility.cache("devices", "read")
        for device in devices:
            if 'hue' in device.lower() and 'philips' in device.lower():
                Philips.__HUEBRIDGE__ = devices[device]['ip']

        config = Utility.read_configuration('PHILLIPS')

        username = config['username']
        
        return config['baseuri'].format(username=username,\
                            phillipsbridgeip=Philips.__HUEBRIDGE__)

    @staticmethod
    def philips_light_colors(devid, hue, color=None, bri=254, sat=254):
        """ Philips light - Change colors """
        data = {"on": True, "bri": bri, "sat": sat}
        if color: data["hue"] = color

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
            hue['status'] = 'danger'

        try:
            hue['message'] = json.loads(response.text)[0]["success"]
        except:
            hue['message'] = response.text

    @staticmethod
    def create_dendrogram_input():
        """ Build initial dendrogram json file"""
        url = Philips.philips_baseurl()

        response = requests.get(url, data=json.dumps({}))
        jdata = json.loads(response.text)

        with open('static/data/light.template', 'r') as template:
            strtmpldata = template.read()

        fintree = {"name": "Bridge - " + Philips.__HUEBRIDGE__,
                   "href": "#",
                   "color": "black",
                   "children": []}

        for devid in jdata:
            print("Device ID - {} Name: {}".format(devid, json.dumps(jdata[devid], indent=4)))
            data = strtmpldata.replace("LIGHTNAME", jdata[devid]["name"]).replace('ID',devid)
            jsdata = json.loads(data)

            if jdata[devid]["type"] == "Dimmable light":
                jsdata["children"] = jsdata["children"][0:2]

            fintree["children"].append(jsdata)

        with open('static/data/philips.json', 'w') as ligtree:
            ligtree.write(json.dumps(fintree, indent=4))
