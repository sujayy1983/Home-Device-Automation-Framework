"""
    Description: AIY Google kit controls are implemented here.
"""

import os
import json

from library.Utility import Utility

class Aiy(object):
    """ Google voice kit controls """

    #----------------------------#
    # Currently running services #
    #----------------------------#
    def __init__(self):
        """ Initializations and/or discovery """

        aiycfg = Utility.read_configuration(config="AIYKIT")
        self.rootdir = aiycfg["rootdir"]

        #----------------------#
        # Available service(s) #
        #----------------------#
        self.available = {}

        #------------------------------#
        # Check if a service available #
        #------------------------------#
        for service in aiycfg["services"]:
            if os.path.isfile("{0}/{1}".format(self.rootdir, \
                aiycfg["services"][service])):
                self.available[service] = "Available"
            else:
                self.available[service] = "Not available on this host."

        self.activeservice = Utility.cache("aiyactiveservice", "read")

    def start(self, service):
        """ Start a program """

        print("InStart - Avl services {}".format(self.available))

        if service not in self.available:
            raise Exception("Invalid service - {0}".format(service))
        elif  self.available[service] != "Available":
            raise Exception("Service - [{}] not installed".format(service))

        for availservice in self.available:
            if availservice == service and service not in self.activeservice:
                print("Starting service - {}".format(service))
                os.system("sudo systemctl start {0}.service".format(service))
                self.activeservice[service] = "active"
            elif service in self.activeservice:
                print("InStart - Service {} already active ... ".format(service))

    def stop(self, service):
        """ Stop a program """
        if service in self.activeservice:
            print("Stopping {}".format(service))
            os.system("sudo systemctl stop {0}.service".format(service))
            del self.activeservice[service]

    def process_request(self, service, action):
        """ Process requests for action to be taken on
            a service.
        """
        function = getattr(self, action)
        retval = function(service)
        Utility.cache("aiyactiveservice", "write", self.activeservice)
        return retval
