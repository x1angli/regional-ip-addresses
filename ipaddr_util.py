import logging
from netaddr import IPSet, IPAddress, IPNetwork

# Reserved IP addresses for special purposes. See:
# https://en.wikipedia.org/wiki/Reserved_IP_addresses
# https://www.iana.org/assignments/ipv4-address-space/ipv4-address-space.xhtml
# https://www.iana.org/assignments/iana-ipv4-special-registry/iana-ipv4-special-registry.xhtml
# https://www.iana.org/assignments/multicast-addresses/multicast-addresses.xhtml
IPV4_RESERVED = IPSet([
    IPNetwork('0.0.0.0/8'),             # Broadcast message (RFC 1122, RFC 1700)
    IPNetwork('10.0.0.0/8'),            # Private network - local communication (RFC 1918)
    IPNetwork('100.64.0.0/10'),         # Carrier grade NAT (RFC 6598)
    IPNetwork('127.0.0.0/8'),           # Loopback addresses (RFC 990, RFC 1122)
    IPNetwork('169.254.0.0/16'),        # Link local (RFC 3927)
    IPNetwork('172.16.0.0/12'),         # Private network - local communication (RFC 1918)
    IPNetwork('192.0.0.0/24'),          # IANA IPv4 Special Purpose Address Registry (RFC 5736, RFC 6890)
    IPNetwork('192.0.2.0/24'),          # TEST-NET-1 examples and documentation (RFC 5737)
    # IPNetwork('192.31.196.0/24'),       # AS112-v4 [RFC 7535]
    # IPNetwork('192.52.193.0/24'),       # AMT [RFC 7450]
    IPNetwork('192.88.99.0/24'),        # Deprecated (6to4 Relay Anycast) (RFC 3068)
    IPNetwork('192.168.0.0/16'),        # Private network - local communication (RFC 1918)
    # IPNetwork('192.175.48.0/24'),       # Direct Delegation AS112 Service [RFC7534]
    IPNetwork('198.18.0.0/15'),         # Benchmarking (RFC 2544
    IPNetwork('198.51.100.0/24'),       # TEST-NET-2 documentation (RFC 5737)
    IPNetwork('203.0.113.0/24'),        # TEST-NET-3  documentation (RFC 5737)
    IPNetwork('224.0.0.0/4'),           # Multicast (RFC 5771), ranges all the way from 224/8 thru 239/8
    IPNetwork('240.0.0.0/4'),           # Reserved for future use, ranges all the way from 240/8 thru 255/8
])

# https://www.iana.org/assignments/iana-ipv6-special-registry/iana-ipv6-special-registry.xhtml
# https://www.iana.org/assignments/ipv6-address-space/ipv6-address-space.xhtml
IPV6_RESERVED = IPSet([
    IPNetwork('::1/128'),
    IPNetwork('::/128'),
    IPNetwork('::ffff:0:0/96'),
    IPNetwork('64:ff9b::/96'),
    IPNetwork('64:ff9b:1::/48'),
    IPNetwork('100::/64'),
    IPNetwork('2001::/23'),
    IPNetwork('2001::/32'),
    IPNetwork('2001:1::1/128'),
    IPNetwork('2001:1::2/128'),
    IPNetwork('2001:2::/48'),
    IPNetwork('2001:3::/32'),
    IPNetwork('2001:4:112::/48'),
    IPNetwork('2001:5::/32'),
    IPNetwork('2001:10::/28'),
    IPNetwork('2001:20::/28'),
    IPNetwork('2001:db8::/32'),
    IPNetwork('2002::/16'),
    IPNetwork('2620:4f:8000::/48'),
    IPNetwork('fc00::/7'),
    IPNetwork('fe80::/10'),
])

def get_ipv4_complement(v4set):
    return IPSet(['0.0.0.0/0']) - IPV4_RESERVED - v4set

def get_ipv6_complement(v6set):
    return IPSet(['2000::/3']) - v6set



