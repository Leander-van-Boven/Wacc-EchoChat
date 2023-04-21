# Kubernetes Dashboard

## How to set up and connect in remote server

### Prerequisites
- Kubernetes cluster
- Kubectl configured for cluster
- SSH access to master node
- Kubernetes dashboard deployed:
    ```
  # Run following on master node
  GITHUB_URL=https://github.com/kubernetes/dashboard/releases
  VERSION_KUBE_DASHBOARD=$(curl -w '%{url_effective}' -I -L -s -S ${GITHUB_URL}/latest -o /dev/null | sed -e 's|.*/||')
  sudo k3s kubectl create -f https://raw.githubusercontent.com/kubernetes/dashboard/${VERSION_KUBE_DASHBOARD}/aio/deploy/recommended.yaml
  ```
- Kubernetes dashboard service account created:
  ```kubectl apply -f ./serviceaccount.yaml```
- Kubernetes dashboard clusterrolebinding:
  ```kubectl apply -f ./clusterrolebinding.yaml```

### Accessing the dashboard
#### 1. Set up proxy
Run the following command on the master node:
```
sudo k3s kubectl proxy
```

#### 2. Obtain token
Run the following command on the master node:
```
sudo k3s kubectl -n kubernetes-dashboard create token admin-user
```

#### 3. Open SSH tunnel
Run the following command on your local machine:
```
ssh -L 8001:localhost:8001 -N -f -l core 195.169.22.178 -i [PATH_TO_SSH_KEY]
```

#### 4. Open dashboard
Open the following URL in your browser:
```
http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/
```
And paste the token obtained in step 2.
