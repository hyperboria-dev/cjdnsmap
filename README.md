``` bash
git clone https://github.com/Randati/cjdnsmap
cd cjdnsmap/force-atlas
wget https://launchpad.net/gephi/toolkit/toolkit-0.8.7/+download/gephi-toolkit-0.8.7-all.zip
unzip gephi-toolkit-0.8.7-all.zip
cd ..
./compile.sh
./run.sh
```

What you need:
* Python
  * lxml
  * pygexf
  * socket
  * httplib2
* Java SDK (for prettifying the graph)
  * Gephi Toolkit
  * org.openide.util.Lookup

