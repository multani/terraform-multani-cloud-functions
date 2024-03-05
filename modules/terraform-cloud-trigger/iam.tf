resource "google_project_iam_member" "this" {
  for_each = toset([
    # https://cloud.google.com/pubsub/docs/access-control#roles
    # Read secrets
    "roles/secretmanager.secretAccessor",

    # https://cloud.google.com/pubsub/docs/access-control#roles
    # Consume messages
    "roles/pubsub.viewer",
  ])

  role    = each.key
  member  = "serviceAccount:${module.this.service_account_email}"
  project = data.google_project.this.project_id
}

# Allow the service publishing the events in Eventarc (for Pub/Sub events) to
# call the Cloud Function.
#
# See https://cloud.google.com/functions/docs/calling/eventarc and more
# specifically,
# https://cloud.google.com/functions/docs/calling/eventarc#trigger-identity
#
# (We deploy a Cloud Function, but the underlying Google service that runs it is
# actually Cloud Run.)
resource "google_cloud_run_service_iam_member" "this" {
  service  = module.this.name
  location = module.this.location

  role   = "roles/run.invoker"
  member = "serviceAccount:${module.this.service_account_email}"
}
