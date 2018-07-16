#!/usr/bin/python
#
# Set downtime for hosts
#
import os
import sys
import pyops
import argparse

#Configure Variables
# To use this, set prod_base to the rest url of the opsview server.
# Then in bash run
# $ export prod_ops_user=opsview_username
# $ read -s prod_ops_pass
# $ export prod_ops_pass

def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(description='Set downtime for hosts in opsview.', 
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""Examples:
./set_downtime.py -e +1d testserver1 testserver2
./set_downtime.py -s '2018-08-10 08:00' -c 'Server upgrade and maintenance' -e +8h prodserver1
./set_downtime.py -d testserver1 testserver2 prodserver1""")

    parser.add_argument('hosts', nargs='*', help="A space separated list of hosts to apply the downtime to.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-e', '--endtime', dest="endtime", help="Downtime end time in an opsview format (e.g. +10m, +2d or '2018-08-10 15:00').")
    group.add_argument('-d', '--delete', dest="delete", action="store_true", help="Delete downtimes instead of adding them.")
    parser.add_argument('-c', '--comment', dest="comment", default="Dowtime set by pyops", help="Comment for the downtime")
    parser.add_argument('-s', '--starttime', dest="starttime", default="now", help="Start time in an opsview format ('2018-08-10 13:00'). Defaults to 'now'")

    prod_base = "https://mon-esp.csc.fi/opsview/rest/"
    try:
        prod_user = os.environ['prod_ops_user']
        prod_pass = os.environ['prod_ops_pass']
    except KeyError:
        print 'Error: You need to specify the "prod_ops_user" and "prod_ops_pass" environment variables. For example:'
        print 'export prod_ops_user="username"'
        print 'read -s prod_ops_pass'
        print 'export prod_ops_pass'
        return 1

    args = parser.parse_args(argv[1:])
    if len(args.hosts) < 1:
        parser.print_help()
        print 'Error: Specify one or more hosts'
        return 1

    opsprod = pyops.opsview(prod_user, prod_pass, prod_base)
    if args.endtime:
        opsprod.set_host_downtime(args.hosts, args.starttime, args.endtime, args.comment)
    if args.delete:
        opsprod.remove_host_downtime(args.hosts)

#for host in hosts:
#    print "Setting downtime for host " + host
    #opsprod.set_host_downtime([host], "now", "+10m", "Test by kalle")
#    opsprod.remove_host_downtimes(hosts)

if __name__ == "__main__":
    main()
