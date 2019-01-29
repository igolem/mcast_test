#!/usr/local/bin/python3

# script: ipv4_mcast_test.py
# author: jason mueller
# created: 2019-01-28
# last modified: 2019-01-29
#
# purpose:
# Script to test basic multicast functionality.
# Script can be an IPv4 multicast source or listener.
# Used to verify multicast forwarding and build multicast state in routers.
# Built on a script I have used for years for multicast testing,
# original date not recoverable.
#
# usage:
# help: python3 ipv4_mcast_test.py -h
# listener: python3 ipv4_mcast_test.py
# source: python3 ipv4_mcast_test.py -s
# use ctrl-c to break out of listener or source (both functions are an infinite loop)
#
# python version: 3.7.2


import argparse
import socket
import struct
import datetime
import time


def get_cli_switches():
    cli_parser = argparse.ArgumentParser(
        description = 'Multicast test script. Script can act as listener or source.',
        epilog = '\033[91mNo guarantees. Use at your own risk.\033[0m\n')

    cli_parser.add_argument('-v', '--version',
                            action = 'version',
                            version = '%(prog)s 1.0.3')
    cli_parser.add_argument('-s',
                            dest = 'source',
                            action = 'store_true',
                            help = 'set script to be a multicast data source. ' + 
                                   'default is to be a multicast listener.')
    cli_parser.add_argument('-g',
                            dest = 'group',
                            default = '239.1.1.1',
                            help = 'set mutlicast group for source or listener.')
    cli_parser.add_argument('-p',
                            dest = 'port',
                            default = 2187,
                            type = int,
                            help = 'set UDP unprivileged port for source or listener.')
    cli_parser.add_argument('-i',
                            dest = 'interval',
                            default = 2,
                            type = int,
                            help = 'set delay in seconds between sending messages ' +
                                   'when script is a multicast source (range: 1-60).')
    cli_parser.add_argument('-t',
                            dest = 'ttl',
                            default = 10,
                            type = int,
                            help = 'set TTL in IP header (range: 1-31).')

    cli_args = vars(cli_parser.parse_args())
    return(cli_args)


# is_ipv4_format
# verify supplied string is valid IPv4 address format
#   All IPv4 addresses from 0.0.0.0 through 255.255.255.255 are true
# returns: True or False
# recycled from my net_eng.py module to remove dependency
def is_ipv4_format(candidate):
    is_ipv4 = True            

    try:
        octets = list(map(int, candidate.split('.')))

        # verify IP address contains four components
        if len(octets) != 4:
            is_ipv4 = False

        # verify values are integer versions of binary octets in candidate IP
        else:
            for octet in octets:
                if (octet < 0 or octet > 255):
                    is_ipv4 = False
    except:
        is_ipv4 = False
        
    return is_ipv4


# is_ipv4_mcast
# verify supplied string is valid IPv4 multicast address
# returns: True or False
# recycled from my net_eng.py to remove dependency
def is_ipv4_mcast(candidate):
    is_mcast = True            

    try:
        # verify supplied string conforms to IPv4 format
        is_mcast = is_ipv4_format(candidate)

        if is_mcast:
            octets = list(map(int, candidate.split('.')))

            # verify first octet valid multicast value
            if (octets[0] < 224 or octets[0] > 239):
                    is_mcast = False
    except:
        is_mcast = False
        
    return is_mcast


# is_unpriv_port
# verify supplied integer (or int version of string) corresponds to an unprivileged TCP/UDP port
# returns: True or False
# recycled from my net_eng.py module to remove dependency
def is_unpriv_port(port):
    unpriv_port = True

    try:
        if (int(port) < 1024 or int(port) > 65535):
            unpriv_port = False

    except:
        unpriv_port = False
    
    return unpriv_port


# normalize provided CLI arguments
def santize_args(cli_args):
    args = {}
    
    # verify multicast group
    if not is_ipv4_mcast(cli_args['group']): 
        args['group'] = '239.1.1.1'
        print('Invalid multicast group provided, using 239.1.1.1.')
    else:
        args['group'] = cli_args['group']

    # verify port supplied is valid unprivileged port
    if not is_unpriv_port(cli_args['port']):
        args['port'] = 2187
        print('Port specified was not a valid unprivileged port number, using 2187.')
    else:
        args['port'] = cli_args['port']

    if cli_args['source']:
        # verify interval is between 1-60
        if (cli_args['interval'] < 1 or cli_args['interval'] > 60):
            args['interval'] = 2
            print('Specified interval was not in allowed range of 1-60, using 2.')
        else:
            args['interval'] = cli_args['interval']
    
        # verify ttl is between 1-31
        if (cli_args['ttl'] < 1 or cli_args['ttl'] > 31):
            args['ttl'] = 10
            print('Specified TTL was not in allowed range of 1-31, using 10.')
        else:
            args['ttl'] = cli_args['ttl']

    return args


# multicast listener
def mcast_listener(args):
    try:
        # create listener socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', args['port']))
        listener = struct.pack("4sl",
                               socket.inet_aton(args['group']),
                               socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP,
                        socket.IP_ADD_MEMBERSHIP,
                        listener)

        print('\nMulticast listener invoked at ' + str(datetime.datetime.now()) + '.')
        print('Listening to multicast group ' +
              args['group'] + ':' +
              str(args['port']) + '.\n')

        # print data received on socket
        while True:
            message = sock.recv(1024)
            print(str(datetime.datetime.now()) + ' received message to ' + 
                  args['group'] + ':' + str(args['port']) +
                  ': \"' + str(message) + '\"')
    except:
        print('\nUnexpected error occurred or loop exited via ctrl-c break.\n')


# multicast source
def mcast_source(args):

    try:
        # create socket for sending timestamp message
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, args['ttl'])

        print('\nMulticast source invoked at ' + str(datetime.datetime.now()) + '.')
        print('Sourcing timestamp message to ' + args['group'] + ':' + str(args['port']) +
              ' every ' + str(args['interval']) + ' seconds.\n')

        # send data to socket at specified interval
        try:
            host = socket.gethostname()
        except:
            host = 'hostname_undefined'

        # send message to socket at specified interval
        while True:
            message = str(datetime.datetime.now()) + '; ' + host
            sock.sendto(message.encode('utf-8'), (args['group'], args['port']))
            print('Sent message to ' + args['group'] + ':' + str(args['port']) + ': ' +
                  '\"' + message + '\"')
            time.sleep(args['interval'])

    except:
        print('\nUnexpected error occurred or loop exited via ctrl-c break.\n')


def march_on_dunsinane():
    cli_args = get_cli_switches()

    args = santize_args(cli_args)

    if cli_args['source']:
        mcast_source(args)
    else:
        mcast_listener(args)        


if __name__ == '__main__':
    march_on_dunsinane()
