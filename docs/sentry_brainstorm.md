# Brainstorming: Sentry vs SigNoz & Deployment Strategy

## 1. Tại sao lại dùng Sentry khi đã có SigNoz?

Dự án hiện tại (`ty-gia/market-scraper`) đang dùng `@opentelemetry/sdk-node` để đẩy log/trace về **SigNoz**. Vậy Sentry giải quyết bài toán gì mà SigNoz chưa làm tốt?

*   **SigNoz (OpenTelemetry):** Rất mạnh về **Tracing** (theo dõi luồng request mất bao lâu, chậm ở query DB nào) và **Logging** (thu thập log tập trung). Tuy nhiên, giao diện báo lỗi (Error Tracking) chưa được tối ưu cho việc debug nhanh.
*   **Sentry:** Sinh ra để làm **Error Tracking** (Bắt lỗi). Sentry tự động nhóm các lỗi giống nhau (Issue Fingerprinting), tự bắt unhandled exceptions, tự gom "Breadcrumbs" (các sự kiện xảy ra ngay trước khi lỗi như click, HTTP request, query DB). 
*   **Kết luận:** Sentry và SigNoz **bổ trợ** cho nhau. SigNoz dùng để giám sát Performance (APM/Trace) & Log hệ thống. Sentry dùng để nhận cảnh báo khi App Crash hoặc văng Exception, giúp Dev fix bug nhanh nhất.

## 2. Bài toán Self-hosted Sentry trong `kido-infra`

Official Sentry (`getsentry/self-hosted`) cực kỳ nặng. Nó chạy khoảng 30+ containers (Kafka, ClickHouse, Postgres, Redis, Snuba, Relay, v.v.). Nếu VPS của anh có cấu hình `< 16GB RAM`, việc chạy chung Sentry và SigNoz gần như chắc chắn sẽ gây quá tải (OOM - Out of Memory).

### Giải pháp thay thế: GlitchTip (Lightweight Sentry)
Thay vì cài Sentry chính chủ, chúng ta có thể dùng **GlitchTip**. 
*   **GlitchTip** là một open-source API-compatible backend của Sentry.
*   Chỉ cần 2 thành phần cơ bản: **PostgreSQL** và **Redis**.
*   Vẫn sử dụng SDK chính chủ `@sentry/node` hoặc `@sentry/nextjs` dưới client/backend. App vẫn tưởng là đang gọi lên Sentry thật.
*   Rất nhẹ, phù hợp chạy chung trên VPS đang host `kido-infra`.

---

## 3. Áp dụng thử vào `ty-gia` (market-scraper)

**Quy trình:**
1. Em sẽ tạo sẵn một file `docker-compose.yml` cho **GlitchTip** trong thư mục `kido-infra/sentry-glitchtip` để anh có thể spin-up Sentry server nội bộ rất nhẹ.
2. Cài đặt SDK `@sentry/node` vào thư mục `/Users/kido/ty-gia/market-scraper`.
3. Tích hợp Sentry vào file khởi tạo (`src/instrumentation.js` hoặc `src/app.js`) của Fastify, thiết lập DSN trỏ về server GlitchTip (hoặc Sentry SaaS nếu anh dùng bản Cloud).

Anh xem code apply ở dưới nhé!
