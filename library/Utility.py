"""
Author: Sujayyendhiren Ramarao Srinivasamurthi
Description: Reusable utilities across modules are placed here
"""

import json
import nmap
import random

import socket
import traceback
from collections import defaultdict

import yaml
import requests

from scapy.all import *


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
    def os_detection(iphost):
        """ Detect OS of a device """

        ipaddr, hostname = iphost

        nm = nmap.PortScanner()
        nm.scan(hosts=ipaddr, arguments='-O')
        nm.all_hosts()
        
        print('-'*70)
        print("Ipaddr: {} Hostname: {}".format(ipaddr, hostname))
        print('-'*70)

        if 'osclass' in nm[ipaddr] :
            for osclass in nm[ipaddr]['osclass']:
                print('OsClass.type : {0}'.format(osclass['type']))
                print('OsClass.vendor : {0}'.format(osclass['vendor']))
                print('OsClass.osfamily : {0}'.format(osclass['osfamily']))
                print('OsClass.osgen : {0}'.format(osclass['osgen']))
                print('OsClass.accuracy : {0}'.format(osclass['accuracy']))
                print('-'*70)
                return (hostname, osclass, 'type1')

        if 'osmatch' in nm[ipaddr]:
            for osmatch in nm[ipaddr]['osmatch']:
                print('osmatch.name : {0}'.format(osmatch['name']))
                print('osmatch.accuracy : {0}'.format(osmatch['accuracy']))
                print('osmatch.line : {0}'.format(osmatch['line']))
                print('-'*70)
                return (ipaddr, osmatch, 'type2')

        if 'fingerprint' in nm[ipaddr]:
            print('Fingerprint : {0}'.format(nm[ipaddr]['fingerprint']))
            print('-'*70)
            return (ipaddr, nm[ipaddr]['fingerprint'], 'type3')


    @staticmethod
    def phillips_baseurl():
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
        """ Phillips light - Toggle ON/OFF """    
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
    def phillips_light_colors(id, color, hue, bri=254, sat=254):
        """ Phillips light - Change colors """    
        data = {"on": True, 
                "hue": color,
                "bri": bri, 
                sat: sat}

        hue['msghead'] = "Request fulfilled"; hue["status"] = 'success'

        baseurl = Utility.phillips_baseurl()
        url = "{0}/{1}/state".format(baseurl, id)

        print("URL: {0}".format(url))
        response = requests.put(url, data=json.dumps(data))


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


    @staticmethod
    #def create_scapy_tree():
    def create_tree():
        """ Faster network discovery with scapy """

        devices = defaultdict(list); cdevices = defaultdict(dict)
        xbase = 150; ybase = 150; xrandmax = 350; yrandmax = 350; gw=None

        homenw = Utility.read_configuration(config="HOME_NETWORK")
        alive, dead = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=homenw),\
                                timeout=2, verbose=0)

        for idx in range(0,len(alive)):

            mac = None; ip = None; hostname = None

            try:
                hname, _a_, _b_ = socket.gethostbyaddr(alive[idx][1].psrc)
                mac = alive[idx][1].hwsrc; ip  = alive[idx][1].psrc
                hostname = hname.split(".")[0]
            except:
                mac = alive[idx][1].hwsrc; ip  = alive[idx][1].psrc
                hostname = alive[idx][1].psrc
            
            devices["nodes"].append(
                    {"name": hostname, 
                       "id":  ip,
                       "x" : xbase + random.randint(1,xrandmax),
                       "y" : ybase + random.randint(1,yrandmax),
                    "group": idx, "mac": mac
                    })
            
            cdevices[hostname]['ip']  = ip; cdevices[hostname]['mac'] = mac

            if not ip.endswith('.1'): 
                devices["links"].append({"source":  "", "target":  ip})
            else:
                gw = ip

        for link in devices["links"]:
            link["source"]  = gw

        with open("static/data/graph.json", 'w') as jswrt:
            jswrt.write(json.dumps(devices, indent=4))

        Utility.cache("devices", action="write", data=cdevices)
