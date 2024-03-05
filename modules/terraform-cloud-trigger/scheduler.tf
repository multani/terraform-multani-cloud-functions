resource "google_cloud_scheduler_job" "this" {
  name        = var.name
  description = "Trigger runs in Terraform Cloud workspaces"
  region      = var.location

  schedule = var.schedule

  pubsub_target {
    topic_name = google_pubsub_topic.this.id

    data = base64encode(jsonencode({
      organization = var.tfe_organization
      secret_name  = google_secret_manager_secret_version.tfe_token.name

      tags_included = []
      tags_excluded = ["ignore"]
    }))
  }
}
