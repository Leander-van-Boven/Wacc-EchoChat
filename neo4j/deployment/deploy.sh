# Add Neo4j helm repo
helm repo add neo4j https://helm.neo4j.com/neo4j
helm repo update

# Install Neo4J Core replicas
helm install --namespace echochat-databases neo4j-core-0 neo4j/neo4j-cluster-core -f ./core-values.yaml
helm install --namespace echochat-databases neo4j-core-1 neo4j/neo4j-cluster-core -f ./core-values.yaml
helm install --namespace echochat-databases neo4j-core-2 neo4j/neo4j-cluster-core -f ./core-values.yaml

helm install --namespace echochat-databases neo4j-headless neo4j/neo4j-cluster-headless-service --set neo4j.name=echochat-neo4j-cluster

# TODO: Install Neo4J Read replicas
# (and figure out if we need them)
