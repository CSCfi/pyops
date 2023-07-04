#!/usr/bin/python
#
# Chris Thomas and Peter Jenkins and Johan Guldmyr and Kalle Happonen
#
# Date: 15/Feb/2017
#
# Version:0.4
#
import logging
#import os
import json
import datetime
import re
import requests


# We need to verify certificates:
# https://urllib3.readthedocs.org/en/latest/security.html
import urllib3
import certifi

class PyOpsException(Exception):
    ''' Base Exception '''
    msg_fmt = "An unknown exception occurred."

    def __init__(self, **kwargs):
        Exception.__init__(self)
        self.message = self.msg_fmt % kwargs

    def __str__(self):
        return self.message

class LoginFailedException(PyOpsException):
    msg_fmt = "%(msg)s"

##### CLASS STARTED:

class Opsview:
    def __init__(self, ops_user, ops_pass, ops_base):
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.WARNING)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s:%(name)s %(message)s')
        handler.setFormatter(formatter)
        self.log.addHandler(handler)
        self.log.debug("\n\n###################### New Run of Debugging    ######################################")
        self.log.debug(datetime.datetime.utcnow())

        # Send any logs from libraries into our logs
        logging.captureWarnings(True)

        # Debug code, not needed
        #self.init_ssl(ops_base)

        self.ops_user = ops_user
        self.ops_pass = ops_pass
        self.ops_base = ops_base

        # We need the full url to log in, but sometimes just the server url
        url_parts = re.search('(^https://[a-z-.]*/)(.*)', ops_base)
        self.ops_url = url_parts.group(0)

        # Login and get the token for all future requests
        self.token = self.get_token()
        self.log.debug("Got token:", self.token)

        # Setup headers for all future requests
        self.headers = {
            "Content-Type": "application/json",
            "X-Opsview-Username":self.ops_user,
            "X-Opsview-Token": self.token
            }

        self.log.info("Connected to Opsview")

    def init_ssl(self, test_url):
        '''
        For testing the connection works. Not requred.
        '''

        http = urllib3.PoolManager(
            cert_reqs='CERT_REQUIRED', # Force certificate check.
            ca_certs=certifi.where(),    # Path to the Certifi bundle.
        )

        # You're ready to make verified HTTPS requests.
        try:
            r = http.request('GET', test_url)
        except urllib3.exceptions.SSLError as e:
            self.log.warning('SSL problems')
            raise

    def get_token(self):
        '''
        Log into Opsview and get a Token
        '''
        login = {'username': self.ops_user,
                'password': self.ops_pass}
        try:
            response = requests.post(self.ops_base + "login", login, verify=False)
            token = response.json()['token']
        except KeyError as e:
            msg = response.json()['message']
            raise LoginFailedException(msg=msg)

        return token

    def destroy_token(self):
        '''
        Logout

        NOTE: not yet working!
        '''
        response = requests.delete(self.ops_base + "login", headers=self.headers, verify=False)
        return response

    def get_data(self, url):
        '''
        Helper for making GET requests to the API
        '''
        result = requests.get(self.ops_base + url, headers=self.headers, verify=False)
        # We care this request was valid
        result.raise_for_status()

        self.log.debug(result.text)
        return result.json()

    def post_data(self, data, path):
        '''
        Post data to API.
        Maybe needed to add new hosts - documentation is horrible on this point
        '''
        result = requests.post(self.ops_base + path, json=data,    headers=self.headers, verify=False)

        # We care this request was valid
        result.raise_for_status()
        return result.json()


    def put_data(self, data, path):
        '''
        Put data to API
        Used for updates to existing objects, perhaps other things.
        '''
        result = requests.put(self.ops_url + path, json=data, headers=self.headers, verify=False)

        # We care this request was valid
        result.raise_for_status()
        return result.json()


    def update_object(self, ops_obj, ops_obj_type):
        '''
        Update a remote opsview object using the object's ID
        '''
        url = 'config/' + ops_obj_type + '/' + ops_obj['object']['id']
        return self.put_data(ops_obj, url)

    def json_nice(self, data):
        '''
        Format json for humans
        '''
        return json.dumps(data, indent=4)

    def ops_reload(self, check="status"):
        '''
        Restart the opsview server.

        This is the same as reloading the config in the GUI and is needed before changes take effect.
        This does the following:
        - Dumps the Opsview database into nagios config files (ugly ones!)
        - Restarts the nagios server

        This is propper scary because we might restart while someone else is making changes. Opsview's
        design is the issue here. Probably best to make changes with the api and manually restart.
        '''
        if "status" in check:
            result = self.get_data("reload")
            if result['server_status'] =="0":
                self.log.info("Server configuration up to date, no changes")
                self.log.debug(self.json_nice(result))
            return result
        elif "reload" in check:
            result = self.post_data("","reload")
            self.log.debug("ops_reload : reload ",    result)
            self.log.info(result)

    '''
    User facing methods.

    These should help make this wrapper easier to use.

    '''

    def get_serverinfo(self):
        return self.get_data("serverinfo")

    def get_user(self):
        return self.get_data("user")

    def get_downtimes(self, page_id):
        try:
            result = self.get_data('downtime?' + str("page") + '=' + str(page_id))
        except requests.exceptions.HTTPError as e:
            self.log.critical(e)
            raise
        return result

    def get_downtimes_by_hg(self, page_id, hostgroup_id):
        try:
            result = self.get_data('downtime?' + str("page=") + str(page_id) + str("&hostgroupid=") + str(hostgroup_id))
        except requests.exceptions.HTTPError as e:
            self.log.critical(e)
            raise
        return result

    def set_downtime(self, hg_id, starttime, endtime, comment):
        '''
        ##
        # Thank you
        # https://www.pythian.com/blog/put-opsview-hosts-into-downtime-via-the-shell/
        ##
        # Set a downtime for hg_id from starttime to endtime with comment
        ## Lessons learnt while writing this:
            - API user needs to have DOWNTIMEALL permissions
            - send the data with json.loads like: post_data(json.loads('{ "json": "json" }')), otherwise you get an error like this:
                JSON text must be an object or array (but found number, string, true, false or null, use allow_nonref to allow this) at (eval 1868) line 161, <\$fh> line 1.
            - error "no object chosen" in opsview-web.log probably means the URL doesn't have a valid host= or hostgroupid= parameter, it should be like these (without starttimes etc):
        /opsview/rest/downtime?host=my-test-server
        /opsview/rest/downtime?hostgroupid=103
        ######

        # Formats a la bash:
        starttime=`date +"%Y/%m/%d %H:%M:%S"`
        endtime=`date +"%Y/%m/%d %H:%M:%S" -d "$hours_of_downtime hours"`
        # endtime can also be like this:
        endtime="+9h"
        comment="$0 api call"
        #

        # TODO: Delete downtimes.
        # This needs a new function which can do http DELETE, see url above for curl example.

        '''
        result = self.post_data(json.loads('{ "starttime" : "%s", "endtime" : "%s", "comment" : "%s" }' % (starttime, endtime, comment)),"downtime?hostgroupid=%s" % hg_id)
        self.log.debug("downtime : downtime ", result)
        self.log.info(result)

    def set_host_downtime(self, hosts, starttime, endtime, comment):
        '''
        Create downtime for the hostlist.

        Lessons learned: Setting downtime by hostid, not hostname, caused a 403 forbidden error.
        '''

        for host in hosts:
            try:
                self.post_data(json.loads('{ "starttime" : "%s", "endtime" : "%s", "comment" : "%s" }  ' % (starttime, endtime, comment)),"downtime?hst.hostname=%s" % host)
                self.log.debug("Downtime set for %s" % host)
            except requests.exceptions.HTTPError:
                self.log.error("Could not set downtime for %s" % host)

    def remove_host_downtime(self, hosts):
        '''
        Remove all coming downtimes for the hostlist.
        '''
        for host in hosts:
            try:
                requests.delete(self.ops_base + "downtime?hst.hostname=%s" % host, headers=self.headers, verify=False)
            except requests.exceptions.HTTPError:
                pass

    def get_configitem(self,item_type, item_id):
        try:
            result = self.get_data('config/' + str(item_type) + '/' + str(item_id))
        except requests.exceptions.HTTPError as e:
            self.log.critical(e)
            raise
        return result

    def get_statusitem(self,item_type, item_id):
        try:
            result = self.get_data('status/' + str(item_type) + str("?%s=%s" % (item_type,item_id)))
        except requests.exceptions.HTTPError as e:
            self.log.critical(e)
            raise
        return result

    def get_hostgroup_statusitem(self,item_type, item_id):
        try:
            result = self.get_data('status/' + str(item_type) + str("?hostgroupid=%s" % (item_id)))
        except requests.exceptions.HTTPError as e:
            self.log.critical(e)
            raise
        return result

    def get_config_by_name(self, item_type, search_string):
        '''
        Search by name and return the item if there is just one match.
        Otherwise return false
        '''
        result = self.search_configitem(item_type, search_string)
        if result['summary']['rows'] == '1':
            return self.get_configitem(item_type, result['list'][0]['id'])
        else:
            return False

    def get_hostconfig(self,host_id=None):
        return self.get_configitem('host', host_id)

    def get_status_host_by_name(self,host_name):
        return self.get_statusitem('host', host_name)

    def get_host_by_name(self,host_name):
        return self.get_config_by_name('host', host_name)

    def get_hosttemplate_by_id(self,template_id):
        return self.get_configitem('hosttemplate', template_id)

    def get_hosttemplate(self,template_name):
        return self.get_config_by_name('hosttemplate', template_name)

    def get_servicecheck(self,servicecheck_id):
        return self.get_configitem('servicecheck', servicecheck_id)

    def get_status_hostgroup(self,hostgroup_id):
        return self.get_hostgroup_statusitem('service', hostgroup_id)

    def get_hostgroup(self,hostgroup_id):
        return self.get_configitem('hostgroup', hostgroup_id)

    def get_hostgroup_by_name(self, hostgroup_name):
        return self.get_config_by_name('hostgroup', hostgroup_name)

    def get_status_hostgroup_by_id(self, hostgroup_id):
        return self.get_hostgroup_statusitem('hostgroup', hostgroup_id)

    def get_servicegroup(self,servicegroup_id):
        return self.get_configitem('servicegroup', servicegroup_id)

    def get_plugin(self,plugin_name):
        ''' Broken '''
        return self.get_configitem('plugin', plugin_name)

    '''
    Search helpers
    '''

    def search_configitem(self, item_type, search_string):
        ''' The opsview API doesn't handle python generated JSON too well
        so we'll just build the string ourselves '''
        self.log.info("Search" + item_type + ' for ' + search_string)
        return self.get_data('config/' + item_type +
                                                '?rows=all&json_filter={"name":{"-like":"%25' +
                                                search_string + '%25"}}')

    def search_hosttemplate(self, search_string):
        '''
        Returns a list JSON file with a list of hosttemplates
        '''
        return self.search_configitem('hosttemplate', search_string)

    def search_ip(self, search_ip):
        return self.search_configitem('host', search_ip)

    def search_name(self, search_name):
        return self.search_configitem('host', search_name)

    '''
    Update helpers
    '''
    def update_host(self, ops_obj):
        '''
        Update an existing opsview host with a modified host object

        Returns some json, which might be the same as what you sent.
        '''
        return self.update_object(ops_obj, 'host')

    '''
    Set helpers
    '''
    def set_host_attribute(self, hostname, name, value):
        '''
        Sets hosts attributes. Dangerious! If you have multiple entries with the same name (e.g. DISK),
        the will be removed! You have been warned.
        '''
        new_attr = {'name': name, 'arg1': None, 'arg2': None,
                                'arg3': None, 'arg4': None, 'value': value }

        ''' Get the current config for the host '''
        host = self.get_host_by_name(hostname)

        ''' get_host_by_name() returns False if there is no match '''
        if host:
            host_attrs = host['object']['hostattributes']
            for attr in host_attrs:
                ''' If the attribute is already set once, remove it!
                Not all attributes work this way! DISK for example '''
                if attr['name'] == name:
                    host_attrs.remove(attr)
            ''' Append the new attribute '''
            host_attrs.append(new_attr)

            ''' Add the attributes back to the object.
            (assuming we are working on a copy of the array) '''
            host['object']['hostattributes'] = host_attrs
            self.update_host(host)
            return True
        else:
            return False

    def set_hostgroup_attribute(self, hostgroup_name, name, value):
        hostgroup = self.get_hostgroup_by_name(hostgroup_name)
        if hostgroup:
            for host in hostgroup['object']['hosts']:
                self.set_host_attribute(host['name'], name, value)
            return True
        else:
            return False
