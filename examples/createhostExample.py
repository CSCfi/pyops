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


#Create instance of the monitoring server
opsprod = pyops.opsview(prod_user,prod_pass,prod_base)

# The easiest way of adding a server is copying the config from an existing server
# First, get the info from a server you want

data = opsprod.get_host_by_name("name_of_the_server")

# Print the data for the host
print opsprod.json_nice(data)

# Get the ID of the hosts (this is what you use as a source for the copy)
hostid = data["object"]["id"]
print hostid

# You can also get the host data by id
data = opsprod.get_hostconfig(hostid)
print opsprod.json_nice(data)

# Let's add a new server. We only define IP and name, the rest is copied from the
# original server
newserver = { "ip": "newhostname_or_ip", "name": "newhostname" }

# By posting this data to the URL rest/config/host/hostid opsview will copy the
# data of hostid, create a new host, and modify it with the data you posted.
# So in this case, we'll take a copy of a host, and change the IP and name for
# the new host. 

response = opsprod.post_data(newserver,"config/host/" + hostid)
print response
