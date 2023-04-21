# Add Prometheus helm charts
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# install Prometheus
helm upgrade --install prometheus prometheus-community/prometheus \
  --namespace echochat-monitoring \
  --set alertmanager.enabled=false \
  --set server.persistentVolume.storageClass=local-path
