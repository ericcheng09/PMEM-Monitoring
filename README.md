# PMEM-Monitoring


## InfluxDB Setup:
At Master Machine
https://docs.influxdata.com/influxdb/v1.8/introduction/install/
```
wget -qO- https://repos.influxdata.com/influxdb.key | sudo apt-key add -
source /etc/lsb-release
echo "deb https://repos.influxdata.com/${DISTRIB_ID,,} ${DISTRIB_CODENAME} stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
```


```
sudo apt-get update && sudo apt-get install influxdb
sudo service influxdb start
```
create user:
```
CREATE USER ‘telegraf’ WITH PASSWORD ‘telegraf’ WITH ALL PRIVILEGES
```

Create databases:
```
CREATE DATABASE “telegraf”   (Data from host machines)
```
or
```
CREATE DATABASE “k8s_demo” (Data from kuberenetes cluster)
```
## Grafana Setup:
At Master Machine
```
https://grafana.com/docs/grafana/latest/installation/debian/
sudo apt-get install -y apt-transport-https
sudo apt-get install -y software-properties-common wget 
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -

sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"

sudo apt-get update
sudo apt-get install grafana

sudo systemctl daemon-reload
sudo systemctl start grafana-server
sudo systemctl status grafana-server
```
At browser, go to <grafana host machine ip>:3000 (3000 is default port of grafana service)

Configure Datasource:
URL: &lt;IP of influxDB’s host machine&gt;:8086
![datasource 1](/Grafana/datasource1.jpg)

