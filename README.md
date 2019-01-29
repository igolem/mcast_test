# ipv4_mcast_test

__ipv4_mcsat_test.py__ is Python script that can be used to create multicast state in routers and switches and test basic multicast forwarding.

There are no explicit or implied guarantees or warranties with this module.
See required Python modules below.

-----
## The script does the following:

* Running the script without any switches will invoke an IPv4 multicast listener \
  for group 239.1.1.1 port 2187. \
  The script assumes the underlying OS will make the proper IGMP join.

* Running the script with a -s switch will invoke an IPv4 multicast source \
  sending timestamp data every 2 seconds to group 239.1.1.1 port 2187.

* The following additional switches are supported:
    * -g [multicast group]; default 239.1.1.1
    * -p [UDP port]; default 2187
    * -i [delay interval in seconds between messages]; default 2
    * -t [TTL specified in IP header]; default 10

-----
## Required Python modules:
* socket
* argparse
* socket
* struct
* datetime
* time
