# Converting the user-readable Container Linux Configuration in flatcar_config.yaml
# into a machine-readable Ignition config file using the "Config Transpiler" ct.
#
# Also performs some template magic on this file to import the ssh keys to use.
data "ct_config" "flatcar_master" {
    strict = true
    pretty_print = false
    platform = "openstack-metadata"

    # Render the template in the given file
    content = templatefile("${path.module}/flatcar_master_config.yaml", {
        # Use these values to fill the template
        sshkey = file("${path.module}/id_rsa.pub")
        k3s_token = var.k3s_token
        hostname = "flatcar-master"
        master_host = var.master_ip
    })
}

data "ct_config" "flatcar_slave" {
    count = 2
    strict = true
    pretty_print = false
    platform = "openstack-metadata"

    # Render the template in the given file
    content = templatefile("${path.module}/flatcar_slave_config.yaml", {
        # Use these values to fill the template
        sshkey = file("${path.module}/id_rsa.pub")
        k3s_token = var.k3s_token
        hostname = "flatcar-slave-${count.index}"
        master_host = openstack_compute_instance_v2.flatcar_master.access_ip_v4
    })
}
