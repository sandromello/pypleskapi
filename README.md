# pypleskapi

Easy requests to [Parallels Plesk Panel](http://www.parallels.com/products/plesk/)

## About
Instead of building complex structures of XML, you can write all the requests in dict types.
Pypleskapi converts all the response and request into xml structures, you just need to know how to write
the corresponding dict structure.

    >>> from pleskapi.base import StructDict
    >>> from pleskapi import send_packet

    >>> packet = StructDict('1.6.3.5')
    >>> packet['webspace']['get']['filter'] = {'name' : 'cpro11674.publiccloud.com.br'}
    >>> packet['webspace']['get']['dataset']['gen_info']
    >>> packet = send_packet(packet.dict())
    {'version': '1.6.3.5', 'result': {'status': 'ok', 'filter-id': 'domain.tld', 'id': '36'}}

The conversion are based in this [project](http://github.com/hay/xml2json)

## Installation

TODO

## Prerequisites

TODO

## Overview - dict to XML

TODO
