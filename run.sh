#!/usr/bin/env bash

WEBSITE_DIR=website


python gexf_output.py network.gexf

cd force-atlas
java -cp /usr/share/java/org-openide-util-lookup.jar:.:gephi-toolkit-0.8.7-all/gephi-toolkit.jar Atlas ../network.gexf ../network-processed.gexf
cd ..


mv network-processed.gexf $WEBSITE_DIR/network-processed.gexf.xml
echo $(date +"%s") > $WEBSITE_DIR/update-time

rm network.gexf
