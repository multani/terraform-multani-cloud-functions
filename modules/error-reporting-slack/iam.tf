# https://cloud.google.com/pubsub/docs/access-control#roles
# Read secrets
resource "google_project_iam_member" "this" {
  role    = "roles/secretmanager.secretAccessor"
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
resource "google_cloud_run_service_iam_member" "trigger_public" {
  service  = module.this.name
  location = module.this.location

  role = "roles/run.invoker"
  # Allow everyone to call the function
  member = "allUsers"
}
