# -*- coding: utf-8 -*-

"""
pypleskapi library
~~~~~~~~~~~~~~~~~~~~~

Provide built-in functions to make requests to the Plesk Panel api in severall formats.

usage:

   >>> import pleskapi
   # Get the IP addresses from Plesk database.
   >>> packet = { 'packet': { '@version': '1.6.3.5', 'ip' : { 'get' : None } } }
   >>> r = pleskapi.send_packet(packet, user='admin', password='setup')
   >>> r.api_response()
   {'version': '1.6.3.5', 'result': {'status': 'ok'}}
   >>> r.dict
   {'packet': {'ip': {'get': {'result': {'status': 'ok', 'addresses': {'ip_info': {'interface': 
   'eth0', 'type': 'shared', 'netmask': '255.255.255.0', 'ip_address': '192.168.1.106', 
   'default': None}}}}}, '@version': '1.6.3.5'}}

See more `pleskapi.api`.

:copyright: (c) 2012 by Sandro Mello.
:license: ISC, see LICENSE for more details.

"""

__title__ = 'pypleskapi'
__version__ = '0.1'
#__build__ = 0x001400
__author__ = 'Sandro Mello'
__license__ = 'ISC'
__copyright__ = 'Copyright 2012 Sandro Mello'

from .api import build, send_packet