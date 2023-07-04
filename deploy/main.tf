module "aks" {
  source = "Azure/aks/azurerm"
  version = "4.0.0"

  client_id             = var.client_id
  client_secret         = var.client_secret
  resource_group_name   = "${var.prefix}-rg"
  kubernetes_cluster_name = "${var.prefix}-aks"
  location              = var.location
  tenant_id             = var.tenant_id
}

resource "azurerm_container_registry" "acr" {
  name                     = "${var.prefix}acr"
  resource_group_name      = "${var.prefix}-rg"
  location                 = var.location
  sku                      = "Basic"
  admin_enabled            = true
}