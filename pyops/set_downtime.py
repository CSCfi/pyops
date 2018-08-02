#!/usr/bin/env python
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
                                     epilog=("Examples:\n"
                                             "./set_downtime.py -e +1d testserver1 testserver2\n"
                                             "./set_downtime.py -s '2018-08-10 08:00' -c "
                                             "'Server upgrade and maintenance' -e +8h prodserver1\n"
                                            "./set_downtime.py -d testserver1 testserver2 prodserver1\n"
                                            "./set_downtime.py -g -e +1d 'compute node group with spaces'"
                                             "'compute node group 2'")
                                     )

    parser.add_argument('hosts', nargs='*', help="A space separated list of hosts (or hostgroups, see -g) to apply the downtime to.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-e', '--endtime', dest="endtime", help="Downtime end time in an opsview format (e.g. +10m, +2d or '2018-08-10 15:00').")
    group.add_argument('-d', '--delete', dest="delete", action="store_true", help="Delete downtimes instead of adding them.")
    parser.add_argument('-c', '--comment', dest="comment", default="Dowtime set by pyops", help="Comment for the downtime")
    parser.add_argument('-s', '--starttime', dest="starttime", default="now", help="Start time in an opsview format ('2018-08-10 13:00'). Defaults to 'now'")
    parser.add_argument('-g', '--group', dest="group", action="store_true", help="Interpret the host list as a list of hostgroup names, and apply the downtime to all the hosts in the groups.")

    args = parser.parse_args(argv[1:])

    try:
        prod_user = os.environ['prod_ops_user']
        prod_pass = os.environ['prod_ops_pass']
        prod_base = os.environ['prod_ops_base']
    except KeyError:
        print(
            'Error: You need to specify the "prod_ops_user" and "prod_ops_pass" and "prod_ops_base" environment variables. For example:')
        print('export prod_ops_user="username"')
        print('read -s prod_ops_pass')
        print('export prod_ops_pass')
        print('export prod_ops_base="https://your-opsview-server/opsview/rest/"')
        return 1

    if len(args.hosts) < 1:
        parser.print_help()
        print('Error: Specify one or more hosts/hostgroups')
        return 1

    opsprod = pyops.opsview(prod_user, prod_pass, prod_base)
 
    if args.group:
        hostlist = []
        for host in args.hosts:
            res = opsprod.get_hostgroup_by_name(host)
            if not res:
                print("Warning: could not find hostgroup '%s'" % host)
            else:
                hltemp = [item["name"] for item in res["object"]["hosts"]]
                hostlist.extend(hltemp)

    else:
        hostlist = args.hosts

    if args.endtime:
        opsprod.set_host_downtime(hostlist, args.starttime, args.endtime, args.comment)
    if args.delete:
        opsprod.remove_host_downtime(hostlist)


if __name__ == "__main__":
    main()
