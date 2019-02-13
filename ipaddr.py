# -*- coding: utf-8 -*-

import logging
import os, subprocess
import requests

__author__ = 'x1ang.li'

# ----- Begin constants -----
APNIC_URL = 'http://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest'
# ----- End of constants -----

# ----- Begin small helper funcs -----
gen_scope_key = lambda country, v4v6: country + '-' + v4v6
# ----- End of small helper funcs -----


logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
log = logging.getLogger(__name__)


def generate_ipaddr_tables():
    country_filter = ['CN']
    v4v6_filter = ['ipv4', 'ipv6']

    # initialize big_dict with Python's dict comprehension of two loops
    big_dict = {gen_scope_key(country, v4v6): [] for country in country_filter for v4v6 in v4v6_filter}

    log.info("Start downloading APNIC stat...")
    r = requests.get(APNIC_URL, stream=True)
    if r.status_code != 200:
        log.error(f"Unable to retrieve table")
        return
    response = r.text
    log.info("Finished downloading APNIC stat.")

    log.info("Start parsing")

    lines = response.splitlines(False)
    for line in lines:
        columns = line.split('|')
        if len(columns) != 7:
            continue
        apnic, country, v4v6, start, value, date, status = columns

        key = gen_scope_key(country, v4v6)
        if key not in big_dict.keys():
            continue

        # ftp://ftp.apnic.net/pub/apnic/stats/apnic/README.TXT
        # value : In the case of IPv4 address the count of hosts for this range.
        #         In the case of IPv6 address the value  will be the CIDR prefix length.
        if v4v6 == 'ipv4':
            value = int(value)
            suffix = value.bit_length() - 1
            if 2 ** suffix != value:
                log.warning(f"The {count_of_addr} is not a power of 2!")
                continue
            prefix = str(32 - suffix)
        elif v4v6 == 'ipv6':
            prefix = value
        else:
            # this block may not be entered at runtime
            continue

        cidr = start + '/' + prefix
        big_dict[key].append(cidr)

    log.info("Finished parsing in-wall IP table(s).")

    # ipset_inwall = IPSet(big_dict[gen_scope_key('CN', 'ipv4')])
    # cidrs_inwall = ipset_inwall._cidrs()

    for key in big_dict.keys():
        cidrs = big_dict[key]
        log.info(f"There are {len(cidrs)} CIDR blocks in {key}.")

        filename = 'tmp/' + key + '.txt'
        log.info(f"Writing output file: {filename}")
        with open(filename, 'w') as f:
            f.writelines(f"{cidr}\n" for cidr in cidrs)

if __name__ == '__main__':
    generate_ipaddr_tables()
