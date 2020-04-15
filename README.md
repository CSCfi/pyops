# pyops - Python bindings for the Opsview API

Usage

How to set downtime:

    $ pip install pip install git+ssh://git@github.com/CSCfi/pyops.git
    $ pyops-downtime --help
    $ export prod_ops_user="username"
    $ read -s prod_ops_pass
    $ export prod_ops_pass
    $ export prod_ops_base="https://your-opsview-server/opsview/rest/""
    $ pyops-downtime -e +1d testserver1 testserver2

Adding node for monitoring:

First we need to edit examples/createhostExample.py file and a add node name from where pyops will fetch template data.
For example, if you want to add a new nodes in devel environment, then we can take metadata from a devel node p5.pouta.csc.fi.
If your newserver is p20.pouta.csc.fi, then we can do following.

    $ export prod_ops_user="username"
    $ read -s prod_ops_pass
    $ export prod_ops_pass
    $ export prod_ops_base="https://your-opsview-server/opsview/rest/""    
    $ vim examples/createhostExample.py
data = opsprod.get_host_by_name("p5.pouta.csc.fi")
newserver = { "ip": "p20.pouta.csc.fi", "name": "p20.pouta.csc.fi" }

    $ python pyops/pyops.py examples/createhostExample.py

