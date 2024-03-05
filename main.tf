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
  version = "1.0.1"

  source_dir = path.module

  name        = var.name
  bucket_name = var.bucket
}
