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
This script provides a function to get DNAC authentication token and functions to make
DNAC REST APIs request. All required modules are imported in this script so from other
scripts just need to import this script
"""

import json
import sys
import logging
import time
import requests
from requests.auth import HTTPBasicAuth

import dnac_config  # DNAC IP is assigned in dnac_config.py

RETRY_INTERVAL = 3

logger = logging.getLogger('WirelessConfigAudit')

# It's used to get rid of certificate warning messages when using Python 3.
# For more information please refer to: https://urllib3.readthedocs.org/en/latest/security.html
requests.packages.urllib3.disable_warnings() # Disable warning message

class TaskTimeoutError(Exception):
    """
    Default Task TimeOut Exception Class
    """

class TaskError(Exception):
    """
    Default Task Error Exception Class
    """


def get_x_auth_token(ip=dnac_config.DNAC_IP, ver=dnac_config.VERSION,
                     uname=dnac_config.USERNAME, pword=dnac_config.PASSWORD):
    """
    This function returns a new JWT token.
    Passing ip, version,username and password when use as standalone function
    to overwrite the configuration above.

    Parameters
    ----------
    ip (str): dnac routable DNS address or ip
    ver (str): dnac version
    uname (str): user name to authenticate with
    pword (str): password to authenticate with

    Return:
    ----------
    str: DNAC authentication token
    """

    # The url for the post ticket API request
    post_url = "https://"+ip+"/dna/system/api/"+ ver +"/auth/token"
    # All DNAC REST API query and response content type is JSON
    headers = {'content-type': 'application/json'}
    # POST request and response
    try:
        resp = requests.post(post_url, auth=HTTPBasicAuth(username=uname, password=pword),
                             headers=headers, verify=False)
        # Remove '#' if need to print out response
        #print (r.text)
        resp.raise_for_status()
        # return service ticket
        return resp.json()["Token"]
    except requests.exceptions.ConnectionError as e:
        # Something wrong, cannot get service ticket
        logger.error("Error: {}".format(e))
        sys.exit()

def get(ip=dnac_config.DNAC_IP, ver=dnac_config.VERSION, uname=dnac_config.USERNAME,
        pword=dnac_config.PASSWORD, api='', params=''):
    """
    To simplify requests.get with default configuration.Return is the same as requests.get

    Parameters
    ----------
    ip (str): dnac routable DNS address or ip
    ver (str): dnac version
    uname (str): user name to authenticate with
    pword (str): password to authenticate with
    api (str): dnac api without prefix
    params (str): optional parameter for GET request

    Return:
    -------
    object: an instance of the Response object(of requests module)
    """
    ticket = get_x_auth_token(ip, ver, uname, pword)
    headers = {"X-Auth-Token": ticket}
    url = "https://"+ip+"/dna/intent/api/"+ver+"/"+api
    logger.debug("Request:\nmethod:\n{}\nurl: {}\nheaders: {}\nParameters: {}"
                 .format('GET', url, headers, params))
    try:
    # The request and response of "GET" request
        resp = requests.get(url, headers=headers, params=params, verify=False)
        logger.debug("GET {0} \nStatus: {1}".format(api, resp.status_code))
        return resp
    except:
        print("Something wrong with GET /{0}".format(api))
        sys.exit()

def post(ip=dnac_config.DNAC_IP, ver=dnac_config.VERSION,
         uname=dnac_config.USERNAME, pword=dnac_config.PASSWORD, api='', data=''):
    """
    To simplify requests.post with default configuration. Return is the same as requests.post

    Parameters
    ----------
    ip (str): dnac routable DNS address or ip
    ver (str): dnac version
    uname (str): user name to authenticate with
    pword (str): password to authenticate with
    api (str): dnac api without prefix
    data (JSON): JSON object

    Return:
    -------
    object: an instance of the Response object(of requests module)
    """
    ticket = get_x_auth_token(ip, ver, uname, pword)
    headers = {"content-type" : "application/json", "X-Auth-Token": ticket}
    url = "https://"+ip+"/dna/intent/api/"+ver+"/"+api
    logger.debug("Request:\nmethod:\n{}\nurl: {}\nheaders: {}"
                 .format('POST', url, headers))
    try:
    # The request and response of "POST" request
        resp = requests.post(url, json.dumps(data), headers=headers, verify=False)
        logger.debug("POST {0} \nStatus: {1}".format(api, resp.status_code))
        return resp
    except:
        print("Something wrong with POST /{0}".format(api))
        sys.exit()

def wait_on_task(task_id, timeout=(5*RETRY_INTERVAL), retry_interval=RETRY_INTERVAL,
                 ip=dnac_config.DNAC_IP, ver=dnac_config.VERSION, uname=dnac_config.USERNAME,
                 pword=dnac_config.PASSWORD):
    """ Waits for the specified task to complete
    """
    ticket = get_x_auth_token(ip, ver, uname, pword)
    headers = {"content-type" : "application/json", "X-Auth-Token": ticket}
    start_time = time.time()
    url = "https://" + ip + "/dna/intent/api/" + ver + "/" + "task/" + task_id
    while True:
        resp = requests.get(url, headers=headers, verify=False)
        resp.raise_for_status()

        response = resp.json()["response"]
        #print json.dumps(response)
        if "endTime" in response:
            return response
        else:
            if timeout and (start_time + timeout < time.time()):
                raise TaskTimeoutError("Task {0} did not complete within the specified timeout "
                                       "({1} seconds)".format(task_id, timeout))

            logger.debug("Task:{0} has not completed yet. Sleeping for {1}seconds..."
                         .format(task_id, retry_interval))
            time.sleep(retry_interval)

        if response['isError']:
            raise TaskError("Task {0} had error {1}".format(task_id, response['progress']))

    return response
