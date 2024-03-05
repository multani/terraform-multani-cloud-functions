module "this" {
  source  = "multani/function/google"
  version = "1.0.2"

  name        = var.name
  description = "Report errors on Slack"

  location    = var.location
  runtime     = "python312"
  entry_point = "error_reporting_slack"

  source_code = {
    bucket = var.source_code.bucket
    object = var.source_code.object
  }

  environment_variables = {
    LOG_FORMAT             = "gcp"
    SECRET_SLACK_API_TOKEN = "${google_secret_manager_secret.slack.name}/versions/latest"
    SECRET_HTTP_AUTH_TOKEN = google_secret_manager_secret_version.http_auth.name
  }
}
