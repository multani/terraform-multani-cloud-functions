resource "google_secret_manager_secret" "slack" {
  secret_id = "${var.name}-slack-token"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "slack" {
  count       = var.slack_token == null ? 0 : 1
  secret      = google_secret_manager_secret.slack.id
  secret_data = var.slack_token
}
