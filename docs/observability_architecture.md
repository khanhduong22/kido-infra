# Observability Stack Architecture (SigNoz & Grafana)

Tài liệu này đi sâu vào kiến trúc chi tiết của cụm **Observability** nằm trong hai thư mục `signoz` và `grafana` trên VPS Contabo của bạn. Đây là trái tim của hệ thống giám sát, thu thập mọi log, metric và trace từ các dịch vụ khác.

## 1. Kiến trúc luồng dữ liệu (Data Flow) chi tiết

Sơ đồ dưới đây mô tả cách dữ liệu (Traces, Metrics, Logs) chảy từ các App của bạn vào OTel Collector, được lưu trữ tại ClickHouse và hiển thị lên UI của SigNoz / Grafana.

```mermaid
graph TD
    classDef app fill:#e74c3c,color:#fff,stroke:#c0392b,stroke-width:2px;
    classDef otel fill:#8e44ad,color:#fff,stroke:#71368a,stroke-width:2px;
    classDef db fill:#f1c40f,color:#000,stroke:#f39c12,stroke-width:2px;
    classDef ui fill:#2ecc71,color:#fff,stroke:#27ae60,stroke-width:2px;
    classDef github fill:#34495e,color:#fff,stroke:#2c3e50,stroke-width:2px;

    subgraph Data_Sources ["Data Sources (Telemetry Emitters)"]
        NextJS["Next.js Apps (Badminton, P2P)"]:::app
        Scraper["Vietnam Market Scraper (Node.js)"]:::app
        Postgres["TimescaleDB / Postgres"]:::db
        GH["GitHub Actions (CI/CD)"]:::github
        Docker["Docker Container Logs"]:::app
    end

    subgraph SigNoz_Folder ["/signoz (Data Ingestion & Storage)"]
        OTel_gRPC["OTel Collector (gRPC: 4317)"]:::otel
        OTel_HTTP["OTel Collector (HTTP: 4318)"]:::otel
        OTel_Webhook["OTel Github Webhook (19418)"]:::otel
        
        ClickHouse[("ClickHouse DB (Columnar)")]:::db
        QueryService["SigNoz Query Service"]:::otel
    end

    subgraph UIs ["Observability UIs"]
        SigNozUI["SigNoz Frontend (Port 3301)"]:::ui
        GrafanaUI["Grafana Dashboard (Port 3000)"]:::ui
    end

    %% Ingestion Flows
    NextJS -- "Send Traces (Web Vitals)" --> OTel_HTTP
    Scraper -- "Send Traces & Metrics" --> OTel_gRPC
    Postgres -- "Scrape Metrics" --> OTel_gRPC
    GH -- "Push Webhooks" --> OTel_Webhook
    Docker -- "Tail file /var/lib/docker/..." --> OTel_gRPC

    %% Processing & Storage
    OTel_HTTP & OTel_gRPC & OTel_Webhook -- "Batch & Export" --> ClickHouse
    
    %% Querying
    QueryService -- "SQL Queries" --> ClickHouse
    SigNozUI -- "API Requests" --> QueryService
    
    %% Grafana Integration
    GrafanaUI -. "ClickHouse Plugin" .-> ClickHouse
```

---

## 2. Chi tiết thư mục `/signoz`

Thư mục này chứa core engine của hệ thống giám sát. Thay vì xài Datadog tốn phí, bạn đang host một hệ thống mạnh tương đương.

- **`docker-compose.yaml`**: Chứa toàn bộ các service của SigNoz (Zookeeper, Clickhouse, Query Service, Frontend, OTel Collector).
- **`otel-collector-config.yaml`**: Đây là **bộ não** định tuyến dữ liệu. Nó định nghĩa:
  - `receivers`: Các cổng mở ra để đón dữ liệu (ví dụ: gRPC `4317` cho backend, HTTP `4318` cho Next.js, Webhook `19418` cho GitHub). Nó cũng chủ động đọc file log của Docker (`filelog/containers`).
  - `processors`: Xử lý, nhào nặn dữ liệu (ví dụ: gán thêm thẻ `service.name: github-actions` cho data từ GitHub, lọc các log rác).
  - `exporters`: Đẩy toàn bộ dữ liệu đã xử lý vào ClickHouse để lưu trữ tối ưu.
- **ClickHouse**: Database dạng cột (Columnar Database) cực kỳ tối ưu cho việc đọc/ghi log và time-series data tốc độ cao.

## 3. Chi tiết thư mục `/grafana`

Dù SigNoz đã rất mạnh, Grafana vẫn được giữ lại để phục vụ các biểu đồ tùy biến phức tạp (Custom Dashboards) hoặc khi cần monitor các metric hạ tầng truyền thống.

- **`docker-compose.yaml`**: Dựng Grafana độc lập.
- **`provisioning/datasources/`**: Cấu hình tự động kết nối Grafana vào ClickHouse hoặc Prometheus của SigNoz. Nhờ vậy Grafana có thể lấy chung một nguồn dữ liệu với SigNoz.
- **`dashboards/`**: Thư mục chứa các file JSON (như `Web Vitals Monitoring (1).json`). Grafana sẽ tự động load các file này lên UI mà không cần bạn phải import bằng tay.

## 4. Sự tương hỗ giữa SigNoz và Grafana

- **SigNoz**: Dùng làm công cụ **Troubleshooting & APM** chính. Khi App sập hoặc API chậm, bạn vào SigNoz xem Flamegraph (Traces) để biết chính xác hàm nào trong code chạy chậm. Bạn cũng xem Log trực tiếp tại đây.
- **Grafana**: Dùng làm công cụ **Executive Dashboard**. Hiển thị các biểu đồ tổng quan về Business (số lượng user, tài nguyên VPS tổng thể) lên màn hình lớn hoặc chia sẻ cho team không chuyên về kỹ thuật xem.
