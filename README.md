# pyops - Python bindings for the Opsview API

Usage

How to set downtime:

    $ pip install git+ssh://git@github.com/CSCfi/pyops.git
    $ pyops-downtime --help
    $ export prod_ops_user="username"
    $ read -s prod_ops_pass
    $ export prod_ops_pass
    $ export prod_ops_base="https://your-opsview-server/opsview/rest/""
    $ pyops-downtime -e +1d testserver1 testserver2

Adding node for monitoring:

First we need to edit examples/createhostExample.py file and a add node name from where pyops will fetch template data.
For example, if you want to add a new node in devel environment, then we can take metadata from a devel node
reference-server.domain. If your newserver is new-server.domain, then we can do following.

    $ export prod_ops_user="username"
    $ read -s prod_ops_pass
    $ export prod_ops_pass
    $ export prod_ops_base="https://your-opsview-server/opsview/rest/""
    $ vim examples/createhostExample.py
data = opsprod.get_host_by_name("reference-server.domain")
newserver = { "ip": "new-server.domain", "name": "new-server.domain" }

    $ PYTHONPATH=./pyops python examples/createhostExample.py

