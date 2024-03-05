```json
{
  "insertId": "1c0im8qc5b6",
  "jsonPayload": {
    "summary": "Webhook failed with 500 Internal Server Error status code.",
    "errorReference": "iw-ACKKAgIvLv7OmKhCjgICLy7-zpioYBmiigICLy7-zpioD"
  },
  "resource": {
    "type": "stackdriver_notification_channel",
    "labels": {
      "project_id": "290596050683",
      "channel_id": "4588183942484313575"
    }
  },
  "timestamp": "2023-12-11T22:10:58.462203Z",
  "severity": "ERROR",
  "logName": "projects/multani-admin/logs/monitoring.googleapis.com%2Fnotification_channel_events",
  "receiveTimestamp": "2023-12-11T22:11:02.343716221Z"
}
```


Interesting logs:

* `logName=~"^projects/.+/logs/clouderrorreporting.googleapis.com%2Finsights"`
