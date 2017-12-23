"""
Author: Sujayyendhiren Ramarao Srinivasamurthi
Description: Network discovery and other network related features move here shortly.
"""

import json
import socket
import random
from collections import defaultdict
from scapy.all import srp, Ether, ARP
from library.Utility import Utility

class HomeNetwork(object):
    """ Home network and other properties discovery """

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

            import math
            radius = 25
            yoncircle = x = base 


            if not ipaddr.endswith('.1'):
                devices["links"].append({"source":  "", "target":  ipaddr})
                x += random.randint(-20, base+200)
                integer = radius*radius - (x-base)*(x-base)
                if integer < 0: integer = integer * (-1)
                yoncircle += math.sqrt(integer)
            else:
                gatewway = ipaddr

            devices["nodes"].append({"name": hostname, "id": ipaddr,\
                "x" : x,\
                "y" : yoncircle,\
                "group": idx, "mac": mac})

            cdevices[hostname]['ip'] = ipaddr
            cdevices[hostname]['mac'] = mac



        for link in devices["links"]:
            link["source"] = gatewway

        with open("static/data/graph.json", 'w') as jswrt:
            jswrt.write(json.dumps(devices, indent=4))

        Utility.cache("devices", action="write", data=cdevices)