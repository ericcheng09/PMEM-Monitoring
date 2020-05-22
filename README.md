# PMEM-Monitoring


## InfluxDB Setup
Do following at master machine.
```
wget -qO- https://repos.influxdata.com/influxdb.key | sudo apt-key add -
source /etc/lsb-release
echo "deb https://repos.influxdata.com/${DISTRIB_ID,,} ${DISTRIB_CODENAME} stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
```


```
sudo apt-get update && sudo apt-get install influxdb
sudo service influxdb start
```
Create user:
```
CREATE USER ‘telegraf’ WITH PASSWORD ‘telegraf’ WITH ALL PRIVILEGES
```
Create databases:
```
CREATE DATABASE “telegraf” (Data from host machines)
CREATE DATABASE “k8s_demo” (Data from kuberenetes cluster)
```
## Grafana Setup
Do following at master machine.
```
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

Configure Datasource
URL: &lt;IP of influxDB’s host machine&gt;:8086

![datasource 1](/Grafana/datasource1.jpg)

![datasource 2](/Grafana/datasource2.jpg)

Create New Dashboards, go to Dashboard settings/JSON Model. Overwrite the content with the JSON files under ./Grafana/ModelJSON.

![Model JSON](/Grafana/ModeJSON.jpg)


## Telegraf Setup

```
wget -qO- https://repos.influxdata.com/influxdb.key | sudo apt-key add –
source /etc/lsb-release
echo "deb https://repos.influxdata.com/${DISTRIB_ID,,} ${DISTRIB_CODENAME} stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
sudo apt-get update && sudo apt-get install telegraf
sudo service telegraf starts
```



## Kubernetes Setup


## Reference
* https://docs.influxdata.com/influxdb/v1.8/introduction/install/
* https://grafana.com/docs/grafana/latest/installation/debian/
* https://docs.influxdata.com/telegraf/v1.13/introduction/installation/