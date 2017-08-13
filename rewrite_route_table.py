# -*- coding: utf-8 -*-

import os
import logging
import subprocess

import requests
from netaddr import IPSet, IPAddress

logging.basicConfig(format='%(levelname)s:\t%(message)s', level=logging.INFO)
log = logging.getLogger(__name__)


class RuntimeException(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

class OfflineException(RuntimeException):
    def __init__(self,*args,**kwargs):
        RuntimeException.__init__(self,*args,**kwargs)

def load_cidr(v4cidr_f):
    if not os.path.exists(v4cidr_f) or not os.path.isfile(v4cidr_f):
        raise ValueError("The file containing IPv4 CIDR block info is missing or is not a valid file %s", v4cidr_f)

    with open(v4cidr_f, 'r') as f:
        lines = f.readlines()

    if not lines:
        raise ValueError("Cannot read the file content %s", v4cidr_f)

    return lines

def detect_interface():
    p = subprocess.run(['route', 'print', '128.0.0.0', '-4'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # p = subprocess.Popen(['route', 'print', '128.0.0.0', '-4'])
    if not p.stdout:
        raise ValueError("Cannot print the route table")

    lines = p.stdout.decode("utf-8").splitlines()
    state = 0 # 0: initial, 1: found v4 table, 2: found active routes section, 3: found actual neworks, -1: nothing
    for line in lines:
        if state == 0:
            if line.startswith('IPv4 Route Table'):
                state = 1
        elif state == 1:
            if line.startswith('Active Routes'):
                state = 2
        elif state == 2:
            line = line.strip()
            if line == 'None':
                state = -1
                break
            elif line.startswith('Network Destination'):
                pass
            elif len(line)<2: # ignore empty lines
                pass
            else:
                state = 3
                break

    if state == -1:
        raise OfflineException("We couldn't find any 3rd-party Interface other than the native one. Please make sure the tunnel is turned on.")
    elif state == 3:
        (dest, mask, gateway, interface, metrics) = line.split()

    logging.info("The gateway is %s", gateway)
    return gateway

def remove_old_rules():
    logging.info("Removing old routing rules...")
    p = subprocess.run(['route', 'delete', '0.0.0.0'  , 'mask', '128.0.0.0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p = subprocess.run(['route', 'delete', '128.0.0.0', 'mask', '128.0.0.0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info("Removed old routing rules.")

def inject_new_rules(outwall_cidr, gateway):
    logging.info("Injecting new routing rules...")
    for line in outwall_cidr:
        line = line.strip()
        p = subprocess.run(['route', 'add', line, gateway, 'metric', '6'], stdout=subprocess.PIPE, stderr=subprocess.PIPE) #
    logging.info("Injected new routing rules.")


def main():
    outwall_cidr, gateway = None, '10.173.172.133'

    try:
        outwall_cidr = load_cidr('output/outwall.txt')
        gateway = detect_interface()
    except ValueError as e:
        logging.error(e)
    except OfflineException as e:
        logging.warn(e)
        logging.info("Restarting the tunnel")
        # we could restart vpn

    if not outwall_cidr:
        logging.error("CIDR blocks must be defined.")
        return
    if not gateway:
        logging.error("The gateway and interface must be a valid value.")
        return
    remove_old_rules()
    inject_new_rules(outwall_cidr, gateway)

if __name__ == '__main__':
    main()