# DNAC Wireless Intent Compliance App

### Description
Simple application to make use of Cisco DNA Center APIs to audit wireless SSID Intent with device configuration.
This script will compare wireless profile provisioned in Cisco DNAC (Design) against network/device configuration and produce a tabular report. This helps network administrator in deteacting mismatches w.r.t. design intent and actual configuration on the device. Based on the report outcome, the administrator can remediate the issue with appropriate site provisoning in DNAC.

DNAC APIs used:

| Method | API |
| --- | --- |
| GET | /dna/intent/api/v1/network-device |
| POST| /dna/intent/api/v1/network-device-poller/cli/read-request |
| GET | /dna/intent/api/v1/wireless/profile |
| GET | /dna/intent/api/v1/membership

### Prerequisite
- Devices should be added to inventory.
- Cisco DNAC with DNAC-Platform 1.4 Published APIs
- Following python packages should be pre installed.
   - requests
   - tabulate
   - json
   - time
   - sys

```buildoutcfg
pip install requests[secure]
pip install tabulate
```

### Configuring the Script
Before running the script you must edit the 'dnac_config.py' file and update the following values
```
DNAC_IP = "Your DNA Center Cluster IP Address"
DNAC_PORT = 443
USERNAME = "Your DNA Center Username"
PASSWORD = "Your DNA Center Password"
VERSION = "v1"
PRODUCT_FAMILY = "Device Family - Any one from the list {Wireless Controller,Routers, Switches}"
```

### Running Python script
```
python compliance_audit.py
```

### Sample Output
```buildoutcfg
./compliance_audit.py
2019-06-03 16:59:16,633-WirelessConfigAudit-INFO - Let's start the program
2019-06-03 16:59:16,633-WirelessConfigAudit-INFO - Login to the DNAC Cluster: 64.103.196.101
2019-06-03 16:59:16,826-WirelessConfigAudit-INFO - WLC device found {u'cbe6e29a-4d7a-434f-b159-51c3a0b60b28': u'10.104.105.10', u'5aa87632-c87d-49ed-8fa0-8a258a57d42f': u'10.104.105.11'}
2019-06-03 16:59:21,543-WirelessConfigAudit-INFO - WLAN configured in DNAC Site Profile [u'simwlan', u'wlan-me-dot1x-1']
"""
2019-06-03 16:59:22,524-WirelessConfigAudit-INFO -

*************************************************************************** WLAN AUDIT Report ***************************************************************************

Device IP Address    Device Family        Assigned Site           WLAN Configured                                    WLAN in SiteProfile               Intent Compliance
-------------------  -------------------  ----------------------  -------------------------------------------------  --------------------------------  -----------------------------------
10.104.105.10       Wireless Controller  Not Assigned            [u'wlan_106', u'TestSpartan1x', u'TestSpartan52']  [u'simwlan', u'wlan-me-dot1x-1']  NO, Device and DNAC are not in SYNC
10.104.105.11        Wireless Controller  Global/Bangalore/BGL18  [u'simwlan', u'wlan-me-dot1x-1']                   [u'simwlan', u'wlan-me-dot1x-1']  YES
```
