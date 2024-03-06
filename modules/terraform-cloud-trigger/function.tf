module "this" {
  source  = "multani/function/google"
  version = "1.0.2"

  name        = var.name
  description = "Trigger runs on Terraform Cloud"

  location    = var.location
  runtime     = "python312"
  entry_point = "terraform_cloud_trigger_all"

  source_code = {
    bucket = var.source_code.bucket
    object = var.source_code.object
  }

  environment_variables = {
    LOG_FORMAT = "gcp"
  }

  event_trigger = {
    # Trigger when a Pub/Sub message is received
    event_type   = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic = google_pubsub_topic.this.id
  }
}
