#
#
# Test Creating hosts
#
import pyops
import os
import json

#Configure Variables
# To use this, set prod_base to the rest url of the opsview server.
# Then in bash run
# $ export prod_ops_user=opsview_username
# $ read -s prod_ops_pass
# $ export prod_ops_pass
prod_user = os.environ['prod_ops_user']
prod_pass = os.environ['prod_ops_pass']
prod_base = "https://example-prod/opsview/rest/"

hosts = ["host1.example.com", "host2.example.com"]

#Create instance of the monitoring server
opsprod = pyops.opsview(prod_user,prod_pass,prod_base)

data = opsprod.get_host_by_name(hosts[0])

# Print the data for the host
print (opsprod.json_nice(data))

# Remove this when you have the bottom figured out
exit(0)

for host in hosts:
  print ("Modifying host " + host)
  data = opsprod.get_host_by_name(host)
  hostid = data["object"]["id"]

  data["object"]["hostattributes"].append( { "name": "SMART_DISK",
				           "arg1": None,
					   "arg2": None,
                                           "arg3": None,
                                           "arg4": None,
                                           "value": "/dev/sda"
              })

  data["object"]["hostattributes"].append( { "name": "SMART_DISK",
				           "arg1": None,
					   "arg2": None,
                                           "arg3": None,
                                           "arg4": None,
                                           "value": "/dev/sdb"
              })

  data["object"]["hosttemplates"].append( { "ref": "/rest/config/hosttemplate/216",
                                            "name": "CSC.CCCP SMART status check"
              })


  res = opsprod.put_data(data, 'config/host/' + hostid);
