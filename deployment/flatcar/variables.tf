# OpenStack auth settings
variable "openstack_url" {
    type = string
    description = "OpenStack Auth URL"
}

variable "openstack_domainid" {
    type = string
    description = "OpenStack Domain ID"
    default = null
}

variable "openstack_domainname" {
    type = string
    description = "OpenStack Domain Name"
    default = null
}

variable "openstack_username" {
    type = string
    description = "OpenStack username"
    sensitive = true
}

variable "openstack_password" {
    type = string
    description = "OpenStack password"
    sensitive = true
}

variable "openstack_projectid" {
    type = string
    description = "OpenStack Project ID"
    sensitive = true
}

variable "openstack_region" {
    type = string
    description = "OpenStack Region"
    default = ""
}

# Other environment settings
variable "master_flavor_name" {
    type = string
    description = "Flavor to use for the master instance"
}

variable "slave_flavor_name" {
    type = string
    description = "Flavor to use for the slave instance"
}

variable "public_network" {
    type = string
    description = "Name of the public network to connect to"
}

variable "master_ip" {
    type = string
    description = "IP address to assign to the master instance"
}

variable "k3s_token" {
    type = string
    description = "K3s token to use for the cluster"
    sensitive = true
}
