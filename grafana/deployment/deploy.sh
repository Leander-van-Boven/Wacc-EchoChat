# USING HELM
# get Grafana helm charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# install Loki
helm upgrade --install loki grafana/loki-simple-scalable \
  --namespace echochat-monitoring \
  --set loki.auth_enabled=false

# install Promtail
helm upgrade --install promtail grafana/promtail \
  --namespace echochat-monitoring \
  --set loki.serviceName=loki-gateway

# install Grafana
helm upgrade --install grafana grafana/grafana \
  --namespace echochat-monitoring \
  --set persistence.enabled=true \
  --set persistence.size=5Gi \
  --set persistence.storageClassName=local-path \
  --set adminPassword=grafana

# install Tempo
helm upgrade --install tempo grafana/tempo \
  --namespace echochat-monitoring

# DEPRECATED: using yaml files instead
# kubectl apply -f ./service.yaml
# kubectl apply -f ./deployment.yaml

# Open Grafana dashboard:
# $(kubectl get pods --namespace echochat-monitoring -l "app.kubernetes.io/name=grafana,app.kubernetes.io/instance=grafana" -o jsonpath="{.items[0].metadata.name}")
# kubectl port-forward --namespace echochat-monitoring service/grafana 3000:3000
