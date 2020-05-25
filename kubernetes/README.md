# Install Kubernetes

## Docker
**At all nodes**
```
sudo apt install docker.io
sudo systemctl enable docker
```

## Kubernetes
**At all nodes**
```
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add
sudo apt-add-repository "deb http://apt.kubernetes.io/ kubernetes-xenial main"
sudo apt install kubeadm
```

**Disable swap memory:**
```
sudo swapoff –a   
```

**Set unique hostname for each machine:**
```
hostnamectl set-hostname <hostname> 
```


**Initialize the master node:**<br> This command will output information for joining machine, please note down the output.
```
sudo kubeadm init --pod-network-cidr=10.244.0.0/16 
```

**Run following as regular user:**
```
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

**To join machine:**
```
kubeadm join <Master Node IP>:6443 --token <Token> --discovery-token-ca-cert-hash sha256:<CA sha256> 
```
You can get this command during the initialization of master node.

**Example:**
```
sudo kubeadm join 140.92.152.61:6443 --token wkry3m.fn4umk0u9ugmlfxz  \
    --discovery-token-ca-cert-hash sha256:2ae3a437401e230bfbe2b0022baa199fea03e39002f7c4f5f515a1c70f05b353
```
**Note:** The token will expire after 24 hours 

**To generate new token:**
```
# At Master Node
kubeadm token create (--ttl 0)  # --ttl 0 will create non-expire token
```
 
**To get CA SHA256:**
```
# At Master Node
openssl x509 -pubkey -in /etc/kubernetes/pki/ca.crt | openssl rsa -pubin -outform der 2>/dev/null | openssl dgst -sha256 -hex | sed 's/^.* //'
```


**To check Nodes in kubernetes cluster:**
```
Kubectl get nodes # At Master Node
```

**Deploy a Pod Network:**
```
sudo kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
```

## Deploy pmem-csi
```
(At Master)
git clone https://github.com/intel/pmem-csi
kubectl label node <node with pmem> storage=pmem

cd pmem-csi
curl -L https://pkg.cfssl.org/R1.2/cfssl_linux-amd64 -o _work/bin/cfssl --create-dirs
curl -L https://pkg.cfssl.org/R1.2/cfssljson_linux-amd64 -o _work/bin/cfssljson --create-dirs
chmod a+x _work/bin/cfssl _work/bin/cfssljson

export KUBCONFIG="/path/to/.kube/config"
export PATH="$PATH:$PWD/_work/bin" 
./test/setup-ca-kubernetes.sh

kubectl create -f deploy/kubernetes-1.17/pmem-csi-direct.yaml
or 
kubectl create -f deploy/kubernetes-1.17/pmem-csi-lvm.yaml
```

*When using LVM mode, csi will pre-create namespace and the amount of space to be used is determined by an argument: -useforfsdax=100 which means 100%(default) of PMEM will be used. To configure, add the argument in the pmem-csi-lvm.yaml file and set the value (0-100).
```
(In pmem-csi-lvm.yaml)
apiVersion: apps/v1
kind: DaemonSet
metadata:
  labels:
    pmem-csi.intel.com/deployment: lvm-production
  name: pmem-csi-node
  namespace: default
spec:
  selector:
    matchLabels:
      app: pmem-csi-node
      pmem-csi.intel.com/deployment: lvm-production
  template:
   ...
initContainers:
      - command:
        - /usr/local/bin/pmem-ns-init
        - -usefordax=50  <- add this line to determine the percentage
        - -v=3
        env:
        - name: TERMINATION_LOG_PATH
          value: /tmp/pmem-ns-init-termination-log
        image: intel/pmem-csi-driver:canary
        imagePullPolicy: Always
        name: pmem-ns-init
    ...
```

After the creation of pvc, if pvcs show “Pending” statu. Try to reduce the size in the pvc configuration files. ([Issue](https://github.com/intel/pmem-csi/issues/107))



```
kubectl get nodes --show-labels
*check whether the node with pmem is labeled:
pmem-csi.intel.com/node=<NODE-NAME>,storage=pmem
```
Create storage classes and pvc, then create pods to use volume.
```
kubectl create -f deploy/kubernetes-1.17/pmem-storageclass-ext4.yaml
kubectl create -f deploy/ kubernetes-1.17/pmem-storageclass-xfs.yaml
kubectl create -f deploy/kubernetes-1.17/pmem-pvc.yaml

kubectl create –f deploy/kubernetes-1.17/pmem-app.yaml
```

## Reference
* https://vitux.com/install-and-deploy-kubernetes-on-ubuntu/
* https://blog.csdn.net/mailjoin/article/details/79686934
* https://kubernetes.io/docs/reference/setup-tools/kubeadm/kubeadm-join/#token-based-discovery-with-ca-pinning
* https://github.com/intel/pmem-csi