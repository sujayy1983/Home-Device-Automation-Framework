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
from library.network import HomeNetwork
from library.Utility import Utility


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
    cache = Utility.cache('devices', 'read')

    for hostname in cache:
        ipaddr.append((cache[hostname]['ip'], hostname))

    pool = Pool(processes=len(ipaddr))
    results = pool.map(oshandler, ipaddr)
    pool.close()
    pool.join()

    newstruct = defaultdict(list)
    osfailure = []

    for aresult in results:
        if 'exception' not in aresult:
            newstruct['cpe'].append(aresult['cpe'][0].replace(":", "_"))
            newstruct['ip'].append(aresult['ip'])
            newstruct['hostname'].append(aresult['hostname'])
            newstruct['osvendor'].append(aresult['vendor'])
            newstruct['osname'].append(aresult['name'])
            newstruct['ostype'].append(aresult['type'])
            newstruct['osgen'].append(aresult['osgen'])
            newstruct['osfamily'].append(aresult['osfamily'])
            newstruct['osaccuracy'].append(aresult['accuracy'])
        else:
            print(json.dumps(aresult, indent=4))
            osfailure.append(aresult)

    HomeNetwork.add_update_rows(newstruct)
    Utility.cache('osdetection', 'write', newstruct)
    Utility.cache('osdetectfailed', 'write', osfailure)


def cleanup():
    """ Cleanup previously network topology temp data """

    for afile in glob("static/data/networkdata-*.json"):
        os.remove(afile)

if __name__ == '__main__':
    HomeNetwork.create_tree()
    osdetection()
    cleanup()
