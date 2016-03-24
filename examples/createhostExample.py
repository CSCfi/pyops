#
#
# Test Creating hosts
#
import pyops
import os
import json

#Configure Variables
dev1_user = os.environ['dev1_ops_user']
dev1_pass = os.environ['dev1_ops_pass']
dev1_base = "https://example-devel/opsview/rest/"

prod_user = os.environ['prod_ops_user']
prod_pass = os.environ['prod_ops_pass']
prod_base = "https://example-prod/opsview/rest/"


#Create instance of the monitoring server
opsdev = pyops.opsview(dev1_user,dev1_pass,dev1_base)
opsprod = pyops.opsview(prod_user,prod_pass,prod_base)

data = opsesp.get_hostconfig("1")
print opsesp.json_nice(data)

print opsesp.json_nice(data)

newserver = { "object": { "ip": "1.2.3.4",  "name": "example",} ,}

print opsesp.json_nice(newserver)

response = opsesp.post_data(opsesp.json_nice(newserver),"config/host/1")
print response



