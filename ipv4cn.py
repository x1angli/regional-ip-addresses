# -*- coding: utf-8 -*-

import os
import logging

import requests
from netaddr import IPSet, IPAddress

__author__ = 'x1ang.li'

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
log = logging.getLogger(__name__)

# ----- Begin Constants -----
APNIC_URL = 'http://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest'

# ----- End of Constants -----


# ----- Begin Utility Functions -----
def binary_log(value):
    """
    Compared with Python's built-in math.log2(), I prefer this function. Since it takes the integer-typed input without
    converting it to float; also, the output it returns is also int-typed; plus, it is supposedly faster
    :param value: a positive integer which should be smaller than 2^32.
    :return: the power to which the base (i.e. 2) must be raised to produce the input value.
    """
    for i in range(32):
        test_value = 1 << i
        if (test_value == value):
            return i
        elif (test_value > value):
            logging.warning("The %i cannot be binary-logged", value)
            return (i + 1)

# ----- End of Utility Functions -----


class IPv4():

    def __init__(self, clear_cache = None):
        self.reserved_ip = 'reserved_ip.txt'
        self.cache_apnic = 'cache/apnic.txt'
        self.outfile_inwall = 'output/inwall.txt'
        self.outfile_outwall = 'output/outwall.txt'

        self.clear_cache = clear_cache

        self.ipset_reserved = None
        self.ipset_inwall = None
        self.ipset_outwall = None
        self.cidrs_inwall = None
        self.cidrs_outwall = None

        self.populate_reserved()


    def populate_reserved(self):
        with open(self.reserved_ip, 'r') as f:
            lines = f.readlines()

        ip_list = []
        for line in lines:
            if not line.startswith('#'):
                line = line.strip()
                if len(line) > 0:
                    ip_list.append(line)

        self.ipset_reserved = IPSet(ip_list)


    def download_table(self):
        if self.clear_cache:
            os.remove(self.cache_apnic)

        if (not os.path.exists(self.cache_apnic)) or os.path.getsize(self.cache_apnic) <= 0:
            logging.info("Start downloading APNIC stat")
            r = requests.get(APNIC_URL, stream=True)
            if r.status_code == 200:
                with open(self.cache_apnic, 'w') as f:
                    f.write(r.text)
                logging.info("Finished downloading APNIC stat")

    def parse_table(self):
        logging.info("Start parsing IP table(s)")

        with open(self.cache_apnic, 'r') as f:
            lines = f.readlines()

        ip_list = []
        for line in lines:
            if line.startswith('apnic|CN|ipv4'):
                line = line.rstrip()
                apnic, country, v4v6, prefix, count_of_addr, date, status = line.split('|')
                if v4v6 == 'ipv4' and country == 'CN':
                    decimal = 32 - binary_log(int(count_of_addr))
                    cidr_addr = prefix + '/' + str(decimal)
                    ip_list.append(cidr_addr)

        self.ipset_inwall = IPSet(ip_list)
        self.cidrs_inwall = list(self.ipset_inwall.iter_cidrs())

        logging.info("Finished parsing in-wall IP table(s). Total: %i CIDR blocks.", len(self.cidrs_inwall), )


    def derive_outwall(self):
        """
        This would not only inverse the set with the "big one", it would also exclude
        See: http://www.tcpipguide.com/free/t_IPReservedPrivateandLoopbackAddresses-3.htm
        """

        self.ipset_outwall = IPSet(['0.0.0.0/0']) ^ self.ipset_inwall ^ self.ipset_reserved
        self.cidrs_outwall = list(self.ipset_outwall.iter_cidrs())

        logging.info("Finished deriving out-wall IP table(s). Total: %i CIDR blocks.", len(self.cidrs_outwall), )


    def write_outfiles(self):
        logging.info("Writing output file: %s", self.outfile_inwall)
        with open(self.outfile_inwall, 'w') as f:
            for cidr_block in self.cidrs_inwall:
                f.write(str(cidr_block) + '\n')

        logging.info("Writing output file: %s", self.outfile_outwall)
        with open(self.outfile_outwall, 'w') as f:
            for cidr_block in self.cidrs_outwall:
                f.write(str(cidr_block) + '\n')


    def main_course(self):
        self.download_table()
        self.parse_table()
        self.derive_outwall()
        self.write_outfiles()

    def check_ip(self, ip):
        ip_addr = IPAddress(ip)
        logging.info("The IP address to be checked is: %s", ip_addr)

        # Populate both IPSets
        if self.ipset_inwall is None or self.ipset_outwall is None:
            self.main_course()

        if ip_addr in self.ipset_inwall:
            logging.info("The IP address %s is located in the Wall", ip)
        if ip_addr in self.ipset_outwall:
            logging.info("The IP address %s is located out the Wall", ip)


if __name__ == '__main__':
    program = IPv4()
    program.main_course()
    # program.check_ip('103.4.201.16')
