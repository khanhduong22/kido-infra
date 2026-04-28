# --- Branch Protection cho danang-badminton-hub ---
resource "github_branch_protection" "badminton_main" {
  repository_id = "danang-badminton-hub"
  pattern       = "main"

  # Bắt buộc CI/CD Pass (Ví dụ: phải pass action 'build')
  required_status_checks {
    strict   = true
    contexts = ["build"] # TODO: Đổi thành tên job thực tế của GitHub Action (ví dụ: 'build', 'test')
  }

  enforce_admins = false # Tạm thời nới lỏng cho Admin (cho phép bạn push thẳng)
}

# --- Branch Protection cho kido-infra ---
resource "github_branch_protection" "infra_main" {
  repository_id = "kido-infra"
  pattern       = "main"

  enforce_admins = false # Tạm thời nới lỏng cho Admin
}
