#!/usr/bin/env python
#
# original - cjdnsmap.py (c) 2012 Gerard Krol
# modified - cjdnsmap.py - 2014 Randati
#
# You may redistribute this program and/or modify it under the terms of
# the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from cjdns import cjdns_connect, cjdns_connectWithAdminInfo
import httplib2
import json


class Route:
    def __init__(self, ip, link, path, version):
        self.ip = ip
        self.link = link
        self.path = path
        self.version = version

        route = path
        route = route.replace('.','')
        route = route.replace('0','x')
        route = route.replace('1','y')
        route = route.replace('f','1111')
        route = route.replace('e','1110')
        route = route.replace('d','1101')
        route = route.replace('c','1100')
        route = route.replace('b','1011')
        route = route.replace('a','1010')
        route = route.replace('9','1001')
        route = route.replace('8','1000')
        route = route.replace('7','0111')
        route = route.replace('6','0110')
        route = route.replace('5','0101')
        route = route.replace('4','0100')
        route = route.replace('3','0011')
        route = route.replace('2','0010')
        route = route.replace('y','0001')
        route = route.replace('x','0000')
        self.route = route[::-1].rstrip('0')[:-1]
        self.quality = link / 5366870.0 # LINK_STATE_MULTIPLIER

    def find_parent(self, routes):
        def is_parent(other):
            return self.route.startswith(other.route) and self != other

        parents = filter(is_parent, routes)
        if not parents: return None

        return max(parents, key=lambda r: len(r.route))


    def __repr__ (self):
        return "%s(%r)" % (self.__class__, self.__dict__)



class Node:
    def __init__(self, route):
        self.ip = route.ip
        self.version = int(route.version)
        self.name = self.ip.split(':')[-1]

        self.connections = 0
        self.active_connections = 0

    def __repr__ (self):
        return "%s(%r)" % (self.__class__, self.__dict__)

class Edge:
    def __init__(self, parent_node, node, quality):
        self.parent_node = parent_node
        self.node = node
        self.quality = quality

    def __repr__ (self):
        return "%s(%r)" % (self.__class__, self.__dict__)




def get_routes(cjdns):
    routes = []
    i = 0

    while True:
        table = cjdns.NodeStore_dumpTable(i)

        for r in table['routingTable']:
            route = Route(r['ip'], r['link'], r['path'], r['version'])
            routes.append(route)

        if not 'more' in table:
            break

        i += 1
    return routes

def sort_routes_on_quality(routes):
    tmp = [(r.quality,r) for r in routes]
    tmp.sort(reverse=True)
    return [q[1] for q in tmp]


def get_nodes(routes):
    nodes = {}
    for r in routes:
        if not r.ip in nodes:
            nodes[r.ip] = Node(r)
    return nodes


def get_edges(routes, nodes):
    link_strengths = {}

    def is_linked(a, b):
        a, b = sorted([a, b])
        return (a, b) in link_strengths

    def set_link_strength(a, b, strength):
        a, b = sorted([a, b])
        if not is_linked(a, b):
            link_strengths[(a, b)] = strength
        else:
            old_strength = link_strengths[(a, b)]
            if strength > old_strength:
                link_strengths[(a, b)] = strength

    edges = []

    for r in routes:
        parent = r.find_parent(routes)
        if not parent: continue

        parent_node = nodes[parent.ip]
        node = nodes[r.ip]

        if not is_linked(parent_node, node):
            parent_node.connections += 1
            node.connections += 1

            if r.quality > 0:
                parent_node.active_connections += 1
                node.active_connections += 1

            edges.append(Edge(parent_node, node, r.quality))

        set_link_strength(parent_node, node, r.quality)

    return edges




def download_node_names():
    print "Downloading names"
    page = 'http://[fc5d:baa5:61fc:6ffd:9554:67f0:e290:7535]/nodes/list.json'

    names = {}
    h = httplib2.Http(".cache")
    try:
        r, content = h.request(page, "GET")
        nameip = json.loads(content)['nodes']
    except:
        print "Connection to Mikey's nodelist failed, continuing without names"
        nameip = {}

    return nameip

def update_names(node_names, nodes):
    for nameip in node_names:
        if nameip['ip'] in nodes:
            nodes[nameip['ip']].name = nameip['name'] 


def get_map():
    try:
        cjdns = cjdns_connect(cjdadmin_ip, cjdadmin_port, cjdadmin_pass)
    except:
        cjdns = cjdns_connectWithAdminInfo()
    
    routes = get_routes(cjdns)
    routes = sort_routes_on_quality(routes)
    nodes = get_nodes(routes)
    edges = get_edges(routes, nodes)

    node_names = download_node_names()
    update_names(node_names, nodes)

    return nodes.values(), edges
