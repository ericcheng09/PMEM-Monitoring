# PMEM-Monitoring
This project describes how to setup a PMEM monitoring system and contains the scripts and configuration files that used to setup and collect metrics. 

## InfluxDB Setup
**Do following at master machine**
```
wget -qO- https://repos.influxdata.com/influxdb.key | sudo apt-key add -
source /etc/lsb-release
echo "deb https://repos.influxdata.com/${DISTRIB_ID,,} ${DISTRIB_CODENAME} stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
```

```
sudo apt-get update && sudo apt-get install influxdb
sudo service influxdb start
```
**Create user:**
```
CREATE USER ‘<username>’ WITH PASSWORD ‘<password>’ WITH ALL PRIVILEGES
```
**Create databases:**
```
CREATE DATABASE “telegraf” (Data from host machines)
CREATE DATABASE “k8s_demo” (Data from kuberenetes cluster)
```
## Grafana Setup
**Do following at master machine**
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

Open browser, go to  &lt;grafana host machine ip&gt;:3000 (3000 is default port of grafana service).

**Add Datasource:**<br>Configure Datasource URL: &lt;IP of influxDB’s host machine&gt;:8086

![datasource 1](/Grafana/datasource1.jpg)<br>
![datasource 2](/Grafana/datasource2.jpg)

**To import existed dashboard:**<br>Create new dashboards, go to Dashboard settings/JSON Model. Overwrite the content with the JSON files in ./Grafana/ModelJSON.

![Model JSON](/Grafana/ModeJSON.jpg)


## Telegraf Setup
**Do following at all nodes.**
```
wget -qO- https://repos.influxdata.com/influxdb.key | sudo apt-key add –
source /etc/lsb-release
echo "deb https://repos.influxdata.com/${DISTRIB_ID,,} ${DISTRIB_CODENAME} stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
sudo apt-get update && sudo apt-get install telegraf
sudo service telegraf starts
```

**Note:** Telegraf will use the configuration file at default location(/etc/telegraf/telegraf.conf). 

**Specify the config for telegraf:**
```
telegraf --config path/to/file.conf
```

**To generate a template config file:**
```
telegraf config > telegraf.conf
```

**Configure output location in the config file:**
```
....
[[outputs.influxdb]]
  .....
  urls = ["http://<influxDB's IP>:8086"]

  database = "database"
  ....
  ## HTTP Basic Auth
  username = "username"
  password = "password"
  ...
```

**To use configured config file:**<br>
Copy and paste the /telegraf/telegraf.config to /etc/telegraf.

**Note:**<br> One of telegraf plugins needs permission to access docker socket, you can either:<br>
1. Run telegraf as root
```
sudo telegraf ...
```
It's not recommended to run telegraf as root.<br>
2. Add telegraf to docker group (Recommand)
```
sudo usermod -aG docker telegraf
(Logout and Login)
Sudo service docker restart
```

**Collect non-supported/custom metics:**<br>
There are some custom metrics we want to collect using our scripts(in /telegraf/scripts folder), so we need to utilize the exec plugin.<br>**Add these commands in exec plugin section in telegraf config file:**
```
commands = [
    "sudo python3 /path/to/pmem_py3.py",
    "sudo python3 /path/to/docker_status.py",
    "sudo python3 /path/to/vm_status.py"
  ]
```
**Note:**You may need to install necessary packages. You also need to allow telegraf to execute command with "sudo", you can do that by:
```
visudo

(@sudoers file)
Add:
    telegraf  ALL=(ALL) NOPASSWD: ALL
```

## Kubernetes and PMEM-CSI Setup
For Kubernetes installation and PMEM-CSI setup, refer to [readme](https://github.com/ericcheng09/PMEM-Monitoring/blob/master/kubernetes/README.md) in /kubernetes.


## Telegraf Setup in Kubernetes
Since k8s uses Role-Based Access Control(RBAC), so we need to create required resources first. All permissions related resources have been configured. Simply:
```
kubectl create -f /telegraf/kubernetes/roles.yaml
```
Then, you can create pods to monitor resources in k8s cluster:
```
kubectl create -f /telegraf/kubernetes/Cluster
```
Or, k8s pods on each node:
```
kubectl create -f /telegraf/kubernetes/Daemonset
```
<span style="color:red">**Note:**</span>  Please modify telegraf-secrets.yaml file with your configurations, so that telegraf can connect to your database correctly. You can also modify config files to configure the telegraf.

You can find descriptions about telegraf plugins [here](https://github.com/influxdata/telegraf).

## Reference
* https://docs.influxdata.com/influxdb/v1.8/introduction/install/
* https://grafana.com/docs/grafana/latest/installation/debian/
* https://docs.influxdata.com/telegraf/v1.13/introduction/installation/
* https://github.com/influxdata/telegraf