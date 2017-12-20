"""
Author: Sujayyendhiren Ramarao Srinivasamurthi
Description: Reusable utilities across modules are placed here
"""

import json

import yaml
import requests


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

