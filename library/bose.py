"""
Author: Sujayyendhiren Ramarao Srinivasamurthi
Description: Bose soundtouch API
"""

import json
import requests
import xmltodict
import xml.dom.minidom

from library.Utility import Utility


def get_bose_baseurl(option):
    bosecfg = Utility.read_configuration("BOSESOUNDTOUCH")
    boseip = None; devices = Utility.cache("devices", "read")
        
    for device in devices:
        if 'touch' in device.lower() and 'sound' in device.lower():
            boseip = devices[device]['ip']

    return bosecfg["baseuri"].format(boseip=boseip, option=option)


def get_bose_info():
    """ Get BOSE info """

    infoRequest = requests.get(get_bose_baseurl("info"))

    infoResponseXML = xml.dom.minidom.parseString(infoRequest.text)
    infoResponseXML_pretty = infoResponseXML.toprettyxml()    
    jsdata = xmltodict.parse(infoResponseXML_pretty, xml_attribs=True)
    #print(json.dumps(jsdata, indent=4))
    return jsdata


def change_key_attr(key):
    """ Select options """

    baseurl = get_bose_baseurl("key")

    pressXML = "<?xml version='1.0' ?><key state=\"press\" sender=\"Gabbo\">" + key + "</key>"
    press = requests.post(baseurl, data=pressXML)
    pressResponseXML = xml.dom.minidom.parseString(press.text)
    pressResponseXML_pretty = pressResponseXML.toprettyxml()
    jsdata = xmltodict.parse(pressResponseXML_pretty, xml_attribs=True)
    
    releaseXML = "<?xml version='1.0' ?><key state=\"release\" sender=\"Gabbo\">" + key + "</key>"
    release = requests.post(baseurl, data=releaseXML)
    releaseResponseXML = xml.dom.minidom.parseString(release.text)
    releaseResponseXML_pretty = releaseResponseXML.toprettyxml()
    jsdata = xmltodict.parse(releaseResponseXML_pretty, xml_attribs=True)
    return jsdata


def check_presets(key):
    """ Select options """
    baseurl = get_bose_baseurl("presets")
    release = requests.post(baseurl, data="")

    print(release.status_code)
    print(release.text)
