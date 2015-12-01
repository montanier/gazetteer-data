#!/usr/bin/python

# Copyright (c) 2015
# Jean-Marc Montanier
# COMPUTER APPLICATIONS IN SCIENCE & ENGINEERING
# BARCELONA SUPERCOMPUTING CENTRE - CENTRO NACIONAL DE SUPERCOMPUTACION
# http://www.bsc.es
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version. 
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public 
# License along with this library.  If not, see <http://www.gnu.org/licenses/>.

from rdflib import Graph
import json
from BeautifulSoup import BeautifulSoup
import requests
import re
import pprint
from rdflib import URIRef
import sys

if not len(sys.argv) == 3:
    print "Use of the script: ./rdfToGeoJSON.py inputFile outputFile"
    exit()

g = Graph().parse(sys.argv[1], format='n3')

output = open(sys.argv[2],"w")
output.write("""{ 
"type": "FeatureCollection",
"crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } }, 

"features": [
""")

previous = False
for s,p,o in g.triples( (None,URIRef(u'http://www.opengis.net/ont/geosparql#hasGeometry'),None)):
    geo = json.loads(g.value(o,URIRef(u'http://data.ordnancesurvey.co.uk/ontology/geometry/asGeoJSON')))

    page = requests.get(str(s))
    parsed_html = BeautifulSoup(page.text)
    pattern = re.compile("<title>(.*) &mdash;.*<\/title>")
    match = pattern.match(str(parsed_html.title))

    if match:
        provinceName = match.group(1)

        geoType = geo["type"]
        geoCoord = geo["coordinates"]

        if previous == False:
            output.write('{ "type": "Feature",')
            previous = True
        else:
            output.write(',{ "type": "Feature",')

        output.write('"properties" : { "name" : "' + provinceName + '" },')
        output.write('"geometry" : { "type": "' + str(geo["type"] + '", "coordinates": ' + str(geoCoord)) + '}}')
        output.write('\n')

    else:
        print("Something failed when treating " + str(s))
        exit()


output.write('] }')
output.close()
