"""
Author: Sujayyendhiren Ramarao Srinivasamurthi
Description: Bose soundtouch API
"""

import xml.dom.minidom

import requests
import xmltodict

from library.Utility import Utility

class Bose(object):
    """ Bose functionalities are static methods for now. Eventually
        it will be object oriented """

    #------------#
    # Best match #
    #------------#
    __IP__ = None
    __HOSTNAME__ = None
    __PERCENT_MATCH__ = 0

    @staticmethod
    def discover_boseip(devices, bosecfg):
        """ Discover IP based on configuration settings """
        matchcnt = 0
        ipmatch = hostmatch = None
        lookupstrings = bosecfg["hostdiscovery"]

        for device in devices:
            for string in lookupstrings:
                if string in device.lower():
                    ipmatch = devices[device]['ip']
                    hostmatch = device
                    matchcnt += 1

            percentmatch = (matchcnt * 100)/len(lookupstrings)
            print("Current %match: {}".format(percentmatch))
            print("Current IP: {}".format(ipmatch))

            if int(percentmatch) > int(Bose.__PERCENT_MATCH__):
                Bose.__IP__ = ipmatch
                Bose.__HOSTNAME__ = hostmatch
                Bose.__PERCENT_MATCH__ = percentmatch

    @staticmethod
    def get_bose_baseurl(option):
        """ Get basic url and other info """
        bosecfg = Utility.read_configuration(config="BOSESOUNDTOUCH")
        devices = Utility.cache("devices", "read")
        Bose.discover_boseip(devices, bosecfg)
        print("IP fetched for URL - {}".format(Bose.__IP__))
        return bosecfg["baseuri"].format( \
            boseip=Bose.__IP__, option=option)

    @staticmethod
    def get_bose_info():
        """ Get BOSE info """

        inforequest = requests.get(Bose.get_bose_baseurl("info"))

        inforesponse = xml.dom.minidom.parseString(inforequest.text)
        inforesponse_pretty = inforesponse.toprettyxml()
        jsdata = xmltodict.parse(inforesponse_pretty, xml_attribs=True)
        #print(json.dumps(jsdata, indent=4))
        return jsdata

    @staticmethod
    def change_key_attr(key):
        """ Select options """

        baseurl = Bose.get_bose_baseurl("key")

        pressxml = "<?xml version='1.0' ?><key state=\"press\" sender=\"Gabbo\">" + key + "</key>"
        press = requests.post(baseurl, data=pressxml)
        pressresponsexml = xml.dom.minidom.parseString(press.text)
        pressresponsexml_pretty = pressresponsexml.toprettyxml()
        jsdata = xmltodict.parse(pressresponsexml_pretty, xml_attribs=True)

        releasexml = "<?xml version='1.0' ?><key state=\"release\" sender=\"Gabbo\">" + key + "</key>"
        release = requests.post(baseurl, data=releasexml)
        releaseresponsexml = xml.dom.minidom.parseString(release.text)
        releaseresponsexml_pretty = releaseresponsexml.toprettyxml()
        jsdata = xmltodict.parse(releaseresponsexml_pretty, xml_attribs=True)
        return jsdata

    @staticmethod
    def check_presets():
        """ Select options """
        baseurl = Bose.get_bose_baseurl("presets")
        release = requests.post(baseurl, data="")

        print(release.status_code)
        print(release.text)
