terraform {
  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 6.0"
    }
    vercel = {
      source  = "vercel/vercel"
      version = "~> 1.0"
    }
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
    signoz = {
      source  = "Signoz/signoz"
      version = "~> 0.0.4"
    }
    nginxproxymanager = {
      source  = "Sander0542/nginxproxymanager"
      version = "~> 1.0"
    }
    sops = {
      source  = "carlpett/sops"
      version = "~> 1.1"
    }
    grafana = {
      source  = "grafana/grafana"
      version = "~> 3.0"
    }
  }
}

provider "github" {
  token = data.sops_file.secrets.data["github_token"]
  owner = "khanhduong22"
}

provider "vercel" {
  api_token = data.sops_file.secrets.data["vercel_api_token"]
}

provider "cloudflare" {
  api_token = data.sops_file.secrets.data["cloudflare_api_token"]
}

provider "signoz" {
}

provider "nginxproxymanager" {
  url      = "http://${data.sops_file.secrets.data["shared_vps_host"]}:81"
  username = data.sops_file.secrets.data["npm_email"]
  password = data.sops_file.secrets.data["npm_password"]
}

provider "grafana" {
  url  = "https://grafana.khanhdp.com"
  auth = data.sops_file.secrets.data["grafana_auth_token"]
}
