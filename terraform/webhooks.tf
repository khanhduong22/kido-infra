locals {
  # Add the names of repositories that should send webhooks to SigNoz
  repos = [
    "danang-badminton-hub",
    "kido-infra",
    "p2p-tracker"
  ]
}

resource "github_repository_webhook" "signoz_cicd" {
  for_each   = toset(local.repos)
  repository = each.key

  configuration {
    url          = "https://otel.khanhdp.com/events"
    content_type = "json"
    secret       = data.sops_file.secrets.data["signoz_webhook_secret"]
    insecure_ssl = false
  }

  active = true
  events = ["*"]
}
