"""
Author: Sujayyendhiren Ramarao
Description: Run this program from cron on a periodic basis and cache the data.
             This cached data maybe read by the UI. This program needs sudo permissions
             and thus isolating this program helps us not run the flask app with sudo
             permissions
"""
import os
import json
import traceback

from glob import glob
from collections import defaultdict
from multiprocessing import Pool

import nmap
import pysftp

from highlander import one
from library.network import HomeNetwork


def oshandler(iphost):
    """ Scan device(s) OS"""

    osinfo = {}

    ipaddr, hostname = iphost

    pscan = nmap.PortScanner()
    pscan.scan(hosts=ipaddr, arguments='-O')
    pscan.all_hosts()

    print('-'*70)
    print("Hostname: {}".format(hostname))
    print('-'*70)

    try:
        if 'osclass' in pscan[ipaddr]:
            for osclass in pscan[ipaddr]['osclass']:
                print('OsClass.type : {0}'.format(osclass['type']))
                print('OsClass.vendor : {0}'.format(osclass['vendor']))
                print('OsClass.osfamily : {0}'.format(osclass['osfamily']))
                print('OsClass.osgen : {0}'.format(osclass['osgen']))
                print('OsClass.accuracy : {0}'.format(osclass['accuracy']))
                print('-'*70)
                osinfo = osclass
                break

        if 'osmatch' in pscan[ipaddr]:
            for osmatch in pscan[ipaddr]['osmatch']:
                print('osmatch.name : {0}'.format(osmatch['name']))
                print('osmatch.accuracy : {0}'.format(osmatch['accuracy']))
                print('osmatch.line : {0}'.format(osmatch['line']))
                print('-'*70)
                osinfo = osmatch
                break

        if 'fingerprint' in pscan[ipaddr]:
            print('Fingerprint : {0}'.format(pscan[ipaddr]['fingerprint']))
            print('-'*70)
            osinfo = pscan[ipaddr]['fingerprint']
    except:
        osinfo["exception"] = traceback.format_exc()
    finally:
        osinfo["ip"] = ipaddr
        osinfo["hostname"] = hostname

        if 'osclass' in osinfo:
            osinfo.update(osinfo['osclass'][0])
            del osinfo['osclass']
    return osinfo


def osdetection():
    """ Detect OS of the network devices """
    ipaddr = []

    for hostname in HomeNetwork.get_allhosts():
        ipaddr.append((HomeNetwork.get_hostname_specificdata(hostname, 'ip'), hostname))

    if not ipaddr:
        return

    pool = Pool(processes=len(ipaddr))
    results = pool.map(oshandler, ipaddr)
    pool.close()
    pool.join()

    newstruct = defaultdict(dict)
    osfailure = []

    for aresult in results:
        if 'exception' not in aresult:
            hostname = aresult['hostname']
            newstruct[hostname]['cpe'] = aresult['cpe'][0].replace(":", "_")
            newstruct[hostname]['ip'] = aresult['ip']
            newstruct[hostname]['hostname'] = hostname
            newstruct[hostname]['osvendor'] = aresult['vendor']
            newstruct[hostname]['osname'] = aresult['name']
            newstruct[hostname]['ostype'] = aresult['type']
            newstruct[hostname]['osgen'] = aresult['osgen']
            newstruct[hostname]['osfamily'] = aresult['osfamily']
            newstruct[hostname]['osaccuracy'] = aresult['accuracy']
        else:
            print(json.dumps(aresult, indent=4))
            osfailure.append(aresult)

    HomeNetwork.add_update_rows(newstruct)


def complete_setup():
    """ Cleanup previously network topology temp data """

    for afile in glob("static/data/networkdata-*.json"):
        os.remove(afile)

    HomeNetwork.hasync()

@one()
def entrypoint():
    """ Runs only a single instance of a process """
    HomeNetwork.initializetable(perms=True)
    HomeNetwork.create_tree()
    osdetection()
    complete_setup()

if __name__ == '__main__':
    entrypoint()
