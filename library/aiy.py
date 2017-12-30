"""
    Description: AIY Google kit controls are implemented here.
"""

import os

from library.Utility import Utility

class Aiy(object):
    """ Google voice kit controls """

    #----------------------------#
    # Currently running services #
    #----------------------------#
    __ACTIVESRV__ = {}

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

    def start(self, service):
        """ Start a program """
        if service not in self.available:
            raise Exception("Invalid service - {0}".format(service))
        elif  self.available[service] != "Available":
            raise Exception("Service - [{}] not installed".format(service))

        for availservice in self.available:
            if availservice == service and service not in Aiy.__ACTIVESRV__:
                os.system("sudo systemctl start {0}.service".format(service))
                Aiy.__ACTIVESRV__[service] = None

    def stop(self, service):
        """ Stop a program """
        if service in Aiy.__ACTIVESRV__:
            os.system("sudo systemctl stop {0}.service".format(service))
            del Aiy.__ACTIVESRV__[service]

    def process_request(self, service, action):
        """ Process requests for action to be taken on
            a service.
        """
        function = getattr(self, action)
        return function(service)
