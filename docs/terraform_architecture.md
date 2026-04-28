# Kiến trúc & Luồng hoạt động của Terraform (Infrastructure as Code)

Tài liệu này sẽ giúp bạn hình dung rõ ràng "cái thứ tên là Terraform này rút cuộc giúp ích được gì cho mình?". Nói một cách đơn giản, Terraform biến bạn từ một người **thợ xây** (phải tự tay làm từng việc) thành một **kiến trúc sư** (chỉ cần vẽ bản vẽ, máy móc sẽ tự xây).

---

## 1. Luồng hoạt động (The Terraform Flow)

Thay vì bạn phải đăng nhập vào 4 trang web khác nhau (Cloudflare, GitHub, Vercel, SigNoz) để bấm các nút cấu hình, mọi thứ giờ đây tập trung tại một luồng duy nhất.

```mermaid
graph TD
    classDef user fill:#3498db,color:#fff,stroke:#2980b9,stroke-width:2px;
    classDef code fill:#2ecc71,color:#fff,stroke:#27ae60,stroke-width:2px;
    classDef tf fill:#9b59b6,color:#fff,stroke:#8e44ad,stroke-width:2px;
    classDef cloud fill:#f39c12,color:#fff,stroke:#d35400,stroke-width:2px;
    classDef state fill:#34495e,color:#fff,stroke:#2c3e50,stroke-width:2px;

    User["Dev (Kido / AI)"]:::user
    Code["Code (.tf files)\n'Bản vẽ thiết kế'"]:::code
    Plan["terraform plan\n'So sánh & Mô phỏng'"]:::tf
    Apply["terraform apply\n'Thực thi'"]:::tf
    State[("terraform.tfstate\n'Bộ nhớ thực tế'")]:::state
    
    subgraph Thuc_Te ["Hệ thống thực tế (Production)"]
        CF["Cloudflare (DNS)"]:::cloud
        GH["GitHub (Repos, Secrets)"]:::cloud
        VC["Vercel (Hosting, Env Vars)"]:::cloud
        SN["SigNoz (Alerts, Dashboards)"]:::cloud
    end

    User -- "1. Sửa/Thêm cấu hình" --> Code
    Code -- "2. Lên kế hoạch" --> Plan
    Plan -. "Đọc trạng thái cũ" .-> State
    Plan -- "3. Xác nhận thay đổi" --> Apply
    
    Apply == "Gọi API" ==> CF
    Apply == "Gọi API" ==> GH
    Apply == "Gọi API" ==> VC
    Apply == "Gọi API" ==> SN
    
    Apply -- "4. Cập nhật lại bộ nhớ" --> State
```

### Giải thích 4 bước thần thánh:
1. **Code (`.tf`)**: Bạn khai báo *kết quả cuối cùng* bạn muốn (Ví dụ: "Tôi muốn có 1 domain tên là `api.khanhdp.com`").
2. **Plan**: Terraform sẽ kiểm tra hệ thống thực tế xem domain đó có chưa. Nếu chưa có, nó sẽ in ra màn hình: *"Domain này chưa có, tôi chuẩn bị TẠO MỚI nhé?"*. Nếu có rồi mà bị sai IP, nó báo: *"IP bị sai, tôi chuẩn bị SỬA LẠI nhé?"*.
3. **Apply**: Nếu bạn gõ `yes`, Terraform sẽ tự động gọi API của Cloudflare để làm đúng những gì nó vừa hứa.
4. **State (`.tfstate`)**: Làm xong, nó ghi nhớ kết quả vào file State để lần sau không bị nhầm lẫn.

---

## 2. Rút cuộc Terraform làm được gì cho hệ thống của tôi?

Dưới đây là các "Siêu năng lực" cụ thể mà Terraform mang lại cho hạ tầng `kido-infra`:

### 🎯 Khắc phục thảm họa (Disaster Recovery) siêu tốc
- **Vấn đề**: Giả sử VPS của bạn bị cháy ổ cứng, hoặc lỡ tay xóa nhầm toàn bộ Dashboard siêu đẹp trên Grafana/SigNoz. Nếu setup bằng tay, bạn sẽ phải tốn hàng tuần để nhớ lại và cấu hình lại từ đầu.
- **Terraform làm gì**: Bấm 1 nút `terraform apply`. Chờ 1 phút. Toàn bộ DNS, Github Secrets, Vercel Env Vars, và Dashboards được tạo lại y chang như lúc đầu.

### 🎯 Cập nhật hàng loạt (Mass Update) thay vì làm "Cửu vạn"
- **Vấn đề**: Bạn đổi IP của VPS. Bạn có 10 subdomains (api, grafana, signoz, otel...). Bạn phải vào Cloudflare click chuột sửa tay 10 lần. Sau đó bạn phải vào 5 repo GitHub để sửa secret `VPS_HOST`. Sau đó vào Vercel sửa biến môi trường. Rất mệt và dễ sai sót.
- **Terraform làm gì**: Bạn chỉ cần sửa 1 biến duy nhất `shared_vps_host = "IP_MOI"` trong file `variables.tf`. Chạy lệnh. Terraform tự động vác cái IP mới đó đem đi cập nhật cho Cloudflare, chèn vào 5 repo GitHub, chèn vào Vercel. Không trật 1 li.

### 🎯 Giao tiếp cực hiệu quả với AI (Open Claw / Cursor)
- **Vấn đề**: AI rất giỏi code, nhưng nó không có mắt để nhìn giao diện UI của Vercel hay Cloudflare. Nếu bạn cấu hình bằng tay trên Web, AI sẽ mù tịt không biết hạ tầng đang kết nối với nhau thế nào (VD: App NextJS đang chọc vào database nào?).
- **Terraform làm gì**: Code Terraform chính là "Ngôn ngữ giao tiếp chung". AI đọc thư mục `terraform/` là hiểu toàn bộ hạ tầng: *"À, repo badminton đang được host ở Vercel, xài biến môi trường NEXT_PUBLIC_API_URL trỏ về server api.khanhdp.com, và domain này được proxy qua Cloudflare"*. Nó hiểu 100% ngữ cảnh mà không cần bạn phải giải thích.

### 🎯 Quản lý bảo mật (Ai làm gì, khi nào?)
- **Vấn đề**: Bạn cấp tài khoản GitHub/Cloudflare cho người khác (hoặc AI), họ vào UI bấm xóa nhầm repo hoặc phá cấu hình, bạn không thể tìm ra ai làm.
- **Terraform làm gì**: Mọi thay đổi đều là Code. Khi muốn thêm/sửa hạ tầng, người đó (hoặc AI) phải sửa code `.tf` và tạo Pull Request (PR). Bạn là người review code, nếu OK mới duyệt. Lịch sử Git lưu lại vĩnh viễn ai đã sửa hạ tầng, vào ngày nào, và vì lý do gì.

## Tóm lại
`kido-infra/terraform` chính là **Bản kiểm soát quyền lực tuyệt đối** của bạn đối với toàn bộ hệ thống phân tán bên ngoài VPS!
