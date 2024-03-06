# The actual notification channel where to send the alerts to
locals {
  url = "${module.this.uri}?auth_token=${google_secret_manager_secret_version.http_auth.secret_data}"

  http_auth_username = "func-${var.name}"
}

resource "google_monitoring_notification_channel" "this" {
  display_name = "Slack: Error Reporting (${var.name})"
  type         = "webhook_basicauth"

  labels = {
    url      = module.this.uri
    username = local.http_auth_username
    password = google_secret_manager_secret_version.http_auth.secret_data
  }
}
