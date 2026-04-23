# P2P Tracker Infrastructure Architecture

Tài liệu này mô tả toàn cảnh kiến trúc Monitoring (Giám sát) và Database (Cơ sở dữ liệu) của hệ thống **P2P Tracker** trên VPS Contabo.

Hệ thống được thiết kế theo chuẩn **Micro-segmentation (Zero-Trust)** giữa các cụm Docker Compose, đảm bảo các dịch vụ giám sát nội bộ không cần mở IP Public mà vẫn tương tác mượt mà với các Database cốt lõi.

---

## 🗺 Sơ đồ Kiến trúc Tổng quan (Mermaid)

```mermaid
graph TD
    %% Define styles
    classDef vps fill:#2d3436,stroke:#b2bec3,stroke-width:2px,color:#fff
    classDef monitor fill:#0984e3,stroke:#74b9ff,stroke-width:2px,color:#fff
    classDef db fill:#00b894,stroke:#55efc4,stroke-width:2px,color:#fff
    classDef scraper fill:#d63031,stroke:#fab1a0,stroke-width:2px,color:#fff
    classDef external fill:#fdcb6e,stroke:#ffeaa7,stroke-width:2px,color:#2d3436

    subgraph VPS["💻 VPS Contabo (144.91.88.242)"]

        subgraph NetOpsBridge["🔒 Docker Network: ops_bridge (Internal Network)"]

            subgraph MonStack["📊 Monitoring Stack (/opt/monitoring)"]
                Grafana["📈 Grafana (UI) :3000"]
                Prometheus["🔭 Prometheus :9090"]
                Loki["📓 Loki (Logs)"]
                AlertManager["🚨 AlertManager"]

                subgraph Exporters["📡 Scrapers & Exporters"]
                    NodeExp["🖥️ Node Exporter"]
                    PgExp["🐘 Postgres Exporter"]
                    RedisExp["🔴 Redis Exporter"]
                    Promtail["🦊 Promtail"]
                    Telegraf["🐳 Telegraf (Docker)"]
                end
            end

            subgraph DBStack["💾 Core Databases"]
                TimescaleDB[("🐘 TimescaleDB (pg16)\n/root/timescaledb\nExt: 5433 | Int: 5432")]
                Redis[("🔴 Redis\n/opt/services\nExt: 6379 | Int: 6379")]
                PgVector[("🐘 Postgres (pgvector)\n/opt/services\nExt: 5432")]
            end
        end

        subgraph ScraperStack["⚙️ Scraper Stack (/root/deploy/p2p-tracker)"]
            P2PWorker["⚡ p2p-worker (Node.js)"]
        end
    end

    subgraph External["🌐 External Clients"]
        Admin["🧑‍💻 Admin / DevOps"]
        VercelOS["▲ Vercel (Next.js Edge Functions)"]
        LocalDev["🏠 Local Machine (bun start)"]
    end

    %% External Connections
    Admin -->|":3000"| Grafana
    VercelOS -->|":5433"| TimescaleDB
    LocalDev -->|":5433"| TimescaleDB

    %% Monitoring connections inside bridge
    Grafana -->|Query Metrics| Prometheus
    Grafana -->|Query Logs| Loki
    Grafana -->|Query SQL| TimescaleDB

    Prometheus -->|Scrape Metrics| NodeExp
    Prometheus -->|Scrape Database| PgExp
    Prometheus -->|Scrape Cache| RedisExp
    Prometheus -->|Scrape Containers| Telegraf

    PgExp -.->|Read Stats| TimescaleDB
    RedisExp -.->|Read Stats| Redis

    Promtail -.->|Watch Docker Logs| Loki

    P2PWorker -->|Write Ticks| TimescaleDB
    P2PWorker -->|Cache| Redis

    %% Assign classes
    class VPS vps
    class Grafana,Prometheus,Loki,AlertManager,NodeExp,PgExp,RedisExp,Promtail,Telegraf monitor
    class TimescaleDB,Redis,PgVector db
    class P2PWorker scraper
    class Admin,VercelOS,LocalDev external
```

---

## 🧩 Giải phẫu các thành phần cốt lõi

### 1. Mạng ảo `ops_bridge` (Zero-Trust)

Thay vì để các cụm Docker Compose nằm riêng rẽ khép kín, hệ thống sử dụng một mạng nội bộ chung có tên là `ops_bridge`.

- **Bảo mật**: Các công cụ như Grafana, Postgres-exporter có thể "nhìn thấy" và truy vấn thẳng vào TimescaleDB qua hostname nội bộ (ví dụ: `timescaledb:5432` hoặc `redis:6379`) hoàn toàn ẩn danh, không cần đi vòng ra IP Public.
- **Tối ưu Network**: Giảm tải cho tường lửa (iptables) và băng thông public.

### 2. Cụm Giám sát (`/opt/monitoring`)

- **Grafana**: Dashboard trung tâm, hiển thị Metric, Log và Tracing SQL.
- **Prometheus**: Não bộ lưu trữ Metric (Time-series), 15 giây lấy dữ liệu từ các Exporter 1 lần.
- **Loki & Promtail**: Promtail giám sát thư mục `/var/lib/docker/containers` để hốt toàn bộ log của tất cả các container trên VPS và đẩy về Loki. Grafana sẽ dùng Loki để query log.
- **Telegraf**: Chuyên gia soi RAM và CPU thời gian thực cho từng container (bằng cách móc vào `docker.sock` và `/host/proc`).
- **AlertManager**: Đẩy cảnh báo về Telegram/Slack khi CPU quá tải (có rule Z-Score quét Anomaly).

### 3. Cụm Databases

Được tách riêng rẽ để đảm bảo độc lập dữ liệu:

- **TimescaleDB (`/root/timescaledb`)**: Lưu trữ giá xăng, giá vàng, ngoại tệ dạng chuỗi thời gian (Time-series). Mở port `5433` ra ngoài cho Next.js/Vercel.
- **Redis (`/opt/services`)**: Môi trường cache siêu tốc.
- **PGVector (`/opt/services`)**: Database chuyên dùng để lưu trữ Vector Embeddings cho AI News, RAG.
