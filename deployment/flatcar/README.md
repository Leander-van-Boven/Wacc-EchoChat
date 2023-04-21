# Terraform provisioning

This folder contains the files necessary to deploy a virtual machine running Flatcar with K3S on OpenStack on the Merlin HPC with a basic network configuration.

- Run `init.sh` to initialise your local copy of the repository.
- Update the secrets file to include your credentials
- Run `terraform init`
- Run `terraform plan -var-file=merlin.tfvars.json`
- Run `terraform apply`
- Output contains the IP of the master node
