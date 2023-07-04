variable "prefix" {
  description = "The prefix used for all resources in this example"
  default     = "audio-summarizer"
}

variable "location" {
  description = "The Azure Region in which all resources in this example should be created"
  default     = "West Europe"
}

variable "client_id" {
  description = "The Client ID of the Service Principal"
}

variable "client_secret" {
  description = "The Client Secret of the Service Principal"
}

variable "tenant_id" {
  description = "The Tenant ID for the Service Principal"
}
