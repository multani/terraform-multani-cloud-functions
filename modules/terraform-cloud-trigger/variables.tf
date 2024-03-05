variable "name" {
  description = "Name of the function and other Google resources"
  default     = "terraform-cloud-trigger"
  type        = string
}

variable "location" {
  description = "Google region where to deploy the function"
  type        = string
}

variable "source_code" {
  description = "The source code on Google Cloud Storage of the function"
  type = object({
    bucket = string
    object = string
  })
}

variable "schedule" {
  description = "When to schedule the function"
  default     = "0 7 * * *"
  type        = string
}

variable "tfe_token" {
  description = "The Terraform Cloud team token to use"
  type        = string
  sensitive   = true
}

variable "tfe_organization" {
  description = "Which organization to schedule triggers into"
  type        = string
}
