from gexf import Gexf
import cjdnsmap
import sys

if len(sys.argv) != 2:
	print "usage: " + sys.argv[0] + " output.gexf"
	sys.exit()

output_filename = sys.argv[1]


nodes, edges = cjdnsmap.get_map()

gexf = Gexf("cjdns mapper", "A map of cjdns network")
graph = gexf.addGraph("undirected", "static", "cjdns network graph")

attr_ip                 = graph.addNodeAttribute("IP",                 type="string")
attr_version            = graph.addNodeAttribute("Version",            type="integer")
attr_connections        = graph.addNodeAttribute("Connections",        type="integer")
attr_active_connections = graph.addNodeAttribute("Active connections", type="integer")

attr_quality            = graph.addEdgeAttribute("Quality", 0,         type="float")


for node in nodes:
	n = graph.addNode(node.ip, node.name)
	n.addAttribute(attr_ip, node.ip)
	n.addAttribute(attr_version, str(node.version))
	n.addAttribute(attr_connections, str(node.connections))
	n.addAttribute(attr_active_connections, str(node.active_connections))

for edge in edges:
	name = edge.parent_node.ip + "-" + edge.node.ip
	e = graph.addEdge(name, edge.parent_node.ip, edge.node.ip, label=str(edge.quality))
	e.addAttribute(attr_quality, str(edge.quality))

output_file = open(output_filename, "w")
gexf.write(output_file)
output_file.close()
