resource "google_pubsub_topic" "this" {
  name = var.name

  # This should be executed fairly quickly.
  message_retention_duration = "600s"
}
