variable "prefix" {
  description = "The prefix used for all resources in this example"
  default     = "audioSummarizer"
}

variable "location" {
  description = "The Azure Region in which all resources in this example should be created"
  default     = "West Europe"
}

variable "client_id" {
  description = "The Client ID of the Service Principal"
  default     = "f3c6d67c-b20c-4ec3-8ab1-f63e55dacb8e"
}

variable "client_secret" {
  description = "The Client Secret of the Service Principal"
  default     = "DVE8Q~BqaLH2JQJo9M6GL0OR2qj3QHjJBNnrnad_"
}

variable "tenant_id" {
  description = "The Tenant ID for the Service Principal"
  default     = "504be20d-314c-4608-bedf-67c39db39b83"
}
