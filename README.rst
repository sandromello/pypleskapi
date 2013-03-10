Pypleskapi
==========

Easy requests to `Parallels Plesk Panel API RPC <http://www.parallels.com/products/plesk/>`_.

About
-----
Instead of building complex structures of XML, you can write all the requests in dict types.
Pypleskapi converts dict type packets into XML structures, and so as the other way around,
you just need to know how to write the corresponding dict structure.

.. code-block:: pycon

    >>> from pleskapi import StructDict
    >>> from pleskapi import send_packet

    >>> packet = StructDict('1.6.3.5')
    >>> packet['webspace']['get']['filter'] = {'name' : 'domain.tld'}
    >>> packet['webspace']['get']['dataset']['gen_info']

    >>> print packet.dict()
    {'packet': {'webspace': {'get': {'filter': {'name': 'domain.tld'}, 'dataset': {'gen_info': {}}}}, '@version': '1.6.3.5'}}

    >>> print packet.xml(True)
    <?xml version="1.0" encoding="UTF-8"?>
    <packet version="1.6.3.5">
      <webspace>
        <get>
          <filter>
            <name>domain.tld</name>
          </filter>
          <dataset>
            <gen_info/>
          </dataset>
        </get>
      </webspace>
    </packet>

    >>> r = send_packet(packet.dict())
    >>> r.response()
    {'version': '1.6.3.5', 'result': {'status': 'ok', 'filter-id': 'domain.tld', 'id': '36'}}
	
StructDict builds chain's of dict without expliciting, common dict's are build this way:

.. code-block:: pycon

	>>> d = dict() or {}
	>>> d['webspace'] = {}
	{'webspace': {}}

You need to create a new dict for every key:

.. code-block:: pycon

	>>> d['webspace'] = {}
	>>> d['webspace']['get'] = {}
	{'webspace': {'get': {}}}
	>>> d['webspace']['get']['filter'] = { 'name' : 'domain.tld' }
	Traceback (most recent call last):
	  File "<stdin>", line 1, in <module>
	KeyError: 'get'

With StructDict you can build chain's of dict:

.. code-block:: pycon

	>>> from pleskapi import StructDict
	""" 1.6.3.5 refer to  packet header body - <packet version="1.6.3.5">...</packet> """
	>>> sd = StructDict('1.6.3.5')
	>>> sd['webspace']['get']['filter']
	{}
	>>> sd
	{'webspace': {'get': {'filter': {}}}}
	>>> print sd.xml()
	<?xml version="1.0" encoding="UTF-8"?><packet version="1.6.3.5"><webspace><get><filter/></get></webspace></packet>

Reference: `Plesk API <http://download1.parallels.com/Plesk/PP11/11.0/Doc/en-US/online/plesk-api-rpc/33899.htm>`_.
The conversion is based in `Hay's project <http://github.com/hay/xml2json>`_.

Installation
------------

The following command will install pleskapi into your Python modules library:

.. code-block:: bash

    $ python setup.py install

This command will generally need to be run with an administrative level account.

Or:

.. code-block:: bash

    $ pip install pypleskapi

Pre-requisites
--------------

If you want to build ordered dict's, you MUST have python2.7+ or `OrderedDict <https://pypi.python.org/pypi/ordereddict>`_.

Overview
--------

Before starting this topic, I recommend the reading of `API RPC Manual <http://www.parallels.com/download/plesk/11/documentation/>` for
better understanding how it works.
For building dict structures that will become valid requests to Plesk API RPC, you need to understand how a dict represents an XML structure.
The conversion follow the example bellow:

.. code-block:: xml

    XML                              JSON
    <e/>                             "e": null
    <e>text</e>                      "e": "text"
    <e name="value" />               "e": { "@name": "value" }
    <e name="value">text</e>         "e": { "@name": "value", "#text": "text" }
    <e> <a>text</a ><b>text</b> </e> "e": { "a": "text", "b": "text" }
    <e> <a>text</a> <a>text</a> </e> "e": { "a": ["text", "text"] }
    <e> text <a>text</a> </e>        "e": { "#text": "text", "a": "text" }

Reference: `Converting Between XML and JSON <http://www.xml.com/pub/a/2006/05/31/converting-between-xml-and-json.html>`_.

An easy way of understanding it's using the converter functions, you can convert from an XML structure to a python dict type

.. code-block:: pycon

	>>> from pleskapi import converter as conv
	>>> xmlstr = '<?xml version="1.0" encoding="UTF-8"?><packet version="1.6.3.5"><webspace><get><filter/></get></webspace></packet>'
	>>> conv.xml2dict(xmlstr)
	{'packet': {'webspace': {'get': {'filter': None}}, '@version': '1.6.3.5'}}

Ordering Dict's
---------------

Plesk RPC API needs that the XML structure follow a specific order, more info: `API RPC Manual`_ - API RPC > API RPC Packets > How to Create Packets.

.. _`API RPC Manual`: http://www.parallels.com/download/plesk/11/documentation/

A python dict type is unordered, so you need to use an OrderedDict type for ordering only the necessary keys.
Let's consider the XML string bellow:

.. code-block:: xml

	<?xml version="1.0" encoding="UTF-8"?>
	<packet version="1.6.3.5">
	  <ip>
	    <add>
	      <ip_address>192.0.2.18</ip_address>
	      <netmask>255.255.255.0</netmask>
	      <type>shared</type>
	      <interface>eth0</interface>
	    </add>
	  </ip>
	</packet>

ip_address node must be the first, netmask the second and so on.
Building this structure without using OrderedDict, outputs to:

.. code-block:: pycon

	>>> from pleskapi import StructDict as sd

	>>> sd['ip']['add'] = {}
	>>> sd['ip']['add']['ip_address'] = '192.0.2.18'
	>>> sd['ip']['add']['netmask'] = '255.255.255.0'
	>>> sd['ip']['add']['type'] = 'shared'
	>>> sd['ip']['add']['interface'] = 'eth0'
	>>> sd.dict()
	{'ip': {'add': {'interface': 'eth0', 'type': 'shared', 'netmask': '255.255.255.0', 'ip_address': '192.0.2.18'}}}

The keys in 'add' are unordered, so the XML structure will be:

.. code-block:: xml

	<?xml version="1.0" encoding="UTF-8"?>
	<packet version="1.6.3.5">
	  <ip>
	    <add>
	      <interface>eth0</interface>
	      <type>shared</type>
	      <netmask>255.255.255.0</netmask>
	      <ip_address>192.0.2.18</ip_address>
	    </add>
	  </ip>
	</packet>

This packet will return an error because the nodes are not ordered as it should.
Ordering then are an easy task, just need to use the proper type:

.. code-block:: pycon

	>>> from pleskapi import StructDict as sd
	>>> from pleskapi import odict

	>>> sd['ip']['add'] = odict()
	>>> sd['ip']['add']['ip_address'] = '192.0.2.18'
	>>> sd['ip']['add']['netmask'] = '255.255.255.0'
	>>> sd['ip']['add']['type'] = 'shared'
	>>> sd['ip']['add']['interface'] = 'eth0'
	>>> sd.dict()
	{'ip': {'add': OrderedDict([('ip_address', '192.0.2.18'), ('netmask', '255.255.255.0'), ('type', 'shared'), ('interface', 'eth0')])}}

`More examples <https://github.com/sandromello/pypleskapi/tree/master/docs>`_

