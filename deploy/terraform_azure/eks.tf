#resource "azurerm_kubernetes_cluster" "aks" {
#  depends_on                = [azurerm_resource_group.rg]
#  name                      = "${var.prefix}Aks"
#  location                  = azurerm_resource_group.rg.location
#  resource_group_name       = azurerm_resource_group.rg.name
#  dns_prefix                = "${var.prefix}Aks"
#  node_resource_group       = "${var.prefix}AksNodes"
#
#  default_node_pool {
#    name                    = "default"
#    node_count              = 1
#    vm_size                 = "Standard_B2s"
#    os_disk_size_gb         = 30
#  }
#
#  service_principal {
#    client_id               = var.client_id
#    client_secret           = var.client_secret
#  }
#}
#
#resource "azurerm_role_assignment" "example" {
#    scope                    = azurerm_container_registry.acr.id
#    role_definition_name     = "AcrPull"
#    principal_id             = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
#}
