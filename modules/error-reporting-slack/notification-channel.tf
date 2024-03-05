# The actual notification channel where to send the alerts to
locals {
  url = "${module.this.uri}?auth_token=${google_secret_manager_secret_version.http_auth.secret_data}"
}

resource "google_monitoring_notification_channel" "this" {
  display_name = "Slack: Error Reporting"
  type         = "webhook_tokenauth"

  labels = {
    url = local.url
  }

  #sensitive_labels {
  #auth_token = google_secret_manager_secret_version.http_auth.secret_data
  #}

  user_labels = {
    identifier = "slack-errors"
    function   = var.name
  }
}
