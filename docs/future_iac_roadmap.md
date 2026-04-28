# 🚀 Kido's Infrastructure Roadmap & TODOs

Danh sách này lưu lại những ý tưởng và công việc còn dang dở để bạn có thể tiếp tục tự động hóa hệ thống (IaC) khi có thời gian.

## 🟢 1. Nâng cấp Terraform (IaC nâng cao)

- `[ ]` **Quản lý SigNoz Dashboards bằng Terraform**: 
  - *Mục tiêu:* Thay vì sửa biểu đồ bằng tay trên giao diện SigNoz, ta sẽ xuất file JSON của biểu đồ (ví dụ: `vps_overview.json`), lưu vào folder `terraform/dashboards/` và dùng `resource "signoz_dashboard"` để tự động deploy. Lợi ích: Lỡ tay xóa Dashboard thì gõ `terraform apply` là nó đẻ lại y nguyên.
- `[ ]` **Tự động hóa Alert Rules (Cảnh báo)**: 
  - *Mục tiêu:* Viết code Terraform (`resource "signoz_alert"`) để tự động gửi thông báo về Slack/Telegram khi CPU > 80% hoặc RAM sắp đầy.
- `[ ]` **Tích hợp Vercel Projects**: 
  - *Mục tiêu:* Cấp lại Vercel API Token (có đủ quyền), sau đó khôi phục lại file `vercel_projects.tf` để Terraform tự động tạo project Next.js và tự bơm biến môi trường (`NEXT_PUBLIC_API_URL`, `DATABASE_URL`) vào Vercel. Không cần copy-paste biến môi trường bằng tay nữa.
- `[ ]` **Cấu hình chứng chỉ SSL tự động (Let's Encrypt)**: 
  - *Mục tiêu:* Cấu hình `nginxproxymanager_certificate` trong Terraform để nó tự xin SSL Let's Encrypt, thay vì gắn Custom SSL (ID=1) bằng tay.

## 🔵 2. Ansible (Server Configuration Management)

- `[ ]` **Khởi tạo Ansible Playbooks**:
  - *Mục tiêu:* Học và viết các file YAML của Ansible để thay thế việc SSH vào VPS gõ từng lệnh.
- `[ ]` **Tự động cài đặt Docker & Môi trường**:
  - *Mục tiêu:* Viết 1 Playbook để chỉ cần gõ 1 lệnh là VPS mới tinh sẽ tự động cài `git`, `zsh`, `docker`, `docker-compose` chuẩn bài.
- `[ ]` **Tự động Clone & Deploy Code**:
  - *Mục tiêu:* Viết Playbook tự động clone các Repo (`kido-infra`, `danang-badminton-hub`), tự động chạy `docker-compose up -d`. Kết hợp Ansible với Github Actions để làm CI/CD cực mượt.

## 🟣 3. Tối ưu Hệ thống & Bảo mật
- `[ ]` **Đóng toàn bộ Port Public trên VPS**: Đổi cấu hình `docker-compose` của các app nội bộ thành `127.0.0.1:PORT:PORT` để ép toàn bộ luồng mạng phải đi qua Nginx Proxy Manager.
- `[ ]` **Quản lý file `.env` bằng SOPS**: Thay vì lưu `.env` trên VPS bừa bãi, dùng SOPS để mã hóa file `.env` rồi đẩy thẳng lên Github, Ansible sẽ tự động kéo về và giải mã tại VPS.
