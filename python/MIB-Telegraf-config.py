# Copyright (c) 2011, Jay Conrod.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Jay Conrod nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL JAY CONROD BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import sys
import re
import os
#from webbrowser import open_new
#from lib2to3.pgen2.token import COMMENT
import json
from jinja2 import Template
import logging


##########################################################################
# Jinja2 Templates for configuration file formatting
##########################################################################

# The following jinja2 template is for expanding the Description information for OIDs
# WE need to create lots of the following:
# [[processors.starlark]]
# source = '''
# def apply(metric):
#     descriptions = {'s650NotifyAlarmEventID': 'The alarm or event ID of the notification.', 's650NotifyIndex': 'Internal alarm index for a notification.'}

#     metric.fields["description"] = str(descriptions.get(metric.tags["name"], "NA"))
#     return metric
# '''

# The data format for the template is
# data = {"description" : {'s650NotifyAlarmEventID': 'The alarm or event ID of the notification.',
#          's650NotifyIndex': 'Internal alarm index for a notification.'}}

d_template = '''[[processors.starlark]]
# MIB filename - {{ mib_filename }}
# MIB name - {{ mib_name }}
source = \'\'\'
def apply(metric):
    des = {{ description }}

    if metric.tags["name"] in des.keys():
        metric.fields["description"] = str(des.get(metric.tags["name"], "NA"))
    return metric 
\'\'\'
'''
##########################################################################
# The following jinja2 template is for MIB TYPE DEFINITION declarations.
# We need to create lots of the following:
# [[processors.enum]]
#     # MIB file - S650ALARM.mib
#     [[processors.enum.mapping]]
#         field = ALARMLEVELTYPE
#     [processors.enum.mapping.value_mappings]
#         0 = clear
#         2 = critical
#         3 = major
#         4 = minor
#         5 = event
#     [[processors.enum.mapping]]
#         field = S650TRANSIENT
#     [processors.enum.mapping.value_mappings]
#         0 = stateEvent
#         1 = transientEvent

# The data format for this template is
#
# data = {"mib_name": "S650ALARM.mib","mib_types":{"ALARMLEVELTYPE" : {'0': 'clear', '2': 'critical', '3': 'major', '4': 'minor', '5': 'event'},
# "S650TRANSIENT" : {'0': 'stateEvent', '1': 'transientEvent'}}}

t_template = '''[[processors.enum]]
    # MIB filename - {{ mib_filename }}
    # MIB name - {{ mib_name }}
    {% for pl_name, pl_lines in mib_types.items() -%}
    [[processors.enum.mapping]]
        field = "{{ pl_name }}"
    [processors.enum.mapping.value_mappings]
    {%- for k,v in pl_lines.items() %}
        {{ k }} = "{{ v }}"
    {%- endfor %}
    {% endfor %}
'''
##########################################################################
# The following jinja2 template is for each TRAP NOTIFICATION in a MIB
# Basically we are looking to collect the varbinds into something simple to
# code with.  These are then passed into a StarLark.conf file that can 
# be hand tweaked.
#
# [[processors.starlark]]
# # MIB filename - S650ALARM.mib
# # MIB name - S650ALARM
# source = '''
# def apply(metric):

#     #============= ntpLeapChange ===============================
#     if metric.tags["name"] == ntpLeapChange:
#         # The following are the varbind mappings from the trap.
#         vb1 = metric.fields["s650NotifyAlarmEventID"]
#         vb2 = metric.fields["s650NotifyAlarmAction"]
#         vb3 = metric.fields["s650NotifyIndex"]
#         vb4 = metric.fields["s650NotifySeverity"]
#         vb5 = metric.fields["s650NotifyDateTime"]
#         vb6 = metric.fields["s650NotifyDescription"]
#         vb7 = metric.fields["s650NotifySequenceNum"]
        

#         # Adapt the following code to suit the individual Notification.
#         metric.fields["agent"] = metric.tags["mib"]
#         metric.fields["alertgroup"] = metric.tags["name"]
#         metric.fields["alertkey"] = ""
#         metric.fields["class"] = "Microsemi"
#         metric.fields["eventid"] = ""
#         metric.fields["firstoccurence"] = ""
#         metric.fields["fqdn"] = ""
#         metric.fields["node"] = metric.tags["source"]
#         metric.fields["severity"] = ""
#         metric.fields["summary"] = "Alarm/Event 163 -- Entered warm-up state"
    
#     return metric 
# '''

#The data input looks like the following example.
#
# data4 = {"oidl": {    
#             "ntpLeapChange": {
#                 "objects": [
#                     "s650NotifyAlarmEventID",
#                     "s650NotifyAlarmAction",
#                     "s650NotifyIndex",
#                     "s650NotifySeverity",
#                     "s650NotifyDateTime",
#                     "s650NotifyDescription",
#                     "s650NotifySequenceNum"
#                 ],
#                 "specific-trap": 163,
#                 "parent_oid": "s650AlarmContain",
#                 "description": "Alarm/Event 163 -- Entered warm-up state",
#                 "organization": "Microsemi"
#                 }
#             },
#         "mib_filename": "S650ALARM.mib",
#         "mib_name": "S650ALARM"

#     }

s_template = '''[[processors.starlark]]
# MIB filename - {{ mib_filename }}
# MIB name - {{ mib_name }}
source = \'\'\'
def apply(metric):

    {% for n,v in oidl.items() -%}

    #============= {{n}} ===============================
    if metric.tags["name"] == "{{n}}":
        {% if v["objects"] is not none %}
        # The following are the varbind mappings from the trap.    
        {% for i in v["objects"] -%}
        vb{{ loop.index }} = metric.fields.get("{{i}}")
        {% endfor %}
        {% else %}
        # There are no varbinds mapped for the trap.
        {% endif %}

        # Adapt the following code to suit the individual Notification.
        metric.fields["agent"] = metric.tags["mib"]
        metric.fields["alertgroup"] = metric.tags["name"]
        metric.fields["alertkey"] = ""
        metric.fields["class"] = "{{v["organization"]}}"
        metric.fields["eventid"] = ""
        metric.fields["firstoccurence"] = ""
        metric.fields["fqdn"] = ""
        metric.fields["node"] = metric.tags["source"]
        metric.fields["severity"] = ""
        metric.fields["summary"] = "{{ v["description"] }}"
        
    {% endfor%}
    return metric 
\'\'\'
'''



##########################################################################
# Main code area
##########################################################################


def writeTelegrafMibConfig(k, t, d):
    '''
    k = the name of the MIB file we originally parsed
    t = a string with the type of config we are writing ["enum", "starlark", etc.]
    d = the Templated data we want to write to file

    outdir = is the GLOBAL file handle for the target directory in which we'll put the files

    The idea is to create subdirectories under outdir with the MIB name that we'll then drop the 
    config into so we can easily update things.

    PRE: we assume that we are in the "outdir" directory
    '''

    subdirname = re.split("\.", k, 1)[0].lower()
    if not os.path.exists(subdirname):
        os.mkdir(subdirname)

    os.chdir(subdirname)
    try:
        # First get the (assumed) first part of the filename that has the MIB name
        outfilename = (re.split("\.", k, 1)[0] + "_" + t + ".conf").lower()
        ofile = open(outfilename, "x")
        ofile.write(d)
    except:
        logging.error(f"Error writing to file for {outfilename}")

    os.chdir("..")


def stripString(s):
    '''
    A simple function to clean up dross from the MIB descriptions.
    '''
    if s is None: s = " "
    # s = s.replace("\n", "")
    # s = s.replace("\t", "")

    return re.sub(r"[^a-zA-Z0-9 . \(\)=]","",s)


def processDescription(m):
    # So we should get a full MIB item at this point
    # Pull out the description and associate it with the object name in oidList{}

    oidList = {}

    #print(f"DEBUG2b: Trying: {k}")
    try:
        ot = m["Body"]["Nodes"]
        n = m["Name"]
        # There are several reasonable cases where we see "Nodes": null
        # if ot is None: return
        # Nodes is a list not a dict
        logging.debug(f"DEBUG2a: Got a hit for {n}")
        for i in ot:
            try:
                oidn = i["Name"]
                oidd = stripString(i["ObjectIdentity"]["Description"])
                oidList[oidn] = oidd
                logging.debug(f"DEBUG2b: {oidn} : {oidd}")
            except:
                pass
            try:
                oidn = i["Name"]
                oidd = stripString(i["ObjectType"]["Description"])
                oidList[oidn] = oidd
                logging.debug(f"DEBUG2d: {oidn} : {oidd}")
            except:
                pass
            try:
                oidn = i["Name"]
                oidd = stripString(i["NotificationType"]["Description"])
                oidList[oidn] = oidd
                logging.debug(f"DEBUG2e: {oidn} : {oidd}")
            except:
                pass
            try:
                oidn = i["Name"]
                oidd = stripString(i["NotificationGroup"]["Description"])
                oidList[oidn] = oidd
                logging.debug(f"DEBUG2f: {oidn} : {oidd}")
            except:
                pass
    except Exception as err:
        # do nothing for the moment
        logging.info(f"DEBUG2c: Threw a wobbly for {n}")
        # traceback.print_exc()

    # OK we should be able to return something?
    return oidList


def processNotificationType(m):
    # So we should get a full MIB item at this point
    # Pull out the MIB NOTIFICATION-TYPE infomrmation into oidList{}

    oidList = {}

    # The Organisation becomes the @Class field in the trap.
    try:
        org = stripString(m["Body"]["Identity"]["Organization"])
    except:
        org = "Unknown"


    try:
        ot = m["Body"]["Nodes"]
        n = m["Name"]

        # Nodes is a list[] not a dict{}
        logging.debug(f"DEBUG3a: Got a hit for {n}")
        for i in ot:
            try:
                oidn = i["Name"]
                oidno = i["NotificationType"]["Objects"]
                oidd = stripString(i["NotificationType"]["Description"])
                oidsi = i["Oid"]["SubIdentifiers"]
                oidList[oidn] = {"objects": oidno,
                                 "specific-trap": oidsi[1]["Number"],
                                 "parent_oid": oidsi[0]["Name"],
                                 "organization": org,
                                 "description": oidd}
                logging.debug(f"DEBUG3b: {oidn} : {oidList[oidn]}")
            except:
                #oidList.pop("oidn", "Not Present")
                pass
    except Exception as err:
        # do nothing for the moment
        logging.info(f"DEBUG3c: Threw a wobbly for {n}")
        # traceback.print_exc()

    # OK we should be able to return something?
    return oidList


def processTypeDefs(m):
    '''    
    So we should get a full MIB item at this point
    Pull out the MIB TYPE infomrmation into oidList{}

    Note: we need to check in two(2) areas of the MIB for
    Type information
    '''

    oidList = {}
    n = m["Name"]
    try:
        ot = m["Body"]["Types"]

        # Types is a list[] not a dict{}

        for i in ot:
            try:
                oidn = i["Name"]
                e = i["Syntax"]["Enum"]
                if e is None:
                    continue
                logging.debug(f"DEBUG4a: Got a hit for {n}:{oidn}")

                eOut = {}
                for i in e:
                    eOut[i["Value"]] = i["Name"]

                oidList[oidn] = eOut
                logging.debug(f"DEBUG4b: {oidn} : {oidList[oidn]}")
            except:
                pass
    except Exception as err:
        # do nothing for the moment
        logging.debug(f"DEBUG4c: Threw a wobbly for {n}")
        # traceback.print_exc()

    try:
        ot = m["Body"]["Nodes"]

        # Nodes is a list[] not a dict{}
        for i in ot:
            try:
                oidn = i["Name"]
                e = i["ObjectType"]["Syntax"]["Type"]["Enum"]
                if e is None:
                    '''
                    The following lookup checks for cross referenced items within MIBs
                    For example the S650Alarm MIB has an OID "s650NotifySeverity" that
                    refers to "ALARMLEVELTYPE" which has the INTEGER to STRING mappings
                    of the severity.  So we are looking for these "s650NotifySeverity"
                    items and mapping the values from "ALARMLEVELTYPE" into the lookup.
                    '''
                    if (xref := i["ObjectType"]["Syntax"]["Type"]["Name"]) in oidList.keys():
                        logging.debug(
                            f"DEBUG4f: Got a hit for {n}:{oidn} cross reference")
                        oidList[oidn] = oidList[xref]
                    continue

                logging.debug(f"DEBUG4d: Got a hit for {n}:{oidn}")
                eOut = {}
                for i in e:
                    eOut[i["Value"]] = i["Name"]

                oidList[oidn] = eOut
                logging.debug(f"DEBUG4e: {oidn} : {oidList[oidn]}")
            except:
                pass
    except Exception as err:
        # do nothing for the moment
        logging.info(f"DEBUG4c: Threw a wobbly for {n}")
        # traceback.print_exc()

    # OK we should be able to return something?
    return oidList

# Iterate over the MIB looking for stuff of interest


def scanMIB(m):
    # "m should be a List of a MIBs.
    # this should itterate - oh dear.

    #  Create somewhere to save the information
    mj = {}
    ml = []

    # Instantiate the Jinja2 templates we are interested in
    j2_descriptions = Template(d_template)
    j2_typedefs = Template(t_template)
    j2_notifications = Template(s_template)

    for mib in m:

        # Even though we we iterate the following we know there is only one item
        # but it is simpler to work this way.
        for k, m in mib.items():
            '''
            k = the name of the MIB File that was parsed
            m = the parsed MIB content
            '''

            #if k != "S650ALARM.mib": continue
            logging.info(f"Processing - {k}")

            if (n := m.get("Name")) is None or m.get("Body") is None:
                # We should never hit this
                logging.warning(f"DEBUG9a: Malformed MIB entry? : {k}")
                continue

            # if len(md := processDescription(m)) > 0:
            #     data = {"mib_filename": k, "mib_name": n, "description": md}
            #     mt = j2_descriptions.render(data)
            #     writeTelegrafMibConfig(k, "starlark", mt)

            if len(mnt := processNotificationType(m)) > 0:
                data = {"mib_filename": k, "mib_name": n, "oidl": mnt}
                mt = j2_notifications.render(data)
                writeTelegrafMibConfig(k, "starlark2", mt)


            # try:
            #     if len(mnt := processNotificationType(m)) > 0:
            #         for kk,vv in mnt.values():
            #             print (kk, vv["description"])


            #         data = {"mib_filename": k, "mib_name": n, "oidl": mnt}
            #         mt = j2_notifications.render(data)
            #         writeTelegrafMibConfig(k, "starlark2", mt)
            # except:
            #     logging.error(f"DEBUG9b: Template error? : {k} \n {mnt}")

            if len(mdt := processTypeDefs(m)) > 0:
                data = {"mib_filename": k, "mib_name": n, "mib_types": mdt}
                mt = j2_typedefs.render(data)
                writeTelegrafMibConfig(k, "enum", mt)




if __name__ == '__main__':

    # Create this as a global for later use
    oidList = {}

    # Setup up logging
    logging.basicConfig(level=logging.INFO)

    if (len(sys.argv) != 3):
        sys.stderr.write(
            "Usage: MIB-Telegraf-config.py <input fille> <output DIRECTORY>\n")
        sys.exit(1)

    try:
        infilename = sys.argv[1]
        infile = open(infilename)
    except:
        logging.error(f"Failed to open or load input file - {infilename}")
        sys.exit(1)

    try:
        outdir = sys.argv[2]
        os.mkdir(outdir)
        os.chdir(outdir)
    except OSError as error:
        logging.error(f"Failed creating ouput directory - {outdir} - {error}")
        sys.exit(1)

    scanMIB(json.load(infile))

    infile.close()
