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
**Note:**The token will expire after 24 hours 

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


## Reference
* https://vitux.com/install-and-deploy-kubernetes-on-ubuntu/
* https://blog.csdn.net/mailjoin/article/details/79686934
* https://kubernetes.io/docs/reference/setup-tools/kubeadm/kubeadm-join/#token-based-discovery-with-ca-pinning