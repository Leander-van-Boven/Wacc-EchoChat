# Add redis helm repo
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install redis
helm install --namespace echochat-databases redis bitnami/redis

# export REDIS_PASSWORD=$(kubectl get secret --namespace echochat-databases redis -o jsonpath="{.data.redis-password}" | base64 -d)
