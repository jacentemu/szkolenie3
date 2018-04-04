# https://docs.microsoft.com/en-us/azure/virtual-machines/linux/ansible-create-complete-vm
#
# az group create --name azu-eu-west --location westeurope

- name: Create Azure VM
  hosts: localhost
  connection: local
  vars:
    eco_azure:
        name: azu-eu-west-ECO
        location: westeurope
        vnet: 
            ip: 172.16.132.0/24
            name: azu-eu-west-eco-vnet
        subnet: 
            ip: 172.16.132.0/24
            name: azu-eu-west-eco-subnet-a
        sg:
            name: azu-eu-west-eco-sg
        sg_tunnel:
            name: azu-eu-west-eco-sg-tunnel
#        vm_tunnel: 
#            - name: azu-eu-west-eco-tunnel-131
#              network_interface:
#                  name: azu-eu-west-subnet-a-ni-tunel
#              vm_size: Standard_DS1_v2
#              username: ubuntu
#              data_disks:
#                  - lun: 0
#                    disk_size_gb: 64
#
        vm:
            - name: azu-eu-west-eco-vpn-132
              network_interface:
                  name: azu-eu-west-eco-subnet-a-ni-vpn
              vm_size: Standard_DS1_v2
              username: ubuntu
              data_disks:
                  - lun: 0
                    disk_size_gb: 64
                    managed_disk_type: Premium_LRS
              managed_disk_type: Premium_LRS
              ip_pub_name: azu-eu-west-eco-vpn-132-pubIP

            - name: azu-compute-eco-102
              network_interface:
                  name: azu-eu-west-eco-subnet-a-ni-ve102it
              vm_size: Standard_DS1_v2
              username: ubuntu
              managed_disk_type: Premium_LRS
              ip_pub_name: azu-eu-west-eco-vpn-102-pubIP
              data_disks:
                  - lun: 0
                    disk_size_gb: 255
                    managed_disk_type: Premium_LRS
                  - lun: 1
                    disk_size_gb: 255
                    managed_disk_type: Premium_LRS
                  - lun: 2
                    disk_size_gb: 255
                    managed_disk_type: Premium_LRS
                  - lun: 3
                    disk_size_gb: 255
                    managed_disk_type: Premium_LRS
##                  - lun: 4
##                    disk_size_gb: 255
##                    managed_disk_type: Premium_LRS
##                  - lun: 5
##                    disk_size_gb: 255
##                    managed_disk_type: Premium_LRS
#            - name: azu-ve105
#              network_interface:
#                  name: azu-eu-west-subnet-a-ni-ve105
#              vm_size: Standard_DS1_v2
#              username: ubuntu
#              managed_disk_type: Premium_LRS
#              data_disks:
#                  - lun: 0
#                    disk_size_gb: 255
#                    managed_disk_type: Premium_LRS
#                  - lun: 1
#                    disk_size_gb: 255
#                    managed_disk_type: Premium_LRS
#                  - lun: 2
#                    disk_size_gb: 255
#                    managed_disk_type: Premium_LRS
#                  - lun: 3
#                    disk_size_gb: 255
#                    managed_disk_type: Premium_LRS
##                  - lun: 4
##                    disk_size_gb: 255
##                    managed_disk_type: Premium_LRS
##                  - lun: 5
##                    disk_size_gb: 255
##                    managed_disk_type: Premium_LRS
#            - name: azu-ve106
#              network_interface:
#                  name: azu-eu-west-subnet-a-ni-ve106
#              vm_size: Standard_DS1_v2
#              username: ubuntu
#              managed_disk_type: Premium_LRS
#              data_disks:
#                  - lun: 0
#                    disk_size_gb: 255
#                    managed_disk_type: Premium_LRS
#                  - lun: 1
#                    disk_size_gb: 255
#                    managed_disk_type: Premium_LRS
#                  - lun: 2
#                    disk_size_gb: 255
#                    managed_disk_type: Premium_LRS
#                  - lun: 3
#                    disk_size_gb: 255
#                    managed_disk_type: Premium_LRS
##                  - lun: 4
##                    disk_size_gb: 255
##                    managed_disk_type: Premium_LRS
##                  - lun: 5
##                    disk_size_gb: 255
##                    managed_disk_type: Premium_LRS

  tasks:
  - name: Create virtual network
    azure_rm_virtualnetwork:
      resource_group: "{{ eco_azure.name }}"
      name: "{{ eco_azure.vnet.name }}"
      address_prefixes: "{{ eco_azure.vnet.ip }}"

  - name: Add subnet
    azure_rm_subnet:
      resource_group: "{{ eco_azure.name }}"
      name: "{{ eco_azure.subnet.name }}"
      address_prefix: "{{ eco_azure.subnet.ip }}"
      virtual_network: "{{ eco_azure.vnet.name }}"

  - name: Create Network Security Group that allows SSH
    azure_rm_securitygroup:
      resource_group: "{{ eco_azure.name }}"
      name: "{{ eco_azure.sg.name }}"
      rules:
        - name: SSH
          protocol: Tcp
          destination_port_range: 22
          access: Allow
          priority: 1001
          direction: Inbound
        - name: vpn
          protocol: Udp
          destination_port_range: 1194
          access: Allow
          priority: 1002
          direction: Inbound

#  - name: Create Network Security Group that allows SSH - tunnel
#    azure_rm_securitygroup:
#      resource_group: "{{ eco_azure.name }}"
#      name: "{{ eco_azure.sg_tunnel.name }}"
#      rules:
#        - name: SSH
#          protocol: Tcp
#          destination_port_range: 22
#          access: Allow
#          priority: 1001
#          direction: Inbound
#
  - name: Create public IP address   ### THIS IP should be in the other end of the tunnel 
    azure_rm_publicipaddress:
      resource_group: "{{ eco_azure.name }}"
      allocation_method: Static
      name: "{{ item.ip_pub_name }}"
    with_items: "{{ eco_azure.vm }}"

#  - name: Create virtual network inteface card - tunnel 
#    azure_rm_networkinterface:
#      resource_group: "{{ eco_azure.name }}"
#      name: "{{ item.network_interface.name }}"
#      virtual_network: "{{ eco_azure.vnet.name }}"
#      subnet: "{{ eco_azure.subnet.name }}"
#      public_ip_name: tunnel-ip-pub
#      security_group: "{{ eco_azure.sg_tunnel.name }}"
#    with_items: "{{ eco_azure.vm_tunnel }}"

  - name: Create virtual network inteface card
    azure_rm_networkinterface:
      resource_group: "{{ eco_azure.name }}"
      name: "{{ item.network_interface.name }}"
      virtual_network: "{{ eco_azure.vnet.name }}"
      subnet: "{{ eco_azure.subnet.name }}"
      #public_ip: False  # bug that force us to use pub_ip https://github.com/ansible/ansible/issues/36163
      public_ip_name: "{{ item.ip_pub_name }}"
      security_group: "{{ eco_azure.sg.name }}"
    with_items: "{{ eco_azure.vm }}"

  - name: Create VM
    azure_rm_virtualmachine:
      resource_group: "{{ eco_azure.name }}"
      name: "{{ item.name }}"
      vm_size: "{{ item.vm_size }}"
      admin_username: "{{ item.username }}"
      ssh_password_enabled: false
      ssh_public_keys: 
        - path: "/home/{{ item.username }}/.ssh/authorized_keys"
          key_data: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC/jpXse+livl1Ih/eBIpZLLdudSrpxlg4oNb+PecRE8ZhznGHIUg6nnoKb06NHxMO0iERpzZyMRtxoajN7CGqp0LF6VHYUHSiEHPuy1tBiYQ24wx4HWeUefUKq8mRz2Bel5gYyGkl4v+8h0OVfcm+42s6kmDpkYP9MdRQ9sZWbLXZhWH7eLzlsayeqSof1zr7JpbpfMHO2RDQP9ESpp2VEKJA1WARGDIZ5Enfp4qNha7cl7yNCQFB3JgkfHa+LEn3yNnz1u5OuwwEiUmtup5+ham6bSUKgjDBtLzogxwDwAtvdcesjK8uRHZHSQ3/9XBpTFDmbxKK9cfMXZOZJgxYN"
      network_interfaces: "{{ item.network_interface.name }}"
      image:
          offer: UbuntuServer
          publisher: Canonical
          sku: 16.04-LTS
          version: latest
      managed_disk_type: "{{ item.managed_disk_type }}"
      data_disks: "{{ item.data_disks }}"
    with_items: "{{ eco_azure.vm }}"

#  - name: Create VM - tunnel
#    azure_rm_virtualmachine:
#      resource_group: "{{ eco_azure.name }}"
#      name: "{{ item.name }}"
#      vm_size: "{{ item.vm_size }}"
#      admin_username: "{{ item.username }}"
#      ssh_password_enabled: false
#      ssh_public_keys: 
#        - path: "/home/{{ item.username }}/.ssh/authorized_keys"
#          key_data: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC/jpXse+livl1Ih/eBIpZLLdudSrpxlg4oNb+PecRE8ZhznGHIUg6nnoKb06NHxMO0iERpzZyMRtxoajN7CGqp0LF6VHYUHSiEHPuy1tBiYQ24wx4HWeUefUKq8mRz2Bel5gYyGkl4v+8h0OVfcm+42s6kmDpkYP9MdRQ9sZWbLXZhWH7eLzlsayeqSof1zr7JpbpfMHO2RDQP9ESpp2VEKJA1WARGDIZ5Enfp4qNha7cl7yNCQFB3JgkfHa+LEn3yNnz1u5OuwwEiUmtup5+ham6bSUKgjDBtLzogxwDwAtvdcesjK8uRHZHSQ3/9XBpTFDmbxKK9cfMXZOZJgxYN"
#      network_interfaces: "{{ item.network_interface.name }}"
#      image:
#          offer: UbuntuServer
#          publisher: Canonical
#          sku: 16.04-LTS
#          version: latest
#    with_items: "{{ eco_azure.vm_tunnel }}"

##This works with ansible.devel (version 2.5)
#  - name: Create managed disk
#    azure_rm_managed_disk:
#      name: mymanageddisk
#      location: "{{ eco_azure.location }}"
#      resource_group: "{{ eco_azure.name }}"
#      disk_size_gb: 4
#
#  - name: Mount the managed disk to VM
#    azure_rm_managed_disk:
#      name: mymanageddisk2
#      location: "{{ eco_azure.location }}"
#      resource_group: "{{ eco_azure.name }}"
#      disk_size_gb: 4
#      managed_by: azu-ve104
#
#
