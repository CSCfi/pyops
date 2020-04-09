#
#
# Test Creating hosts

# usage: 
# $ cd pyops
# $ $EDITOR ../examples/enable_host_flapping_detection.py 
# $ # and change prod_base perhaps and change the host group ids..
# $ python ../examples/enable_host_flapping_detection.py 
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
prod_base = "https://monitoring.example.org/opsview/rest/"

#Create instance of the monitoring server
opsprod = pyops.opsview(prod_user,prod_pass,prod_base)

data0 = opsprod.get_hostgroup(11111111)
data1 = opsprod.get_hostgroup(222222222)
data2 = opsprod.get_hostgroup(333333333)

# Print the data for the host
#print opsprod.json_nice(data0)

hosts = []

for host in data0['object']['hosts']:
  hosts.append(host['name'])
for host in data1['object']['hosts']:
  hosts.append(host['name'])
for host in data2['object']['hosts']:
  hosts.append(host['name'])

print (hosts)

# Remove this when you have the bottom figured out
exit(0)

for host in hosts:
  print ("Attempting to modify host " + host)
  data = opsprod.get_host_by_name(host)
  hostid = data["object"]["id"]
  cnt = 0

  if data["object"]["notification_interval"] == "60":
    print (data["object"]["notification_interval"])
    print ("would set notification_interval from 60 to 0")
    data["object"]["notification_interval"] = "0"
    cnt = cnt + 1

  if data["object"]["flap_detection_enabled"] == "0":
    print (data["object"]["flap_detection_enabled"])
    print ("would enable flap detection")
    data["object"]["flap_detection_enabled"] = "1"
    cnt = cnt + 1

  if cnt != 0:
    print ("Sending new config to opsview")
    res = opsprod.put_data(data, 'config/host/' + hostid);
  else:
    print ("Not changing anything")

if cnt != 0:
  print ("Reload opsview")
