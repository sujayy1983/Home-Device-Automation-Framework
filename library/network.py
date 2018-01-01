"""
Author: Sujayyendhiren Ramarao Srinivasamurthi
Description: Network discovery and other network related features move here shortly.
"""

import os
import json
import socket
import random
import pysftp
import sqlite3
import traceback
from shutil import chown
from datetime import datetime
from collections import defaultdict

import pandas
from scapy.all import srp, Ether, ARP
from library.Utility import Utility

class HomeNetwork(object):
    """ Home network and other properties discovery """

    @staticmethod
    def initializetable(perms=False):
        """ Initialize a sqlite3 device table """
        cfg = Utility.read_configuration(config="DEVICEDETECT")

        if not os.path.exists(cfg["devicedb"]):
            connection = sqlite3.connect(cfg["devicedb"])
            dataframe = pandas.read_csv("templates/devicetable.csv")
            dataframe.to_sql(cfg["tablename"], connection, index=False)
        
        if perms:
            permscfg = Utility.read_configuration(config="CACHEPERMS")
            chown(cfg["devicedb"], permscfg["user"], permscfg["group"])

    @staticmethod
    def get_connection_info(haconf=False):
        """ Get connection info and table name """
        cfg = Utility.read_configuration(config="DEVICEDETECT")

        if haconf:
            from glob import glob
            # Read one other than cfg["devicedb"]
            dbs = glob("cache/*devices.db")

            for db in dbs:
                if db != cfg["devicedb"]:
                    return sqlite3.connect(db), cfg["tablename"]
        else:
            return sqlite3.connect(cfg["devicedb"]), cfg["tablename"]

    @staticmethod
    def add_update_rows(rowinfo, init=False):
        """ sqlite into dataframe """

        try:
            connection, tablename = HomeNetwork.get_connection_info()
            query = "SELECT * from {table}".format(table=tablename)

            dbdata = pandas.read_sql_query(query, connection).to_json(orient='records')
            dbdata = json.loads(dbdata)

            #------------#
            # Slave info #
            #------------#
            haconnection, hatablename = HomeNetwork.get_connection_info()
            query = "SELECT * from {table}".format(table=hatablename)

            hadbdata = pandas.read_sql_query(query, haconnection).to_json(orient='records')
            hadbdata = json.loads(hadbdata)

            easylkup = {}
            for entry in dbdata + hadbdata:
                easylkup[entry['hostname']] = entry

            dfdata = []
            for hostname in rowinfo:
                rowinfo[hostname]['datetime'] = str(datetime.now())

                if hostname in easylkup:
                    easylkup[hostname].update(rowinfo[hostname])
                    dfdata.append(easylkup[hostname])
                else:
                    dfdata.append(rowinfo[hostname])

            dataframe = pandas.DataFrame(dfdata)
            dataframe.to_sql(tablename, connection, index=False, if_exists='replace')
            return True
        except:
            print(traceback.format_exc())
            return False

    @staticmethod
    def read_sqlite3_current(jsondata=False):
        """ Get current entries in the database """
        connection, tablename = HomeNetwork.get_connection_info()
        query = "SELECT * from {table}".format(table=tablename)

        if jsondata:
            return pandas.read_sql_query(query, connection).to_json(orient='records')

        return pandas.read_sql_query(query, connection)

    @staticmethod
    def get_hostname_specificdata(host, index=None):
        """ Get relevant entry from the database """
        connection, tablename = HomeNetwork.get_connection_info()
        query = 'SELECT * from {0} WHERE hostname="{1}"'.format(\
                    tablename, host)
        output = pandas.read_sql_query(query, connection).to_json(orient='records')

        if index:
            for hostinfo in json.loads(output):
                if hostinfo["hostname"] == host and index in hostinfo:
                    return hostinfo[index]
        else:
            return json.loads(output)

    @staticmethod
    def get_allhosts():
        """ Get all hosts in the sqlite3 db """
        connection, tablename = HomeNetwork.get_connection_info()
        query = 'SELECT hostname from {}'.format(tablename)
        output = pandas.read_sql_query(query, connection).to_json(orient='records')

        for host in json.loads(output):
            yield host["hostname"]

    @staticmethod
    def create_tree():
        """ Faster network discovery with scapy """
        basey = 960/2
        basex = 600/2
        newstruct = defaultdict(dict)
        homenw = Utility.read_configuration(config="HOME_NETWORK")
        alive, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=homenw),\
                                timeout=2, verbose=0)

        for idx in range(0, len(alive)):
            try:
                hname, _, _ = socket.gethostbyaddr(alive[idx][1].psrc)
                hostname = hname.split(".")[0]
            except:
                hostname = alive[idx][1].psrc

            mac = alive[idx][1].hwsrc
            ipaddr = alive[idx][1].psrc
            xcoord = random.randint(0, 2*basex)
            ycoord = random.randint(0, 2*basey)

            newstruct[hostname]['ip'] = ipaddr
            newstruct[hostname]['mac'] = mac
            newstruct[hostname]['hostname'] = hostname
            newstruct[hostname]['x'] = xcoord
            newstruct[hostname]['y'] = ycoord

            if not ipaddr.endswith('.1'):
                newstruct[hostname]['gateway'] = "N"
            else:
                newstruct[hostname]['gateway'] = "Y"
                newstruct[hostname]['x'] = 0
                newstruct[hostname]['y'] = 0


        #---------------------------------#
        # New implementation with sqlite3 #
        #---------------------------------#
        HomeNetwork.add_update_rows(newstruct, init=True)

    @staticmethod
    def create_d3json(jsonfile="static/data/graph.json"):
        """ Create tree from sqlite data """
        gateway = None
        devices = defaultdict(list)
        colors = {}

        jsdata = HomeNetwork.read_sqlite3_current(jsondata=True)

        devices["nodes"] = json.loads(jsdata)

        for anode in devices["nodes"]:
            if anode["gateway"] == "Y":
                gateway = anode["ip"]
                anode["color"] = "red"
                continue
            
            if "osvendor" in anode and anode["osvendor"] not in colors:
                red = 0
                green = random.randint(-100, 255)
                blue = random.randint(-25, 236)
                colors[anode["osvendor"]] = "rgb({}, {}, {})".format(red, green, blue)

            elif "osvendor" not in anode:
                anode["osvendor"] = "default"
                red = 0
                green = random.randint(0, 2200)
                blue = random.randint(0, 9600)%255
                colors[anode["osvendor"]] = "rgb({}, {}, {})".format(red, green, blue)

            anode["color"] = colors[anode["osvendor"]]
            devices["links"].append({"source":  "", "target": anode["ip"]})

        for link in devices["links"]:
            link["source"] = gateway

        if jsonfile.startswith("/"):
            jsonfile = jsonfile[1:]

        with open(jsonfile, 'w') as jswrt:
            jswrt.write(json.dumps(devices, indent=4))

    @staticmethod
    def hasync():
        """ Sync HA data """
        
        cinfo = Utility.read_configuration(configfile="haconf.yml", config="HACREDS")
        
        with pysftp.Connection(**cinfo) as sftp:
            filecfg = Utility.read_configuration(configfile="haconf.yml", config="FILETX")

            with sftp.cd(filecfg["parentdir"]):
                sftp.put(filecfg["send"]["local"], filecfg["send"]["remote"], preserve_mtime=True)


