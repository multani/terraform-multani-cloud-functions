output "service_account_name" {
  description = "The service account FQDN used by the function"
  value       = module.this.service_account_name
}

output "uri" {
  description = "The URI to call the function"
  value       = local.url
  sensitive   = true
}
