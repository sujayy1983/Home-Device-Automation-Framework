"""
Author: Sujayyendhiren Ramarao Srinivasamurthi
Description: Reusable utilities across modules are placed here
"""

import json
import socket
import random
from collections import defaultdict

import yaml
import nmap
import requests
from scapy.all import srp, Ether, ARP


class Utility(object):
    """ Utility functions """

    @staticmethod
    def read_configuration(config=None):
        """ Read configuration """
        with open("configuration/configuration.yml", 'r') as read:
            if config:
                config = yaml.load(read.read())[config]
            else:
                config = yaml.load(read.read())
            return config

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

        pscan = nmap.PortScanner()
        pscan.scan(hosts=ipaddr, arguments='-O')
        pscan.all_hosts()
        print('-'*70)
        print("Ipaddr: {} Hostname: {}".format(ipaddr, hostname))
        print('-'*70)

        if 'osclass' in pscan[ipaddr]:
            for osclass in pscan[ipaddr]['osclass']:
                print('OsClass.type : {0}'.format(osclass['type']))
                print('OsClass.vendor : {0}'.format(osclass['vendor']))
                print('OsClass.osfamily : {0}'.format(osclass['osfamily']))
                print('OsClass.osgen : {0}'.format(osclass['osgen']))
                print('OsClass.accuracy : {0}'.format(osclass['accuracy']))
                print('-'*70)
                return (hostname, osclass, 'type1')

        if 'osmatch' in pscan[ipaddr]:
            for osmatch in pscan[ipaddr]['osmatch']:
                print('osmatch.name : {0}'.format(osmatch['name']))
                print('osmatch.accuracy : {0}'.format(osmatch['accuracy']))
                print('osmatch.line : {0}'.format(osmatch['line']))
                print('-'*70)
                return (hostname, osmatch, 'type2')

        if 'fingerprint' in pscan[ipaddr]:
            print('Fingerprint : {0}'.format(pscan[ipaddr]['fingerprint']))
            print('-'*70)
            return (hostname, pscan[ipaddr]['fingerprint'], 'type3')

    @staticmethod
    def appletv_baseurl(action):
        """ Apple TV baseurl """
        appletvip = None
        devices = Utility.cache("devices", "read")

        for device in devices:
            if 'apple' in device.lower() and 'tv' in device.lower():
                appletvip = devices[device]['ip']

        config = Utility.read_configuration('APPLETV')

        return config['baseuri'].format(action=action,\
                                     appletvip=appletvip)

    @staticmethod
    def appletv_processing(action):
        """ Apple TV related info shall be added here """
        url = Utility.appletv_baseurl(action)

        print("URL: {0}".format(url))
        response = requests.put(url, data=json.dumps({}))

        print(response.status_code)
        print(response.text)

        return True

    @staticmethod
    def create_tree():
        """ Faster network discovery with scapy """
        base = 150
        gatewway = None
        devices = defaultdict(list)
        cdevices = defaultdict(dict)

        homenw = Utility.read_configuration(config="HOME_NETWORK")
        alive, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=homenw),\
                                timeout=2, verbose=0)

        for idx in range(0, len(alive)):

            mac = ipaddr = hostname = None

            try:
                hname, _, _ = socket.gethostbyaddr(alive[idx][1].psrc)
                mac = alive[idx][1].hwsrc
                ipaddr = alive[idx][1].psrc
                hostname = hname.split(".")[0]
            except:
                mac = alive[idx][1].hwsrc
                ipaddr = alive[idx][1].psrc
                hostname = alive[idx][1].psrc

            devices["nodes"].append({"name": hostname, "id": ipaddr,\
                "x" : base + random.randint(1, base+200),\
                "y" : base + random.randint(1, base+200),\
                "group": idx, "mac": mac})

            cdevices[hostname]['ip'] = ipaddr
            cdevices[hostname]['mac'] = mac

            if not ipaddr.endswith('.1'):
                devices["links"].append({"source":  "", "target":  ipaddr})
            else:
                gatewway = ipaddr

        for link in devices["links"]:
            link["source"] = gatewway

        with open("static/data/graph.json", 'w') as jswrt:
            jswrt.write(json.dumps(devices, indent=4))

        Utility.cache("devices", action="write", data=cdevices)
