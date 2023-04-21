# The actual Virtual Machine instance running Flatcar
resource "openstack_compute_instance_v2" "flatcar_master" {
    name = "Flatcar Master"
    image_id = openstack_images_image_v2.flatcar.id
    flavor_name = var.master_flavor_name
    security_groups = ["default", openstack_networking_secgroup_v2.basic.name]
    
    user_data = data.ct_config.flatcar_master.rendered

    network {
        uuid = openstack_networking_network_v2.internal.id
        fixed_ip_v4 = var.master_ip
    }
}

resource "openstack_compute_instance_v2" "flatcar_slave" {
    count = 2
    name = "Flatcar Slave ${count.index}"
    image_id = openstack_images_image_v2.flatcar.id
    flavor_name = var.slave_flavor_name
    security_groups = ["default", openstack_networking_secgroup_v2.basic.name]
    
    user_data = data.ct_config.flatcar_slave[count.index].rendered

    network {
        uuid = openstack_networking_network_v2.internal.id
    }
}

resource "null_resource" "tls_master" {
    triggers = {
        master_id = openstack_compute_instance_v2.flatcar_master.id
    }

    depends_on = [
        openstack_compute_instance_v2.flatcar_master
    ]

    connection {
        type = "ssh"
        user = "core"
        host = openstack_networking_floatingip_v2.float_ip.address
        private_key = file("${path.module}/id_rsa")
        timeout = "5m"
    }

    provisioner "remote-exec" {
        # Update Kubeconfig certificate to accept connections on public ip
        inline = [
            "until [ -f /etc/rancher/k3s/k3s.yaml ]; do echo 'Waiting for k3s.yaml to be created'; sleep 1; done",
            "curl -vk --resolve ${openstack_networking_floatingip_v2.float_ip.address}:6443:${openstack_compute_instance_v2.flatcar_master.access_ip_v4}  https://${openstack_networking_floatingip_v2.float_ip.address}:6443/ping"
        ]
    }
}
