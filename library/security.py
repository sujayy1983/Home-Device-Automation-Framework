"""
    Author: Sujayyendhiren Ramarao Srinivasamurthi
    Description: Security stuff is here
"""

import json
import socket
import random

from collections import defaultdict
import scapy.all as scapy


class Security(object):
    """ Networking and security functionalities """

    @staticmethod
    def traceroute(destination, minttl=1, maxttl=24, dport=33434, trtype='udp'):
        """ Traceroute """

        results = [] 

        for ttl in range(minttl, maxttl):

            pkt = scapy.IP(dst=destination, ttl=ttl) / scapy.UDP(dport=random.randint(33434, 33534))

            # --------------------------------- #
            #  Send the packet and get a reply  #
            # --------------------------------- #
            reply = scapy.sr1(pkt, verbose=0)

            if ttl == 1:
                print(dir(reply))

            if reply is None:
                print("Exiting as no reply ... ")
                results.append((ttl, "Exiting no reply", None, None))
                break

            elif reply.type == 3:
                print("Done {} hops away: {} {} {}".format(ttl, reply.src, reply.type, reply.time))
                results.append((ttl, reply.src, reply.time, reply.type))
                break

            else:
                print("{} hops away {} {} {}".format(ttl, reply.src, reply.type, reply.time))
                results.append((ttl, reply.src, reply.time, reply.type))

        return results

    @staticmethod
    def generate_results(targethostname, filename):
        """ """

        retresults = defaultdict(list)

        src = socket.gethostname()
        results = Security.traceroute(targethostname)

        retresults['nodes'].append({"hostname":src, "ip": src, "x": 10, "y": 10, "color": "rgb({}, {}, {})".format(100, 100, 100)})

        for idx, result in enumerate(results):
            elem = {}
            ttl, nxthop, time, type = result

            hostname = None
        
            try:    
                hostname = socket.gethostbyname(nxthop)
            except:
                hostname = nxthop

            color = "rgb({}, {}, {})".format(50, 150, 255) 

            if idx+1 == len(results):
                color = "rgb({}, {}, {})".format(100, 100, 100) 
                hostname = targethostname

            retresults['nodes'].append({"hostname": hostname, "ip": nxthop, "x": 10+idx*3, "y": 10+idx*3, "color": color})

            elem['source'] = src
            elem['target'] = nxthop  
            retresults['links'].append(elem)
            src = nxthop   

        with open(filename, 'w') as fd:
            fd.write(json.dumps(retresults, indent=4))

    @staticmethod
    def test_results(targethostname, filename):
        """ """

        retresults = defaultdict(list)
        src = socket.gethostname()
        srcid = "0"
        results = Security.traceroute(targethostname)

        retresults['nodes'].append({"id": "0", "group": "1", "hostname": src, "ip": src})

        for idx, result in enumerate(results):
            ttl, nxthop, time, ttype = result

            group = ttl%3 + 1
        
            if idx+1 == len(results):
                group = 1

            retresults['nodes'].append({"id": str(ttl), "hostname": nxthop, "ip": nxthop, "group": str(group), "hostname": nxthop})

            retresults['links1'].append({"id": str(idx), "source": srcid, "target": str(ttl)})
            srcid = str(idx)

        with open(filename, 'w') as fd:
            fd.write(json.dumps(retresults, indent=4))

if __name__ == '__main__':
    """ Traceroute entry point """
    Security.generate_results('www.facebook.com', "../static/data/traceroute.json")
