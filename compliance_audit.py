#!/usr/bin/env python
"""
Copyright (c) 2018 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""
"""
    @author Washim Bari
"""

from tabulate import tabulate
from dnac_api_helper import *
import dnac_config

logger = logging.getLogger('WirelessConfigAudit')
if dnac_config.VERBOSE:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

class Color:
    """
    Color Class to log text in Color
    """
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\x1b[0;30;41m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\x1b[0m'


def get_network_device_id(device_ip=dnac_config.DEVICE_IP, params=None):

    '''
    Get the Device UUID for a given IP address
    Get to network-device/ip-address/{device_ip}
    :param device_ip: Device IP address which has been added to the inventory
    :return: Returns device UUID
    '''
    try:
        # The request and response of GET network-device/ip-address/ API
        if params:
            resp = get(api="network-device", params=params)
        # If Device IP is provided
        else:
            resp = get(api="network-device/ip-address/"+device_ip, params=params)

        status = resp.status_code
        device = resp.text

    except ValueError:
        logger.error("Something wrong, cannot get network device information")
        sys.exit()

    if status != 200:
        logger.debug(resp.text)
        sys.exit()

    if not device:  # Response is empty, no network-device is discovered.
        logger.warning("No matching network device found on the Cluster")
        sys.exit()
    else:
        device_json = json.loads(device)
        logger.debug(json.dumps(device_json, indent=4, sort_keys=True))
        return {ele["instanceUuid"]:ele["managementIpAddress"] for ele in device_json["response"]}


def read_wireless_config_from_device(deviceUUIDList, cmd=["show wlan summary"]):
    '''
    Execute CLI commands on the Device and get the task id
    :param deviceUUIDList: List of Device UUID
    :param cmd: List of CLI commands that need to be executed on the device
    :return: Task ID
    '''
    payload = {"name": "command-runner",
               "description": "command-runner-network-poller",
               "deviceUuids": deviceUUIDList,
               "commands": cmd}
    # The request and response of POST  template-programmer/project API
    try:
        resp = post(api="network-device-poller/cli/read-request", data=payload)
        status = resp.status_code
        template = resp.text

    except ValueError:
        logger.error("Something wrong, can't execute command on the device")
        sys.exit()

    if status != 202:
        logger.debug(resp.text)
        sys.exit()
    else:
        template_json = json.loads(template)
        logger.debug(json.dumps(template_json, indent=4, sort_keys=True))
        logger.debug(resp.json()["response"]["taskId"])
        return resp.json()["response"]["taskId"]

def get_command_output(file_id):

    '''
    Get the Command Output from the File
    :param file_id: File ID created by DNAC
    :return: Command output as JSON
    '''
    try:
        # The request and response of GET network-device/ip-address/ API
        resp = get(api="file/"+file_id)

        status = resp.status_code
        file = resp.text

    except ValueError:
        logger.error("Something wrong, cannot get file information")
        sys.exit()

    if status != 200:
        logger.debug(resp.text)
        sys.exit()

    if file == []:  # Response is empty, no network-device is discovered.
        logger.error("No File found with ID {} !".format(file))
        sys.exit()
    else:
        file_json = json.loads(file)
        logger.debug(json.dumps(file_json, indent=4, sort_keys=True))
        return file_json

def get_wireless_profile():
    '''
    Get the SSID name created for Wireless Site Profile
    :return: List of SSIDs
    '''
    try:
        resp = get(api="wireless/profile", )
        status = resp.status_code
        profile = resp.text

    except ValueError:
        logger.error("Something wrong, cannot get Wireless Profile information")
        sys.exit()

    if status != 200:
        logger.debug(resp.text)
        sys.exit()

    if profile == []:  # Response is empty, no network-device is discovered.
        logger.error("No Wireless Profile found {} !")
        sys.exit()
    else:
        profile_json = json.loads(profile)
        logger.debug(json.dumps(profile_json, indent=4, sort_keys=True))
        return [ele["name"] for ele in profile_json[0]["profileDetails"]["ssidDetails"]]


def get_site_id():
    """
        Get Site IDs available on Clusters
    :return: List of SiteIds
    """
    try:
        resp = get(api="site", )
        status = resp.status_code
        site = resp.text

    except ValueError:
        logger.error("Something wrong, cannot get Site ID information")
        sys.exit()

    if status != 200:
        logger.debug(resp.text)
        sys.exit()

    if site == []:  # Response is empty, no network-device is discovered.
        logger.error("No Sites found on the DNAC Cluster!")
        sys.exit()
    else:
        profile_json = json.loads(site)
        logger.debug(json.dumps(profile_json, indent=4, sort_keys=True))
        logger.debug([{ele["id"]:ele["groupNameHierarchy"]} for ele in profile_json["response"]])
        return [{ele["id"]:ele["groupNameHierarchy"]} for ele in profile_json["response"]]

def get_device_from_site(siteId):
    '''
    Get the List of devices associated with a particular Site
    :param siteId: Site UUID
    :return: List of Management IPs of the devices associated with the Site
    '''
    try:
        params = {"siteId": siteId}
        resp = get(api="membership", params=params)
        status = resp.status_code
        site = resp.text

    except ValueError:
        logger.error("Something wrong, cannot get Site Membership information")
        sys.exit()

    if status != 200:
        logger.debug(resp.text)
        sys.exit()

    if site == []:
        logger.error("No Sites found on the DNAC Cluster!")
        sys.exit()
    else:
        profile_json = json.loads(site)
        logger.debug(json.dumps(profile_json, indent=4, sort_keys=True))
        if profile_json['device']["response"]:
            return [i['managementIpAddress'] for i in profile_json['device']["response"]]
        else:
            return None

def parse_output(output, device_ids_dict):
    '''
    Parse the show WLAN Summary Output from the device
    :param output: Command Output for the device
    :param device_ids_dict: List of the device
    :return: Parsed Output for the command
    '''
    parse_output = {}
    for i in output:
        if i["commandResponses"]["SUCCESS"]:
            device_ip = device_ids_dict[i["deviceUuid"]]
            parse_output[device_ip] = i["commandResponses"]["SUCCESS"]
    cmd_output = {}
    for i in parse_output.keys():
        wlan_output = parse_output[i]['show wlan summary'].split('\n')[6:-2]
        wlan_data = {'WLAN ID': [],
                     'WLAN Profile Name / SSID': [],
                     'Status': [],
                     'Interface Name': [],
                     'PMIPv6 Mobility': []}
        for row in wlan_output:
            row = row.split('  ')
            values = [r.strip() for r in row if r != '']
            wlan_data['WLAN ID'].append(int(values[0]))
            wlan_data['WLAN Profile Name / SSID'].append(values[1].split('/')[0].strip())
            wlan_data['Status'].append(values[2])
            wlan_data['Interface Name'].append(values[3])
            wlan_data['PMIPv6 Mobility'].append(values[4])
        cmd_output[i] = wlan_data
    logger.debug('Parse Output {}'.format(cmd_output))
    return cmd_output

def audit_config(parse_output_from_device=None, device_site_dict=None, config_dnac=None):
    '''

    :param parse_output_from_device: Parsed Output of the command
    :param device_site_dict: Device To Site Map table
    :param config_dnac: List of SSIDs configured on DNAC Cluster
    :return:

    Print a table like following

    Device Name         WLAN Configured         WLAN in SiteProfile
    ----------------------------------------------------------------
    ABCD                [WLAN106, WLAN107]      [Blizzard,Alpha]

    BCDE                [WLAN108, WLAN109]      [Blizzard,Alpha]
    '''
    table = []
    for device_ip in parse_output_from_device.keys():
        if parse_output_from_device[device_ip]['WLAN Profile Name / SSID'] != config_dnac:
            compliance = Color.BOLD + Color.RED + 'NO, Device and DNAC are not in SYNC'+ Color.END
        else:
            compliance = Color.BOLD + Color.GREEN + 'YES' + Color.END

        try:
            table_row = [device_ip, 'Wireless Controller', device_site_dict[device_ip],
                         str(parse_output_from_device[device_ip]['WLAN Profile Name / SSID']),
                         str(config_dnac),
                         compliance]
        except KeyError:
            table_row = [device_ip, 'Wireless Controller', 'Not Assigned',
                         str(parse_output_from_device[device_ip]['WLAN Profile Name / SSID']),
                         str(config_dnac),
                         compliance]
        table.append(table_row)

    logger.info('\n\n'+ '*'*75 +' WLAN AUDIT Report ' + '*'*75 + '\n\n' +
                tabulate(table,
                         headers=['Device IP Address', 'Device Family', 'Assigned Site', 'WLAN Configured',
                                  'WLAN in SiteProfile', 'Intent Compliance']) +'\n\n')


if __name__ == '__main__':
    logger.info('Let\'s start the program')
    logger.info('Login to the DNAC Cluster: {}'.format(dnac_config.DNAC_IP))
    device_ids_dict = get_network_device_id(params={'family': "Wireless Controller"})
    logger.info('WLC device found {}'.format(device_ids_dict))
    task_id = read_wireless_config_from_device(deviceUUIDList=[i for i in device_ids_dict.keys()])
    logger.debug('Task ID {}'.format(task_id))
    logger.debug('Wait for Task to Complete')
    task_status = wait_on_task(task_id)
    logger.debug(task_status)
    file_id = task_status["progress"]
    logger.debug('Fetching File...')
    output = get_command_output(file_id=json.loads(file_id)["fileId"])
    logger.debug('Output {}'.format(output))
    parsed_output = parse_output(output, device_ids_dict)
    logger.debug('Output {}'.format(parsed_output))
    wlan = get_wireless_profile()
    logger.info('WLAN configured in DNAC Site Profile {}'.format(wlan))
    device_site_dict = {}
    site_ids = get_site_id()
    for sites in site_ids:
        for siteId, site in sites.items():
            devices = get_device_from_site(siteId)
            if devices:
                for device in devices:
                    device_site_dict[device] = site
    audit_config(parsed_output, device_site_dict, wlan)
