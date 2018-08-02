# pyops - Python bindings for the Opsview API

Usage

    $ pip install pip install git+ssh://git@github.com/CSCfi/pyops.git
    $ pyops-downtime --help
    $ export prod_ops_user="username"
    $ read -s prod_ops_pass
    $ export prod_ops_pass
    $ export prod_ops_base="https://your-opsview-server/opsview/rest/""
    $ pyops-downtime -e +1d testserver1 testserver2


