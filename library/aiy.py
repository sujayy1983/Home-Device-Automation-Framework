"""
    Description: AIY Google kit controls are implemented here.
"""

import os

class Aiy(object):
    """ Google voice kit controls """

    def __init__(self):
        """ Initializations and/or discovery """
        #----------------------#
        # Available service(s) #
        #----------------------#
        self.available = {}
        #------------------------------------#
        # Maintain one instance of a service #
        #------------------------------------#
        self.activeprocesses = {}
        self.rootdir = '~/AIY-voice-kit-python'
        programs = {"gassistant": 'src/assistant_library_demo.py'}
        #------------------------------#
        # Check if a service available #
        #------------------------------#
        for service in programs:
            if os.path.isfile("{0}/{1}".format(self.rootdir, \
                programs[service])):
                self.available[service] = True
            else:
                self.available[service] = "Not installed."

    def start(self, service):
        """ Start a program """
        if service not in self.available:
            raise Exception("Invalid service - {0}".format(service))
        elif  isinstance(self.available[service], str):
            raise Exception("Service - [{}] not installed".format(service))

        for availservice in self.available:
            if availservice == service and service not in self.activeprocesses:
                print("Start service: {}@{}".format(self.rootdir, service))
                self.activeprocesses[service] = None

    def stop(self, service):
        """ Stop a program """
        if service in self.activeprocesses:
            print("Start service: {}".format(service))

    def process_request(self, service, action):
        """ Process requests for action to be taken on
            a service.
        """
        function = getattr(self, action)
        return function(service)
