# -*- coding: utf-8 -*-
"""
pleskapi.base
~~~~~~~~~~~~

This module contains the main built-ins for exercing the requests to the Plesk Panel endpoint.
Note: For using OrderedDict in the requests, only with Python 2.7+ or install ordereddict from http://pypi.python.org.
"""
import urllib2
from converter import xml2elem, dict2xml, elem2xml, xml2dict, xml2json
from xml.etree.ElementTree import Element as xmlobj
import warnings

odict = True
try: import OrderedDict
except ImportError: odict = False

warnings.simplefilter('once')

def build(packet, **kwargs):
    """ Build the :class:`BaseRequest <BaseRequest>`.
    :param **kwargs: Arguments that BaseRequest takes.
    """
    return BaseRequest(packet, **kwargs)

def send_packet(packet, **kwargs):
    """ Start a request to the Plesk Panel endpoint.
    Return a :class:`BaseResponse <BaseResponse>`.
    :param **kwargs: Arguments that BaseRequest takes.
    """
    return BaseRequest(packet, **kwargs).send()

class PleskApiError(Exception): pass

class StructDict(dict):
    def __init__(self, version):
        self.version = version

    def __getitem__(self, key):
        if key in self:
            return self.get(key)
        return self.setdefault(key, StructDict(self.version))

    def dict(self):
        warnings.warn("Missing OrderedDict package. Dict's are not ordered, elements SHOULD be in order or the request may fail.", ImportWarning)
        packet = { 'packet' : {} }
        packet['packet'].update(self)
        packet['packet'].update({ '@version' : self.version })
        return packet

    def xml(self):
        warnings.warn("Missing OrderedDict package. Dict's are not ordered, elements SHOULD be in order or the request may fail.", ImportWarning)
        return dict2xml(self.dict())

class BaseRequest(object):
    def __init__(self, packet, server='localhost', port='8443',
                 user='admin', password='setup', key=None, timeout=240):
        """
        Represents the data that is going to be sent to the Plesk Panel endpoint.
        :param packet: The packet for sending to the Plesk Panel endpoint. Should be only in three formats: dict, OrderedDict or xml string (without headers).
        :param server: The server IP Address or uri. Default: localhost.
        :param port: The port of the Plesk Panel. Default: 8443.
        :param user: The credentials of the Plesk Panel. Default: admin.
        :param password: The password of the user. Default: setup.
        :param key: (optional) Use a secret key instead of username and password.
        :param timeout: The timeout of the request. Default: 240.
        """
        self.server = server
        self.port = port

        if isinstance(packet, dict):
            warnings.warn("Missing OrderedDict package. Dict's are not ordered, elements SHOULD be in order or the request may fail.", ImportWarning)
            self.packetxml = dict2xml(packet)
        elif isinstance(packet, type(xmlobj)):
            self.packetxml = elem2xml(packet)
        elif isinstance(packet, str):
            self.packetxml = packet
        else:
            raise TypeError('Unrecognized packet type.')
        if key:
            self.headers = { 'KEY': key }
        else:
            self.headers = { 'HTTP_AUTH_LOGIN': user, 'HTTP_AUTH_PASSWD': password }
        self.headers.update({'Content-Type': 'text/xml'})
        self.timeout = timeout

    @property
    def endpoint_uri(self):
        """ The Plesk Panel endpoint api constructed. """
        return 'https://{0}:{1}/enterprise/control/agent.php'.format(self.server, self.port)

    def send(self):
        """ Start the request to the Plesk Panel endpoint. Returns xml data.
        Return a :class:`BaseResponse <BaseResponse>`. """
        try:
            response = urllib2.urlopen(urllib2.Request(self.endpoint_uri, self.packetxml, self.headers), timeout=self.timeout)
            responsepacket = response.read().strip().replace('\n', '').encode('utf-8')
            return BaseResponse(responsepacket)
        except urllib2.URLError, e:
            if e.code == 500:
                raise PleskApiError('Error requesting plesk api endpoint. Check server logs for more info.')
            raise

class BaseResponse(object):
    def __init__(self, rpacket):
        """ Represents the response data returned from the Plesk Panel api.
        :param rpacket: The xml packet response from the Plesk Panel api.
        """
        self._rpacket = rpacket
        self._dict = self.todict()

    # TODO: Testar c/resposta retornando lista
    def response(self, bare=True):
        """ Extract the 'result' node containing only the status of the response.
        :param bare: True returns everthing which is not a dict. False returns everthing. Default: True
        """
        self._validate()
        result = self._extract_result(self.dict, bare)
        # Return the full packet if the 'result' node is a list
        if isinstance(result, list):
            return self.dict
        version = self.dict['packet']['@version']
        return { 'result' : result, 'version' : version }

    def _validate(self):
        if 'system' in self.dict['packet']:
            raise PleskApiError(self.dict['packet']['system'])
        r = self._extract_result(self.dict)
        if not isinstance(r, list):
            if r.get('status') == 'error':
                raise PleskApiError(r)

    def _extract_result(self, packet, bare=True):
        def extract(packet):
            ext = {}
            for key in packet:
                try:
                    # Domains xml schema plesk bug.
                    if 'result' in packet['result']:
                        packet['result'] = packet['result']['result']
                    for rkey in packet['result']:
                        # If the 'result' node is a list, end loop
                        if isinstance(packet['result'], list):
                            ext = []
                            break
                        if bare:
                            if not isinstance(packet['result'][rkey], dict):
                                ext[rkey] = packet['result'][rkey]
                        else:
                            ext[rkey] = packet['result'][rkey]
                except KeyError:
                    # 'result' not find, move to the next record
                    if not isinstance(packet[key], dict):
                        continue
                    return extract(packet[key])
                except TypeError:
                    # 'ext' is not a dict, continue loop
                    continue
            return ext
        ext = extract(packet)
        if isinstance(ext, list):
            return ext
        if not ext:
            raise ValueError('Could not extract the result from the response packet: %s' % packet)
        return ext

    def element(self):
        """ The response data as xml.etree.ElementTree.Element. """
        return xml2elem(self._rpacket)

    def json(self):
        """ The response data as json. """
        return xml2json(self._rpacket)

    def todict(self):
        """ Convert to dict. """
        return xml2dict(self._rpacket)

    @property
    def dict(self):
        """ The response data as dict. """
        return self._dict
