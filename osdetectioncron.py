"""
Author: Sujayyendhiren Ramarao
Description: Run this program from cron on a periodic basis and cache the data.
             This cached data maybe read by the UI. This program needs sudo permissions
             and thus isolating this program helps us not run the flask app with sudo
             permissions
"""

import traceback
from multiprocessing import Pool

import nmap
import pysftp
from library.network import HomeNetwork
from library.Utility import Utility


def syncaches():
    """ Sync caches """

    cfg = Utility.read_configuration(configfile="haconf.yml")

    primary = cfg["CLUSTERINFO"]["primary"]
    myhostname = Utility.hostname()
    creds = cfg["CREDENTIALS"]

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    with pysftp.Connection(primary, username=creds["username"],\
         password=creds["password"], cnopts=cnopts) as sftp:
        with sftp.cd(cfg["DIRECTORY"]["syncdir"]):
            primary = primary.split('.')[0]

            if primary == myhostname:
                return

            for acache in cfg["DIRECTORY"]["getfiles"]:
                print("---GET--- {}".format(acache.format(primary)))
                sftp.get(acache.format(primary))

                print("---PUT--- {}".format(acache.format(myhostname)))
                sftp.put("cache/{0}".format(acache.format(myhostname)))


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

    return osinfo


def osdetection():
    """ Detect OS of the network devices """
    ipaddr = []

    cache = Utility.cache('devices', 'read')

    for hostname in cache:
        ipaddr.append((cache[hostname]['ip'], hostname))

    pool = Pool(processes=len(ipaddr))
    result = pool.map(oshandler, ipaddr)
    pool.close()
    pool.join()

    cache = Utility.cache('osdetection', 'write', result)

if __name__ == '__main__':
    HomeNetwork.create_tree()
    osdetection()
 
    #----------------------------------------#
    # New feature and thus skip any failures #
    #----------------------------------------#
    try:
        syncaches()
    except:
        pass
