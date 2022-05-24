### Testing telegraf with snmptrap

Tried this command

```
snmptrap -v 2c -c public 192.168.0.51:1162 "" NET-SNMP-EXAMPLES-MIB::netSnmpExampleHeartbeatNotification netSnmpExampleHeartbeatRate i 123456
```

Saw this in Docker

```
docker logs -f mytelegraf
2022-04-04T22:00:33Z I! Using config file: /etc/telegraf/telegraf.conf
2022-04-04T22:00:33Z I! Starting Telegraf 1.22.0
2022-04-04T22:00:33Z I! Loaded inputs: snmp_trap
2022-04-04T22:00:33Z I! Loaded aggregators: 
2022-04-04T22:00:33Z I! Loaded processors: 
2022-04-04T22:00:33Z I! Loaded outputs: file
2022-04-04T22:00:33Z I! Tags enabled: host=a3ee5177c0ec
2022-04-04T22:00:33Z I! [agent] Config: Interval:10s, Quiet:false, Hostname:"a3ee5177c0ec", Flush Interval:10s
2022-04-04T22:00:33Z I! [inputs.snmp_trap] Listening on udp://:1162
2022-04-05T06:35:30Z E! [inputs.snmp_trap] Error resolving OID oid=.1.3.6.1.2.1.1.3.0, source=192.168.0.51: command timed out
```

Useful commands

```
# Open a Bash Shell in the container:
docker exec -it  mytelegraf bash


# Check the container logs
docker logs mytelegraf
```

**Gave up on the Docker version for the time being and use the installer into the Vagrant VM below.**

### VM based Telegraf installation

Note: Add option to select translator #10802

> Telegraf recently switched translation to use **gosmi** to address performance concerns. (see #9518, released in 1.21.0) This resulted in translation not being backward compatible with the previous release, 1.20.4.
> 
> This PR makes gosmi translation a config option, but defaults to netsnmp translation.
> 
> Users of 1.21.0 and later who have transitioned to gosmi will need to set **snmp_translator = "gosmi"** in their ***agent*** config. Users who have not upgraded past 1.20.4 in order to keep using netsnmp translation should be able to use this without config changes.

From: [Install Telegraf | Telegraf 1.22 Documentation](https://docs.influxdata.com/telegraf/v1.22/install/)

```
wget -qO- https://repos.influxdata.com/influxdb.key | sudo tee /etc/apt/trusted.gpg.d/influxdb.asc >/dev/null
source /etc/os-release
echo "deb https://repos.influxdata.com/${ID} ${VERSION_CODENAME} stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
sudo apt-get update && sudo apt-get install telegraf
```

Version installed was **1.22.0-1** as of 20220406

This runs as a service and can be stopped and started using the following.  This is useful in case you want to see if the config loads correctly and to see what telegraf is making of the incoming data (SNMP Trap).

```
sudo systemctl stop telegraf.service
sudo systemctl status telegraf.service
```

### Examples traps and corresponding STDOUT from telegraf.

Some are from Ben Bourke.

```
snmptrap -v 2c -c public 192.168.0.51:1162 "" NET-SNMP-EXAMPLES-MIB::netSnmpExampleHeartbeatNotification netSnmpExampleHeartbeatRate i 123456
```

> snmp_trap,community=public,host=tnstelegraf,mib=NET-SNMP-EXAMPLES-MIB,name=netSnmpExampleHeartbeatNotification,oid=.1.3.6.1.4.1.8072.2.3.0.1,source=192.168.0.51,version=2c sysUpTimeInstance=33098i,netSnmpExampleHeartbeatRate=123456i 1649225378344211897

```
snmptrap -v 2c -c public 192.168.0.51:1162 0 .1.3.6.1.4.1.18841.1.2.1.6.0.2 .1.3.6.1.4.1.18841.1.2.1.5.2 s "0"
```

> snmp_trap,community=public,host=tnstelegraf,mib=SNMPv2-SMI,name=enterprises.18841.1.2.1.6.0.2,oid=.1.3.6.1.4.1.18841.1.2.1.6.0.2,source=192.168.0.51,version=2c sysUpTimeInstance=0i,enterprises.18841.1.2.1.5.2="0" 1649225474425035648

```
snmptrap -v 2c -c public 192.168.0.51:1162 0 1.3.6.1.4.1.9070.1.2.5.7.4.1.2.163 1.3.6.1.4.1.9070.1.2.5.7.4.1.1.1.0 i 163 1.3.6.1.4.1.9070.1.2.5.7.4.1.1.10.0 i 1 1.3.6.1.4.1.9070.1.2.5.7.4.1.1.2.0 i "0" 1.3.6.1.4.1.9070.1.2.5.7.4.1.1.3.0 i 5 1.3.6.1.4.1.9070.1.2.5.7.4.1.1.5.0 s "2019-07-18 00:02:14" 1.3.6.1.4.1.9070.1.2.5.7.4.1.1.6.0 s "NTP leap indicator changed to 3" 1.3.6.1.4.1.9070.1.2.5.7.4.1.1.8.0 i "737"
```

> snmp_trap,community=public,host=tnstelegraf,mib=SNMPv2-SMI,name=enterprises.9070.1.2.5.7.4.1.2.163,oid=.1.3.6.1.4.1.9070.1.2.5.7.4.1.2.163,source=192.168.0.51,version=2c enterprises.9070.1.2.5.7.4.1.1.3.0=5i,enterprises.9070.1.2.5.7.4.1.1.5.0="2019-07-18 00:02:14",enterprises.9070.1.2.5.7.4.1.1.6.0="NTP leap indicator changed to 3",enterprises.9070.1.2.5.7.4.1.1.8.0=737i,sysUpTimeInstance=0i,enterprises.9070.1.2.5.7.4.1.1.1.0=163i,enterprises.9070.1.2.5.7.4.1.1.10.0=1i,enterprises.9070.1.2.5.7.4.1.1.2.0=0i 1649225944485110353

After I loaded the SMI MIBs I got this:

> snmp_trap,community=public,host=tnstelegraf,mib=S650ALARM,name=ntpLeapChange,oid=.1.3.6.1.4.1.9070.1.2.5.7.4.1.2.163,source=192.168.0.51,version=2c s650NotifyDescription.0="NTP leap indicator changed to 3",s650NotifySequenceNum.0=737i,sysUpTimeInstance=0i,s650NotifyAlarmEventID.0=163i,s650NotifyAlarmAction.0=1i,s650NotifyIndex.0=0i,s650NotifySeverity.0=5i,s650NotifyDateTime.0="2019-07-18 00:02:14" 1649226608383880797

```
snmptrap -v 2c -c public 192.168.0.51:1162 0 1.3.6.1.4.1.7054.70.0.107 1.3.6.1.4.1.7054.71.2.1.0 i 1001.3.6.1.4.1.7054.71.2.3.0 s "TYPE = 24, SEVERITY = 100, START = 1590387900, END = 1590387960, SRC = 10.113.112.37, DST = N/A"1.3.6.1.4.1.7054.71.2.4.0 i 12225 1.3.6.1.4.1.7054.71.2.5.0 s "https://10.113.112.40/event_viewer.php?id=12225" 1.3.6.1.4.1.7054.71.2.7.0 i 31.3.6.1.4.1.7054.71.2.8.0 i 1590387900 1.3.6.1.4.1.7054.71.2.16.0 i 0 1.3.6.1.4.1.7054.71.2.17.1.1.1 i 1 1.3.6.1.4.1.7054.71.2.17.1.2.1 s "10.113.112.37"1.3.6.1.4.1.7054.71.2.17.1.3.1 a "10.113.112.37" 1.3.6.1.4.1.7054.71.2.17.1.4.1 i 1 1.3.6.1.4.1.7054.71.2.17.1.5.1 s "0a.71.70.25 (hex)"1.3.6.1.4.1.7054.71.2.18.0 i 0 1.3.6.1.4.1.7054.71.2.20.0 i 0 1.3.6.1.4.1.7054.71.2.22.0 i 0
```

## Installing GO

**Remove any previous Go installation** by deleting the /usr/local/go folder (if it exists), then extract the archive you just downloaded into /usr/local, creating a fresh Go tree in /usr/local/go:

```
sudo rm -rf /usr/local/go 
```

```
sudo tar -C /usr/local -xzf go1.18.linux-amd64.tar.gz
```

(You may need to run the command as root or through `sudo`).

**Do not** untar the archive into an existing /usr/local/go tree. This is known to    produce broken Go installations.

Add /usr/local/go/bin to the `PATH` environment variable.

You can do this by adding the following line to your $HOME/.profile or    /etc/profile (for a system-wide installation):

```
export PATH=$PATH:/usr/local/go/bin
```

**Note:** Changes made to a profile file may not apply until the next time you log into your computer. To apply the changes immediately, just run the shell commands directly or execute them from the profile using a command such as

```
source $HOME/.profile
```

Verify that you've installed Go by opening a command prompt and typing the following command.

```
go version
```

Confirm that the command prints the installed version of Go.

### Checking the Telegraf gosmi library

**gosmi** is based off **PySMI** by the looks and implements ***RFC 1442  Structure of Management Information (SMI) for SNMPv2***.

Downloaded the ZIP file from the github repository and dropped it under a "go" folder in the vagrant-shared area.

Looking at the code I wanted to check the "cmd/parse" code to see if it parsed MIBs with anything interesting.

```
cd vagrant-shared/go/gosmi-master/cmd/parse
```

Then tried the incldued test.mib

```
go run . ./test.mib
```

This produced some JOSN output that looked interesting, so I copied the S650ALARM.mib into the same location and ran it.

```
go run . ./S650ALARM.mib > results.json
```

I can then see it referenced in the "**ntpLeapChange**" notification:

>         Pos: Position{Filename: "./S650ALARM.mib", Offset: 55720, Line: 1544, Column: 3},
>         Name: types.SmiIdentifier("ntpLeapChange"),
>         NotificationType: &parser.NotificationType{
>           Pos: Position{Filename: "./S650ALARM.mib", Offset: 55755, Line: 1545, Column: 4},
>           Objects: []types.SmiIdentifier{
>             types.SmiIdentifier("s650NotifyAlarmEventID"),
>             types.SmiIdentifier("s650NotifyAlarmAction"),
>             types.SmiIdentifier("s650NotifyIndex"),
>             types.SmiIdentifier("s650NotifySeverity"),
>             types.SmiIdentifier("s650NotifyDateTime"),
>             types.SmiIdentifier("s650NotifyDescription"),
>             types.SmiIdentifier("s650NotifySequenceNum"),
>           },
>           Status: parser.Status("current"),
>           Description: "Alarm/Event 163 -- NTP Leap indicator Changed\n\t\t\t\t\n\t\t\t\tIt contains the OID and value for alarm ID, notify index, severity, transient, \n\t\t\t\tdate and time, severity, descriptions, and sequence number.",
>         },
>         Oid: &parser.Oid{
>           Pos: Position{Filename: "./S650ALARM.mib", Offset: 56170, Line: 1553, Column: 10},
>           SubIdentifiers: []parser.SubIdentifier{
>             {
>               Pos: Position{Filename: "./S650ALARM.mib", Offset: 56170, Line: 1553, Column: 10},
>               Name: &types.SmiIdentifier("s650AlarmContain"),
>             },
>             {
>               Pos: Position{Filename: "./S650ALARM.mib", Offset: 56187, Line: 1553, Column: 27},
>               Number: &types.SmiSubId(163),
>             },
>           },
>         },
>       },

The "**s650NotifySeverity**" identifier links to 

> Pos: Position{Filename: "./S650ALARM.mib", Offset: 6144, Line: 273, Column: 3},
>         Name: types.SmiIdentifier("s650NotifySeverity"),
>         ObjectType: &parser.ObjectType{
>           Pos: Position{Filename: "./S650ALARM.mib", Offset: 6178, Line: 274, Column: 4},
>           Syntax: parser.Syntax{
>             Pos: Position{Filename: "./S650ALARM.mib", Offset: 6185, Line: 274, Column: 11},
>             Type: &parser.SyntaxType{
>               Pos: Position{Filename: "./S650ALARM.mib", Offset: 6185, Line: 274, Column: 11},
>               Name: types.SmiIdentifier("ALARMLEVELTYPE"),
>             },
>           },
>           Access: parser.Access("read-only"),
>           Status: parser.Status("current"),
>           Description: "Alarm severity:\n\t\t\t\t0 - clear alarm or event\n\t\t\t\t2 - critical alarm (set, if non-transient)\n\t\t\t\t3 - major alarm (set, if non-transient)\n\t\t\t\t4 - minor alarm (set, if non-transient)\n\t\t\t\t5 - report event (set, if non-transient)",
>         },

Looking at it with vscode I could see the declarations for things like "**ALARMLEVELTYPE**" in the JSON:

> ```
>     Name: types.SmiIdentifier("ALARMLEVELTYPE"),
>     Syntax: &parser.SyntaxType{
>       Pos: Position{Filename: "./S650ALARM.mib", Offset: 1334, Line: 54, Column: 22},
>       Name: types.SmiIdentifier("INTEGER"),
>       Enum: []parser.NamedNumber{
>         {
>           Pos: Position{Filename: "./S650ALARM.mib", Offset: 1350, Line: 56, Column: 4},
>           Name: types.SmiIdentifier("clear"),
>           Value: "0",
>         },
>         {
>           Pos: Position{Filename: "./S650ALARM.mib", Offset: 1363, Line: 57, Column: 4},
>           Name: types.SmiIdentifier("critical"),
>           Value: "2",
>         },
>         {
>           Pos: Position{Filename: "./S650ALARM.mib", Offset: 1379, Line: 58, Column: 4},
>           Name: types.SmiIdentifier("major"),
>           Value: "3",
>         },
>         {
>           Pos: Position{Filename: "./S650ALARM.mib", Offset: 1392, Line: 59, Column: 4},
>           Name: types.SmiIdentifier("minor"),
>           Value: "4",
>         },
>         {
>           Pos: Position{Filename: "./S650ALARM.mib", Offset: 1405, Line: 60, Column: 4},
>           Name: types.SmiIdentifier("event"),
>           Value: "5",
>         },
>       },
> ```

So we can see the link from the notification "**ntpLeapChange**" to "**s650NotifySeverity**" to the "**ALARMLEVELTYPE**"

It looks like the information is there; it is just that perhaps telegraf or the gosmi library is not using it.   Basically, neither library look that complete; equally there does not seem to be much reason to revert to the net-snmp library as that seems to be a complication that is not needed.

### Kludging a MIB parser in GO

So used the GO Telegraf libraries to parse the above in the following folder (Vagrant VM). These are the github.com/sleepinggenius2/gosmi/parser libraries with some copied directory traversing work to produce a very big file > 1.6 million lines of formatted JSON! It includes a lot of "Pos" position information to help with debugging of the results.

> /home/vagrant/vagrant_data/snmp-telegraf-git/telegraf-snmp/go_mib_parser/main.go

Did some initial setup and dowloading of modules etc.

```
go mod init go_mib_parser
go mod tidy
```

This produces a file **based on the (static coded) starting directory** "/home/vagrant/vagrant_data/snmp-telegraf-git/telegraf-snmp/mibs" (it is actually a relative path in  main.go file as "../mibs").

```
go run . > results.json
```

Can build the file then do much the same

```
go build
./go_mib_parser > result.json
```

## Build Telegraf from Source

Build From Source

Telegraf requires Go version 1.17 or newer, the Makefile requires GNU make.

Install Go >=1.17 (1.17.2 recommended)

Clone the Telegraf repository:

    git clone https://github.com/influxdata/telegraf.git

Run make from the source directory

    cd telegraf
    make

It worked and leaves an executable in the folder that can be run.

**It pulled down lots of modules or GO source that we would need to understand (scanned etc.) as part of building in our environment.**

### Trying to understand how Telegraf and the GoSMI modules work.

For the most part I was only looking at v2 traps on the assumption that Trap Ringer would be OK to convert from v1, v3 to v2 inside the DC.

**telegraf/plugins/inputs/snmp_trap/snmp_trap.go** [262] ***makeTrapHandler*** is the main trap handler in Telegraf. It takes a SnmpTrap as its input:

> // SnmpTrap is used to define a SNMP trap, and is passed into SendTrap
> type SnmpTrap struct {
>    **Variables []SnmpPDU**
> 
>    // If true, the trap is an InformRequest, not a trap. This has no effect on
>    // v1 traps, as Inform is not part of the v1 protocol.
>    IsInform bool
> 
>    // These fields are required for SNMPV1 Trap Headers
>    Enterprise   string
>    AgentAddress string
>    GenericTrap  int
>    SpecificTrap int
>    Timestamp    uint
> }

Basically, for v2 traps at least it is an array of PDUs.  This is all explained in **gosnmp/marshal.go** .  The **SnmpPacket stuct** has the entire SNMP message.

|

|->> [321] calls ***translator.lookup(oid string)*** in **telegraf/plugins/inputs/snmp_trap/gosmi.go** which is basiclly a wrapper to snmp.TrapLookup(oid string) [148] in **telegraf/internal/snmp/translate.go**.

#### Conclusion

The issue is that Telegraf and gosmi makes no attempt to do any lookup on the value in the PDU.  Telegrapf DOES load the MIB using ***LoadModule(module string)*** in **gosmi/smi/internal/module.go** [344] which inturn calls ***Parse(r io.Reader)*** in **gosmi/parser/parser.go** - this is what was used in the **gosmi/cmd/parse** test above.

- The parser does seem to be useful and we could use it for the basis of a lookup function.

- We could potentially either modify Telegraf itself or develop some processor code that uses the lookup to replace values with meaningful names.

- Completely separately to the above, we could also add a processor to do field munging like we do in Netcool Rules, but we would need to assess the value of doing this going forward.

### Using telegraf.conf ENUM Processor

> The Enum Processor allows the configuration of value mappings for metric tags or fields. The main use-case for this is to rewrite status codes such as red, amber and green by numeric values such as 0, 1, 2. 

It can also map numeric values to status codes!

The following shows how we can manually do the mapping for a couple of fields in the s650 MIB from above.

```
###############################################################################
#                            PROCESSOR PLUGINS                                #
###############################################################################
# Map enum values according to given table.
[[processors.enum]]
  [[processors.enum.mapping]]
    ## Name of the field to map. Globs accepted.
    field = "s650NotifySeverity"

    ## Name of the tag to map. Globs accepted.
    # tag = "status"

    ## Destination tag or field to be used for the mapped value.  By default the
    ## source tag or field is used, overwriting the original value.
    dest = "s650NotifySeverity"

    ## Default value to be used for all values not contained in the mapping
    ## table.  When unset and no match is found, the original field will remain
    ## unmodified and the destination tag or field will not be created.
    # default = 0

    ## Table of mappings
    [processors.enum.mapping.value_mappings]
      5 = "critical"
      4 = "warning"
      3 = "information"

  [[processors.enum.mapping]]
    ## Name of the field to map. Globs accepted.
    field = "s650NotifyAlarmAction"

    ## Name of the tag to map. Globs accepted.
    # tag = "status"

    ## Destination tag or field to be used for the mapped value.  By default the
    ## source tag or field is used, overwriting the original value.
    dest = "s650NotifyAlarmAction"

    ## Default value to be used for all values not contained in the mapping
    ## table.  When unset and no match is found, the original field will remain
    ## unmodified and the destination tag or field will not be created.
    # default = 0

    ## Table of mappings
    [processors.enum.mapping.value_mappings]
      5 = "critical"
      4 = "warning"
      1 = "read a book (1)"
```

Start Telegraf with the option to load extra configuration files:

```
./telegraf --config-directory /etc/telegraf/telegraf.d
```

When we send the following:

```
snmptrap -v 2c -c public 192.168.0.51:1162 0 1.3.6.1.4.1.9070.1.2.5.7.4.1.2.163 1.3.6.1.4.1.9070.1.2.5.7.4.1.1.1.0 i 163 1.3.6.1.4.1.9070.1.2.5.7.4.1.1.10 i 1 1.3.6.1.4.1.9070.1.2.5.7.4.1.1.2.0 i "0" 1.3.6.1.4.1.9070.1.2.5.7.4.1.1.3 i 5 1.3.6.1.4.1.9070.1.2.5.7.4.1.1.5.0 s "2019-07-18 00:02:14" 1.3.6.1.4.1.9070.1.2.5.7.4.1.1.6.0 s "NTP leap indicator changed to 3" 1.3.6.1.4.1.9070.1.2.5.7.4.1.1.8.0 i "737"
```

NOTE:  I did need to "strip" the ".0" from the OIDs to ensure we mapped, so I would need to check this with Ben B to make sure this is a valid approach.

We get the following:

> snmp_trap,community=public,host=tnstelegraf,mib=S650ALARM,name=ntpLeapChange,oid=.1.3.6.1.4.1.9070.1.2.5.7.4.1.2.163,source=192.168.0.51,version=2c s650NotifyDateTime.0="2019-07-18 00:02:14",s650NotifyDescription.0="NTP leap indicator changed to 3",s650NotifySequenceNum.0=737i,sysUpTimeInstance=0i,s650NotifyAlarmEventID.0=163i,s650NotifyIndex.0=0i,s650NotifySeverity="**critical**",s650NotifyAlarmAction="**read a book (1)**" 1650357810197891127

#### Codifying using ENUM Configuration

The python code  for this is in ***~/Documents/Software/Ansible-Vagrant/Ubuntu 20.04LTS Telegraf SNMP/vagrant_shared/python***.

It is run as follows:

```
ython3 ./MIB-lookup-extract.py results.json processors.enum.conf
```

Then basically copy the .conf to ***/etc/telegraf/telegraf.d*** in the VM running Telegraf then start telegraf as above with the ***--config*** directive.

Processing time difference in neglegible (i.e.  I could not tell just looking at it), but stress testing would be needed to see what happens with a lot of incoming events.

The code currently:

1. Parses the vendor MIBs to produce the intermediate JSON (done in the precursor GO code).

2. Picks up the ENUMs in the MIB and maps them into Telgraf format.

3. Checks and includes the "indirect" lookups (e.g. s650NotifySeverity) to map them across also.

4. Output is the named string - we could add the original value to the string if need be.

### Using telegraf.conf Starlark Processor

> The starlark processor calls a Starlark function for each matched metric, allowing for custom programmatic metric processing.
> 
> The Starlark language is a dialect of Python, and will be familiar to those who have experience with the Python language. However, there are major differences. Existing Python code is unlikely to work unmodified. The execution environment is sandboxed, and it is not possible to do I/O operations such as reading from files or sockets.

The Starlink language is specified in [starlark-go/spec.md at master · google/starlark-go · GitHub](https://github.com/google/starlark-go/blob/master/doc/spec.md#type).

Trying to see if I can use this for slightly more complex field manipulations such creating a "Summary" field from a dsicovery OID.

The configuration for such looks like:

```
###############################################################################
#                            PROCESSOR PLUGINS                                #
###############################################################################
# Process metrics using a Starlark script
[[processors.starlark]]

namepass = ["snmp_trap"]

source = '''
def apply(metric):
    if metric.tags["name"] == "ntpLeapChange":
        metric.fields["summary"] = str(metric.fields["s650NotifyDescription.0"])
    return metric
'''
```

So when sending the same trap, and in addition to the EMUM processor, we see:

> snmp_trap,community=public,host=tnstelegraf,mib=S650ALARM,name=ntpLeapChange,oid=.1.3.6.1.4.1.9070.1.2.5.7.4.1.2.163,source=192.168.0.51,version=2c s650NotifyIndex.0=0i,s650NotifyDateTime.0="2019-07-18 00:02:14",s650NotifyDescription.0="NTP leap indicator changed to 3",s650NotifySequenceNum.0=737i,sysUpTimeInstance=0i,s650NotifyAlarmEventID.0=163i,**summary="NTP leap indicator changed to 3"**,s650NotifySeverity="critical",s650NotifyAlarmAction="read a book (1)" 1650487073845089242

We could effectively use this to replace the ENUM processor also.

=================

## SMI Investigations

This is just trying to put the SMI RFC into a simpler context.

### NOTIFICATION-TYPE

          -- definitions for notifications
          NOTIFICATION-TYPE MACRO ::=
          BEGIN
              TYPE NOTATION ::=
                            ObjectsPart
                            "STATUS" Status
                            "DESCRIPTION" Text
                            ReferPart
              VALUE NOTATION ::=
                            value(VALUE OBJECT IDENTIFIER)
              ObjectsPart ::=
                            "OBJECTS" "{" Objects "}"
                          | empty
              Objects ::=
                            Object
                          | Objects "," Object
              Object ::=
                            value(Name ObjectName)
              Status ::=
                            "current"
                          | "deprecated"
                          | "obsolete"
              ReferPart ::=
                          "REFERENCE" Text
                        | empty
              -- uses the NVT ASCII character set
              Text ::= """" string """"
          END

An example of this looks like the following; the ***OBJECTS array*** links to other **ObjectName** items.

>         -- 1.3.6.1.4.1.9070.1.2.5.7.4.1.2.1
>         enterWarmUpState NOTIFICATION-TYPE
>             OBJECTS { s650NotifyAlarmEventID, s650NotifyAlarmAction, s650NotifyIndex, s650NotifySeverity, s650NotifyDateTime, 
>                 s650NotifyDescription, s650NotifySequenceNum }
>             STATUS current
>             DESCRIPTION 
>                 "Alarm/Event 1 -- Entered warm-up state.
>     
>                 It contains the OID and value for alarm ID, notify index, severity, transient, 
>                 date and time, severity, descriptions, and sequence number."
>             ::= { s650AlarmContain 1 }

Looking at how the **s650NotifySeverity object** can be interpreted; looking it up in the MIB.

>         -- 1.3.6.1.4.1.9070.1.2.5.7.4.1.1.3
>         s650NotifySeverity OBJECT-TYPE
>             SYNTAX ALARMLEVELTYPE
>             MAX-ACCESS read-only
>             STATUS current
>             DESCRIPTION
>                 "Alarm severity:
>                 0 - clear alarm or event
>                 2 - critical alarm (set, if non-transient)
>                 3 - major alarm (set, if non-transient)
>                 4 - minor alarm (set, if non-transient)
>                 5 - report event (set, if non-transient)
>                 "
>             ::= { s650NotifyElements 3 }

This is then broken down using the **SYNTAX** term.

>         ALARMLEVELTYPE ::= INTEGER
>             {
>             clear(0),
>             critical(2),
>             major(3),
>             minor(4),
>             event(5)
>             }

From this results.json file, we can crunch it with some Python code to interpret important MIB structures (we hope).  Notionally, this could and should be converted to GO for ease of code maintenance; it was only done in Python becuase I was more comfortable coding JSON in it.

Directory is:

> /home/vagrant/vagrant_data/python

Run the following:

```
python3 ./MIB-lookup-extract.py results.json > out.txt
```

### 20220431

Have create python3 code **MIB-information-extract.py** that creates a directory of Telegraf configuration files.

It is run as:

```
python3 ./MIB-information-extract.py results-old-working.json fred
where:
    results-old-working.json is the input parsed MIB file or files
    fred is the target directory under which the configuration files will be saved.
```

The output is saved in the following directory structure:

(fred directory)
            |----- (MIB Name directory)
                                    |----- (MIB Name .conf file(s))

            |----- (s650alarm directory)

                                    |----- s650alarm_enum.conf

                                    |----- s650alarm__starlink.conf

                                    |----- s650alarm_starlink2.conf>

The whole fred directory can be loaded under /etc/telegraf/telegraf.d and will be read and parsed when Telegraf is loaded using:

```
./telegraf --config-directory /etc/telegraf/telegraf.d
```

### Basic  approach for the POC

1. Create a base directory called "poc"

2. Copy "telegraf-snmp/go_mib_parser/go_mib_parser" from the GIT POC repo download to this directory.  This is the GO MIB parser.

3. Copy "telegraf-snmp/python/MIB-Telegraf-config.py" to this directory.  This is the python Telegraf configuration builder.

4. Create a sub-directory  "poc/mibs".  Put all the MIBs to be parsed in there in any (reasonable) structure, the parser will walk the tree.

5. Run the MIB Parser:

```
go_mib_parser > results.json
```

6. The results.json will look like crap unless you have an editor that can prettyprint JSON.  VSC can do this, but it is still a big file at around 28MB.

7. Run the python config builder:

```
python3 MIB-Telegraf-config.py 
Usage: MIB-Telegraf-config.py <input fille> <output DIRECTORY>


# So the typical POC call is:
python3 MIB-Telegraf-config.py result.json fred
```

8. This should give a folder called "fred" with the configurations in there.

9. Assuming that telgraf is already installed and using default directories, copy the configurations.

```
sudo cp telegraf-snmp/telegraf/telegraf.conf /telegraf.conf
sudo rm -rf /etc/telegraf/telegraf.d/fred
sudo cp -r fred /etc/telegraf/telegraf.d
```

10. You WILL need to eventually adjust the OUTPUT on the telegraf.conf configuration as it just writes to STDOUT.

11. Please eventually use a better directory name than "fred".

12. You may need to stop the telegraf service if it auto-starts as it did for me on Ubuntu.

```
sudo systemctl stop telegraf.service
```

13. You should be able to start telegraf and check the loading of the MIBs.

```
telegraf --config-directory /etc/telegraf/telegraf.d
```

14. You should see something like the following at the start:

```
2022-05-24T21:06:19Z I! Using config file: /etc/telegraf/telegraf.conf
2022-05-24T21:06:19Z W! DeprecationWarning: Option "timeout" of plugin "inputs.snmp_trap" deprecated since version 1.20.0 and will be removed in 2.0.0: unused option
2022-05-24T21:06:19Z I! Starting Telegraf 1.22.3
2022-05-24T21:06:19Z I! Loaded inputs: snmp_trap
2022-05-24T21:06:19Z I! Loaded aggregators: 
2022-05-24T21:06:19Z I! Loaded processors: enum (95x) starlark (36x)
2022-05-24T21:06:19Z I! Loaded outputs: file
2022-05-24T21:06:19Z I! Tags enabled: host=tnstelegraf
2022-05-24T21:06:19Z W! Deprecated inputs: 0 and 1 options

```

15. The main check is for the line with "Loaded processors: enum (95x) starlark (36x)" to confirm it saw the configurations in the "fred" folder.

16. If there were no errors in the configs then the last line should read:

```
2022-05-24T21:06:24Z I! [inputs.snmp_trap] Listening on udp://:1162
```

18. Now it is a case of:
- playing with the python code to change the Starlark templates if desired.

- updating the Starlark configurations to match the current NC Rules as far as you see appropriate.
