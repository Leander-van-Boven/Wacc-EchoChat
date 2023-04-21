kubectl apply -f ./service.yaml
kubectl apply -f ./statefulset.yaml

helm repo add elastic https://helm.elastic.co
helm repo update

helm upgrade --install kibana elastic/kibana \
    --namespace echochat-databases \
    -f kibana_values.yaml
