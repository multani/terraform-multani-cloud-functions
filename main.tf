terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
    }
  }
}

variable "name" {
  description = "The name of the source code folder in the storage bucket"
  default     = "functions"
  type        = string
}

variable "bucket" {
  description = "The name of the Cloud Storage bucket to store the function code in."
  type        = string
}

module "this" {
  source  = "multani/function/google//modules/code"
  version = "1.0.2"

  source_dir = path.module

  name        = var.name
  bucket_name = var.bucket
}

output "bucket" {
  description = "The bucket in which the function code is stored"
  value       = module.this.bucket
}

output "object" {
  description = "The bucket's object representing the function code"
  value       = module.this.object
}

