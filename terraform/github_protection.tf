# --- Branch Protection cho danang-badminton-hub ---
resource "github_branch_protection" "badminton_main" {
  repository_id = "danang-badminton-hub"
  pattern       = "main"

  # Bắt buộc Pull Request
  required_pull_request_reviews {
    required_approving_review_count = 0 # Có thể tăng lên 1 nếu có team member
    require_code_owner_reviews      = false
  }

  # Bắt buộc CI/CD Pass
  required_status_checks {
    strict   = true
    contexts = ["build"] # TODO: Đổi thành tên job thực tế của GitHub Action (ví dụ: 'build', 'test')
  }

  enforce_admins = true # Bắt buộc admin cũng phải tuân thủ luật
}

# --- Branch Protection cho kido-infra ---
resource "github_branch_protection" "infra_main" {
  repository_id = "kido-infra"
  pattern       = "main"

  required_pull_request_reviews {
    required_approving_review_count = 0
  }

  enforce_admins = true
}
