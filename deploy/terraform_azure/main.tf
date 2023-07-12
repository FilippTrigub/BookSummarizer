terraform {
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
      version = "3.64.0"
    }
  }
}

provider "azurerm" {
  features {}
  skip_provider_registration = true
}

resource "azurerm_resource_group" "rg" {
  name                      = var.prefix
  location                  = var.location
}

resource "azurerm_service_plan" "example" {
  name                = "GenMyBotASP"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  sku_name            = "B1"
}

resource "azurerm_container_registry" "acr" {
  depends_on                = [azurerm_resource_group.rg]
  name                      = "${var.prefix}Acr"
  resource_group_name       = azurerm_resource_group.rg.name
  location                  = azurerm_resource_group.rg.location
  sku                       = "Basic"
  admin_enabled             = true
}
