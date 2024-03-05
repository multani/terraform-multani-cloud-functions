resource "google_secret_manager_secret" "tfe_token" {
  secret_id = "${var.name}-tfe-token"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "tfe_token" {
  secret      = google_secret_manager_secret.tfe_token.id
  secret_data = var.tfe_token
}
