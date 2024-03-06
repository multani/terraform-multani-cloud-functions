variable "name" {
  description = "Name of the function and other Google resources"
  default     = "slack-error-reporting"
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

variable "slack_token" {
  description = "The Slack 'Bot User OAuth Token'"
  type        = string
  sensitive   = true
}

variable "slack_channel_id" {
  description = "The Slack channel ID to report errors to"
  type        = string
}
