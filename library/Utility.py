"""
Author: Sujayyendhiren Ramarao Srinivasamurthi
Description: Reusable utilities across modules are placed here
"""

import json
import nmap
import random
import traceback
from collections import defaultdict

import yaml
import requests


class Utility(object):
    """ Utility functions """

    @staticmethod
    def read_configuration(config=None):
        """ Read configuration """
        with open("configuration/configuration.yml", 'r') as read:
            if config:
                return yaml.load(read.read())[config]
            else:
                return yaml.load(read.read())


    @staticmethod
    def cache(filename="default", action="read", data=None):
        """ Cache network data and others that can be reused """

        filepath = "cache/{0}.cache".format(filename)

        if action == "read":
            with open(filepath, 'r') as cache:
                return json.loads(cache.read())

        elif action == "write":
            with open(filepath, 'w') as cache:
                cache.write(json.dumps(data, indent=4))
                return True
        
        return False


    @staticmethod
    def create_tree():
        """ """
        xbase = 150; ybase = 150; xrandmax = 350; yrandmax = 350; gw=None
        nm = nmap.PortScanner()
        homenw = Utility.read_configuration(config="HOME_NETWORK")

        devices = defaultdict(list); cdevices = defaultdict(dict)

        nm.scan(hosts=homenw, arguments='')
        scanned = nm.all_hosts()
        
        for idx, host in enumerate(scanned, start=1):

            print(json.dumps(nm[host], indent=4))

            macaddr  = nm[host]['addresses']['mac'] if 'mac' \
                        in nm[host]['addresses'] else ''
            hostname = nm[host]['hostnames'][0]['name'].split(".")[0]
            xrand = random.randint(1,xrandmax)
            yrand = random.randint(1,yrandmax)

            if host.endswith('.1'):
                gw = host 
                xrand = (150 + xrandmax)/2
                yrand = (150 + yrandmax)/2

            devices["nodes"].append({"name": hostname, 
                                    "id":  host,
                                    "x":xbase + xrand , 
                                    "y": ybase + yrand,
                                    "group": idx, "mac": macaddr
                                    })

            if len(hostname) == 0: hostname = host

            cdevices[hostname]['ip']  = host
            cdevices[hostname]['mac'] = macaddr

            if host != gw: 
                devices["links"].append({"source":  "", "target":  host})
        
        if gw != None:
            for link in devices["links"]:
                link["source"]  = gw

        with open("static/data/graph.json", 'w') as jswrt:
            jswrt.write(json.dumps(devices, indent=4))

        Utility.cache("devices", action="write", data=cdevices)


    @staticmethod
    def phillips_baseurl():
        huebridgeip = None; devices = Utility.cache("devices", "read")
        
        for device in devices:
            if 'hue' in device.lower() and 'philips' in device.lower():
                huebridgeip = devices[device]['ip']

        config = Utility.read_configuration('PHILLIPS')

        username = config['username']
        return config['baseuri'].format(username=username,\
                            phillipsbridgeip=huebridgeip)


    @staticmethod
    def get_basic_info():
        """ Get info about lights """
        url = Utility.phillips_baseurl()

        print("Phillips info URL: {0}".format(url))
        lightinfo = defaultdict(dict)
        response = requests.get(url, data=json.dumps({}))
        jdata = json.loads(response.text)

        for id in jdata:
            print("ID: {0}".format(id))
            lightinfo[id]["state"] = jdata[id]["state"]["on"]
            lightinfo[id]["name"] = jdata[id]["name"]
            lightinfo[id]["modelid"] = jdata[id]["modelid"]
            lightinfo[id]["swversion"] = jdata[id]["swversion"] 

            if jdata[id]["state"]["on"] == True:
                lightinfo[id]["color"] = 'success'
            else:
                lightinfo[id]["color"] = 'warning'

        return lightinfo


    @staticmethod
    def phillips_light_switch(toggle, hue):
        """ Phillips light - Change switch """    
        data = {"on": True}
        hue['msghead'] = "Request fulfilled"; hue["status"] = 'success'

        baseurl = Utility.phillips_baseurl()
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
    
    @staticmethod
    def appletv_baseurl(action):
        """ Apple TV baseurl """
        appletvip = None; devices = Utility.cache("devices", "read")
        
        for device in devices:
            if 'apple' in device.lower() and 'tv' in device.lower():
                appletvip = devices[device]['ip']

        config = Utility.read_configuration('APPLETV')

        return config['baseuri'].format(action=action,\
                                     appletvip=appletvip)


    @staticmethod
    def appletv_processing(action):

        url = Utility.appletv_baseurl(action)

        print("URL: {0}".format(url))
        response = requests.put(url, data=json.dumps({}))

        print(response.status_code)
        print(response.text)

        return True
