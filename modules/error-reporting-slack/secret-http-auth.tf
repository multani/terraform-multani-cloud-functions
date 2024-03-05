resource "google_secret_manager_secret" "http_auth" {
  secret_id = "${var.name}-http-auth"

  replication {
    auto {}
  }
}

resource "random_password" "http_auth" {
  length = 32
}

resource "google_secret_manager_secret_version" "http_auth" {
  secret      = google_secret_manager_secret.http_auth.id
  secret_data = random_password.http_auth.result
}
