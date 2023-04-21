# Outputs to show when done provisioning
output "flatcar_ip" {
    value = openstack_networking_floatingip_v2.float_ip.address
    description = "IP Address to reach the VM on"
}

# Save the public IP, i.e. the IP of the master node, to a file, so it may be used by the CI/CD pipeline
resource "local_file" "master_ip" {
    content = openstack_networking_floatingip_v2.float_ip.address
    filename = "${path.module}/master_ip.txt"
}
