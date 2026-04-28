# --- Định nghĩa Vercel Projects ---

# resource "vercel_project" "badminton_hub" {
#   name      = "danang-badminton-hub"
#   framework = "nextjs"
#
#   git_repository = {
#     type = "github"
#     repo = "khanhduong22/danang-badminton-hub"
#   }
#
#   # Cấu hình môi trường cho Production
#   environment = [
#     {
#       key    = "NEXT_PUBLIC_API_URL"
#       value  = "https://api.khanhdp.com"
#       target = ["production"]
#     },
#     {
#       key    = "DATABASE_URL"
#       value  = "postgresql://..."
#       target = ["production"]
#     }
#   ]
# }

# Quản lý Domain (ví dụ: gán domain cho project)
# resource "vercel_project_domain" "badminton_domain" {
#   project_id = vercel_project.badminton_hub.id
#   domain     = "badminton.khanhdp.com"
# }
