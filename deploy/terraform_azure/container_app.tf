resource "azurerm_log_analytics_workspace" "audio_summarizer" {
  name                = "acctest-01"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_container_app_environment" "audio_summarizer" {
  name                       = "${var.prefix}Environment"
  location                   = azurerm_resource_group.rg.location
  resource_group_name        = azurerm_resource_group.rg.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.audio_summarizer.id
}

resource "azurerm_container_app" "audio_summarizer_container_app" {
  name                         = "${var.prefix}app"
  container_app_environment_id = azurerm_container_app_environment.audio_summarizer.id
  resource_group_name          = azurerm_resource_group.rg.name
  revision_mode                = "Single"

  template {
    container {
      name   = "examplecontainerapp"
      image  = "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"
      cpu    = 0.25
      memory = "0.5Gi"
    }
  }
}