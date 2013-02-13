"""
Relies on ElementTree for the XML parsing.  This is based on
pesterfish.py but uses a different XML->JSON mapping.
The XML->JSON mapping is described at
http://www.xml.com/pub/a/2006/05/31/converting-between-xml-and-json.html

Rewritten to a command line utility by Hay Kranen < github.com/hay >

XML                              JSON
<e/>                             "e": null
<e>text</e>                      "e": "text"
<e name="value" />               "e": { "@name": "value" }
<e name="value">text</e>         "e": { "@name": "value", "#text": "text" }
<e> <a>text</a ><b>text</b> </e> "e": { "a": "text", "b": "text" }
<e> <a>text</a> <a>text</a> </e> "e": { "a": ["text", "text"] }
<e> text <a>text</a> </e>        "e": { "#text": "text", "a": "text" }

This is a mess in that it is so unpredictable -- it requires lots of testing
(e.g. to see if values are lists or strings or dictionaries).  For use
in Python this could be vastly cleaner.  Think about whether the internal
form can be more self-consistent while maintaining good external characteristics
for the JSON.
"""

import xml.etree.cElementTree as ET
from xml.etree import ElementTree
from xml.dom import minidom

try: import simplejson
except ImportError: import json as simplejson

try: from collections import OrderedDict as odict
except ImportError:
    try: import OrderedDict as odict
    except ImportError: odict = dict

def elem_to_internal(elem, strip=1):
    """ Convert an Element into an internal dictionary (not JSON!). """
    d = dict()
    for key, value in elem.attrib.items():
        d['@'+key] = value

    # loop over subelements to merge them
    for subelem in elem:
        v = elem_to_internal(subelem, strip)
        tag = subelem.tag
        value = v[tag]
        try:
            # add to existing list for this tag
            d[tag].append(value)
        except AttributeError:
            # turn existing entry into a list
            d[tag] = [d[tag], value]
        except KeyError:
            d[tag] = value

    text = elem.text
    tail = elem.tail

    if strip:
        # ignore leading and trailing whitespace
        if text: text = text.strip()
        if tail: tail = tail.strip()

    if tail:
        d['#tail'] = tail

    if d:
        # use #text element if other attributes exist
        if text: d["#text"] = text
    else:
        # text is the value if no attributes
        d = text or None

    return {elem.tag: d}

def internal_to_elem(pfsh, dictype):
    """ Convert an internal dictionary (not JSON!) into an Element.
    """
    attribs = dictype()
    text = None
    tail = None
    sublist = []
    tag = pfsh.keys()
    if len(tag) != 1:
        raise ValueError("Illegal structure with multiple tags: %s" % tag)
    tag = tag[0]
    value = pfsh[tag]
    if isinstance(value,dict):
        for k, v in value.items():
            if k[:1] == "@":
                attribs[k[1:]] = v
            elif k == "#text":
                text = v
            elif k == "#tail":
                tail = v
            elif isinstance(v, list):
                for v2 in v:
                    sublist.append(internal_to_elem({k:v2}, dictype))
            else:
                sublist.append(internal_to_elem({k:v}, dictype))
    else:
        text = value
    e = ET.Element(tag, attribs)
    for sub in sublist:
        e.append(sub)
    e.text = text
    e.tail = tail
    return e

def elem2dict(elem, strip=1):
    """ Convert an ElementTree or Element into a JSON string."""
    if hasattr(elem, 'getroot'):
        elem = elem.getroot()
    return elem_to_internal(elem, strip=strip)

def xml2elem(xmlstr, strip=1):
    return ET.fromstring(xmlstr)

def xml2json(xmlstring, strip=1):
    """ Convert an XML string into a JSON string.
    :param xmlstring: The specified xml string to convert into a json string
    :param strip: Ignore leading and trailing whitespace. Default: 1 (ignore)
    """
    elem = ET.fromstring(xmlstring)
    return simplejson.dumps(elem2dict(elem, strip=strip))

def xml2dict(xmlstring, strip=1):
    """ Convert an XML string into a dictionary.
    :param xmlstring: The specified xml string to convert into a dict
    :param strip: Ignore leading and trailing whitespace. Default: 1 (ignore)
    """
    elem = ET.fromstring(xmlstring)
    return elem2dict(elem, strip=strip)

def dict2xml(adict, dictype=odict):
    """ Convert a dict to an xml string with headers.
    :param adict: The specified dictonary to convert into an xml
    :param dictype: The type of the dictionary which will be used to construct the xml string (dict or OrderedDict). Default: OrderedDict (odict) 
    """
    elem = internal_to_elem(adict, dictype)
    elem = minidom.parseString(ElementTree.tostring(elem, encoding='UTF-8'))
    return elem.toprettyxml(indent='', encoding='UTF-8').replace('\n', '')

def elem2xml(elem):
    elem = minidom.parseString(ElementTree.tostring(elem, encoding='UTF-8'))
    return elem.toprettyxml(indent='', encoding='UTF-8').replace('\n', '')