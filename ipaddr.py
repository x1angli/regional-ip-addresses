# -*- coding: utf-8 -*-

import logging
import os.path
import time
import urllib.request
from netaddr import IPSet, IPAddress, IPNetwork

__author__ = 'x1ang.li'

# ----- Begin config -----

# What countrys/regions/organizations are of our interest? Each element in this list has to be an ISO 3166 
# 2-letter code of the organisation to which the allocation or assignment was made. If a country/region is
# not listed here, then it would be skipped.
COUNTRY_CODES = ['CN']

# What type of network are of our interest? Just ipv4 or both ipv4 and ipv6? 
NETWORK_TYPES = ['ipv4', 'ipv6']
# ----- End config -----

# ----- Begin constants -----
APNIC_URL = 'https://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest'
APNIC_CACHE_PATH = './cache/apnic.txt'

# Reserved IP addresses for special purposes. See:
# https://en.wikipedia.org/wiki/Reserved_IP_addresses
# https://www.iana.org/assignments/ipv4-address-space/ipv4-address-space.xhtml
# https://www.iana.org/assignments/iana-ipv4-special-registry/iana-ipv4-special-registry.xhtml
# https://www.iana.org/assignments/multicast-addresses/multicast-addresses.xhtml
IPV4_RESERVED = IPSet([
    IPNetwork('0.0.0.0/8'),  # Broadcast message (RFC 1122, RFC 1700)
    IPNetwork('10.0.0.0/8'),  # Private network - local communication (RFC 1918)
    IPNetwork('100.64.0.0/10'),  # Carrier grade NAT (RFC 6598)
    IPNetwork('127.0.0.0/8'),  # Loopback addresses (RFC 990, RFC 1122)
    IPNetwork('169.254.0.0/16'),  # Link local (RFC 3927)
    IPNetwork('172.16.0.0/12'),  # Private network - local communication (RFC 1918)
    IPNetwork('192.0.0.0/24'),  # IANA IPv4 Special Purpose Address Registry (RFC 5736, RFC 6890)
    IPNetwork('192.0.2.0/24'),  # TEST-NET-1 examples and documentation (RFC 5737)
    # IPNetwork('192.31.196.0/24'),       # AS112-v4 [RFC 7535]
    # IPNetwork('192.52.193.0/24'),       # AMT [RFC 7450]
    IPNetwork('192.88.99.0/24'),  # Deprecated (6to4 Relay Anycast) (RFC 3068)
    IPNetwork('192.168.0.0/16'),  # Private network - local communication (RFC 1918)
    # IPNetwork('192.175.48.0/24'),       # Direct Delegation AS112 Service [RFC7534]
    IPNetwork('198.18.0.0/15'),  # Benchmarking (RFC 2544
    IPNetwork('198.51.100.0/24'),  # TEST-NET-2 documentation (RFC 5737)
    IPNetwork('203.0.113.0/24'),  # TEST-NET-3  documentation (RFC 5737)
    IPNetwork('224.0.0.0/4'),  # Multicast (RFC 5771), ranges all the way from 224/8 thru 239/8
    IPNetwork('240.0.0.0/4'),  # Reserved for future use, ranges all the way from 240/8 thru 255/8
])

# https://www.iana.org/assignments/iana-ipv6-special-registry/iana-ipv6-special-registry.xhtml
# https://www.iana.org/assignments/ipv6-address-space/ipv6-address-space.xhtml
# IPV6_RESERVED = IPSet([
#     IPNetwork('::1/128'),
#     IPNetwork('::/128'),
#     IPNetwork('::ffff:0:0/96'),
#     IPNetwork('64:ff9b::/96'),
#     IPNetwork('64:ff9b:1::/48'),
#     IPNetwork('100::/64'),
#     IPNetwork('2001::/23'),
#     IPNetwork('2001::/32'),
#     IPNetwork('2001:1::1/128'),
#     IPNetwork('2001:1::2/128'),
#     IPNetwork('2001:2::/48'),
#     IPNetwork('2001:3::/32'),
#     IPNetwork('2001:4:112::/48'),
#     IPNetwork('2001:5::/32'),
#     IPNetwork('2001:10::/28'),
#     IPNetwork('2001:20::/28'),
#     IPNetwork('2001:db8::/32'),
#     IPNetwork('2002::/16'),
#     IPNetwork('2620:4f:8000::/48'),
#     IPNetwork('fc00::/7'),
#     IPNetwork('fe80::/10'),
# ])
# ----- End of constants -----

# ----- Begin global variables -----
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
log = logging.getLogger(__name__)

rawstr_table = {}
domestic_table = {}
overseas_table = {}
# ----- End of global variables-----


def init():
    global rawstr_table
    rawstr_table = {f'{country}-{net_type}': [] for country in COUNTRY_CODES for net_type in NETWORK_TYPES}

    if not os.path.exists('cache'):
        os.makedirs('cache')


def populate_rawstr_table():
    log.info("Attempting to load local APNIC stats file...")
    if os.path.exists(APNIC_CACHE_PATH) and os.path.isfile(APNIC_CACHE_PATH):
        mod_time = os.path.getmtime(APNIC_CACHE_PATH)
        now_time = time.time()
        age = now_time - mod_time
        if age < 3600:
            log.info("Loading stats file from local cache file")
            with open(APNIC_CACHE_PATH, 'r') as f:
                stats_data = f.read()
        else:
            log.info("Loading stats file from APNIC website")
            log.info("Downloading APNIC stats file...")
            with urllib.request.urlopen(APNIC_URL) as res:
                stats_data = str(res.read(), 'utf-8')
            log.info("Downloaded APNIC stats file.")
            with open(APNIC_CACHE_PATH, 'w') as f:
                f.write(stats_data)
    log.info("Parsing stats file")

    lines = stats_data.splitlines(False)
    for line in lines:
        columns = line.split('|')
        if len(columns) != 7:
            continue

        registry, country_code, net_type, start, value, date, status = columns

        key = f'{country_code}-{net_type}'
        if key not in rawstr_table.keys():
            continue

        # ftp://ftp.apnic.net/pub/apnic/stats/apnic/README.TXT
        # value : In the case of IPv4 address the count of hosts for this range.
        #         In the case of IPv6 address the value will be the CIDR prefix length.
        if net_type == 'ipv4':
            value = int(value)
            suffix = value.bit_length() - 1
            if 2 ** suffix != value:
                log.warning(f"The {value} is not a power of 2!")
                continue
            prefix = str(32 - suffix)
        elif net_type == 'ipv6':
            prefix = value
        else:
            # this block may not be entered at runtime
            continue

        rawstr_table[key].append(start + '/' + prefix)

    log.info("Parsed stats file")


def write_file(scope: str, content: IPSet, prefix=''):
    if len(prefix) > 0 and not prefix.endswith('-'):
        prefix = prefix + '-'
    filename = f'output/{prefix}{scope}.txt'
    cidrs = content.iter_cidrs()
    log.info(f"Writing output file: {filename}")
    log.info(f"There are {len(cidrs)} CIDR blocks in {filename}.")
    with open(filename, 'w') as f:
        f.writelines(f"{cidr}\n" for cidr in cidrs)
    log.info(f"Wrote output file: {filename}")


def cal_n_write_domestic_table():
    for k, v in rawstr_table.items():
        domestic_table[k] = IPSet(v)

    for k, v in domestic_table.items():
        write_file(k, v)


def cal_complement_ipset(scope: str, content: IPSet) -> IPSet:
    if scope.endswith('v4'):
        return IPSet(['0.0.0.0/0']) - IPV4_RESERVED - content
    elif scope.endswith('v6'):
        return IPSet(['2000::/3']) - content
    else:
        log.warning(f"Unable to determine the network type {scope}. It has to be either ipv4 or ipv6.")
        return IPSet()


def cal_n_write_overseas_table():
    for k, v in domestic_table.items():
        overseas_table[k] = cal_complement_ipset(k, v)

    for k, v in overseas_table.items():
        write_file(k, v, 'out')


def main():
    init()
    populate_rawstr_table()
    cal_n_write_domestic_table()
    cal_n_write_overseas_table()


if __name__ == '__main__':
    main()
