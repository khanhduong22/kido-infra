# Kido-Infra Architecture

Sơ đồ dưới đây mô tả kiến trúc tổng thể của `kido-infra`, đóng vai trò là "Control Plane" (Trung tâm điều khiển) cho toàn bộ hệ sinh thái của bạn, kết hợp giữa **Infrastructure as Code (Terraform)** và **Containerized Services (Docker Compose)**.

```mermaid
graph TD
    %% Định nghĩa các Style cho đẹp
    classDef tf fill:#5c4ee5,color:#fff,stroke:#3b31a3,stroke-width:2px;
    classDef docker fill:#0db7ed,color:#fff,stroke:#098ab3,stroke-width:2px;
    classDef cloudflare fill:#f38020,color:#fff,stroke:#d46400,stroke-width:2px;
    classDef vercel fill:#000,color:#fff,stroke:#333,stroke-width:2px;
    classDef github fill:#181717,color:#fff,stroke:#000,stroke-width:2px;
    classDef signoz fill:#f06a6a,color:#fff,stroke:#d04a4a,stroke-width:2px;
    classDef grafana fill:#f46800,color:#fff,stroke:#c45300,stroke-width:2px;
    classDef vps fill:#2c3e50,color:#fff,stroke:#1a252f,stroke-width:2px;

    subgraph Kido_Infra ["Kido-Infra Repository (Control Plane)"]
        TF["Terraform (IaC)"]:::tf
        DC["Docker Compose"]:::docker
    end

    subgraph SaaS ["External SaaS & APIs"]
        CF["Cloudflare (DNS/CDN)"]:::cloudflare
        VC["Vercel (Next.js Apps)"]:::vercel
        GH["GitHub (Source Code & CI/CD)"]:::github
    end

    subgraph Contabo ["Contabo VPS"]
        Nginx["Nginx Proxy Manager"]:::docker
        
        subgraph Observability ["Observability Stack"]
            SigNoz["SigNoz (APM, Traces, Metrics)"]:::signoz
            Grafana["Grafana (Dashboards)"]:::grafana
            OTel["OpenTelemetry Collector"]:::docker
        end
    end

    %% Terraform Control Flow
    TF == "Cấp phát tên miền & Proxy" ==> CF
    TF == "Cấu hình Deployment & Env Vars" ==> VC
    TF == "Bơm Secrets & Branch Protection" ==> GH
    TF == "Quản lý Alerts & Dashboards" ==> SigNoz

    %% Docker Compose Deployment Flow
    DC -. "Triển khai Container" .-> Nginx
    DC -. "Triển khai Container" .-> Observability

    %% Traffic & Data Flow
    CF -- "Routing HTTP/HTTPS" --> Nginx
    Nginx -- "Reverse Proxy" --> SigNoz
    Nginx -- "Reverse Proxy" --> Grafana
    
    GH -- "Webhooks (CI/CD Traces)" --> OTel
    OTel -- "Đẩy dữ liệu Telemetry" --> SigNoz
```

## Diễn giải kiến trúc:

1. **Control Plane (`kido-infra`)**:
   - Chứa code Terraform để tự động hóa toàn bộ hạ tầng (DNS, GitHub, Vercel, SigNoz).
   - Chứa các file `docker-compose.yml` để dựng các dịch vụ core trên máy chủ.
   
2. **Infrastructure as Code (Terraform)**:
   - Thay vì setup bằng tay, Terraform giao tiếp với API của các bên thứ ba (Cloudflare, Vercel, GitHub, SigNoz) để đồng bộ hóa trạng thái mong muốn từ code thành thực tế.

3. **Contabo VPS**:
   - Dùng **Nginx Proxy Manager** làm Gateway để nhận request từ Cloudflare và điều phối vào trong.
   - Chạy cụm **Observability Stack** (SigNoz, Grafana, OpenTelemetry) để giám sát hiệu năng hệ thống.

4. **Data Flow**:
   - GitHub bắn webhook mỗi khi có Action chạy về OpenTelemetry Collector. Collector xử lý rồi ném cho SigNoz vẽ ra các biểu đồ CI/CD.
