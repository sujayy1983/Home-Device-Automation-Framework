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
        self.available = []
        #------------------------------------#
        # Maintain one instance of a service #
        #------------------------------------#
        self.activeprocesses = {}
        rootdir = '~/AIY-voice-kit-python'
        programs = {"gassistant": 'src/assistant_library_demo.py'}
        #------------------------------#
        # Check if a service available #
        #------------------------------#
        for service in programs:
            if os.path.isfile("{0}/{1}".format(rootdir, programs[service])):
                self.available.append((rootdir, service))

    def start(self, service):
        """ Start a program """

        if service not in self.available:
            raise Exception("Invalid service - {0}".format(service))

        for _, availservice in self.available:
            if availservice == service and service not in self.activeprocesses:
                #Create an active process
                pass

    def stop(self, service):
        """ Stop a program """

        if service in self.activeprocesses:
            pass
