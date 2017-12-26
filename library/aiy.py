"""
    Description: AIY Google kit controls are implemented here.
"""

import os

from library.Utility import Utility

class Aiy(object):
    """ Google voice kit controls """

    def __init__(self):
        """ Initializations and/or discovery """

        aiycfg = Utility.read_configuration(config="AIYKIT")
        self.rootdir = aiycfg["rootdir"]

        #----------------------#
        # Available service(s) #
        #----------------------#
        self.available = {}
        self.activeprocesses = {}

        #------------------------------#
        # Check if a service available #
        #------------------------------#
        for service in aiycfg["services"]:
            if os.path.isfile("{0}/{1}".format(self.rootdir, \
                aiycfg["services"][service])):
                self.available[service] = "Available"
            else:
                self.available[service] = "Not available on this host."

    def start(self, service):
        """ Start a program """
        print("Start service: {}@{}".format(self.rootdir, service))
        os.system("sudo systemctl start gassistant.service")
        if service not in self.available:
            raise Exception("Invalid service - {0}".format(service))
        elif  isinstance(self.available[service], str):
            raise Exception("Service - [{}] not installed".format(service))

        for availservice in self.available:
            if availservice == service and service not in self.activeprocesses:
                self.activeprocesses[service] = None

    def stop(self, service):
        """ Stop a program """
        print("Start service: {}@{}".format(self.rootdir, service))
        os.system("sudo systemctl stop gassistant.service")
        if service in self.activeprocesses:
            print("Start service: {}".format(service))

    def process_request(self, service, action):
        """ Process requests for action to be taken on
            a service.
        """
        function = getattr(self, action)
        return function(service)
