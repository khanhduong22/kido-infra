# Deployment Rules & Guidelines

## Prerequisites
The environment is already fully authenticated via CLI for the following services:
- **GitHub** (`gh` CLI)
- **Vercel** (`vercel` CLI)
- **VPS (Contabo)** (`ssh` is pre-configured and authenticated)
- **Supabase / Neon** (CLI authenticated)

## Deployment Workflow
**DO NOT** modify hardcoded `localhost` URLs in deployment scripts (e.g., changing `localhost:3000` to a public IP) just to deploy remotely.

Instead, follow these standard procedures:

### 1. VPS Infrastructure (Grafana, Docker, etc.)
Since SSH is authenticated, you can deploy by either:
- SSH-ing directly into the VPS and executing the scripts locally on the server.
  ```bash
  ssh root@144.91.88.242
  cd /path/to/project
  python3 deploy_merged.py
  ```
- Or committing changes via Git and pulling them on the VPS.

### 2. Frontend & Backend
- Use `vercel deploy` for frontend/Next.js applications.
- Use `supabase` or `neon` CLI tools directly for database migrations.

By relying on the existing CLI authentications, we keep the codebase clean and avoid exposing production IPs or credentials in the scripts.
