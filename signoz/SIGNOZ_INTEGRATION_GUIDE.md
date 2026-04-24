# Hướng Dẫn Tích Hợp SigNoz (Observability Best Practices)

Tài liệu này tổng hợp các kinh nghiệm xương máu và best practices để setup giám sát (Observability) bằng SigNoz cho các dự án mới, đảm bảo ăn ngay 100% từ Frontend Web Vitals đến CI/CD Pipeline.

---

## 1. Giám Sát Frontend Web Vitals (Next.js / React)

**⚠️ Vấn đề thường gặp:** Mọi người thường dùng Tracer (`@opentelemetry/sdk-trace-web`) để gửi Web Vitals dưới dạng Spans. Tuy nhiên, Dashboard chuẩn của SigNoz lại đọc dữ liệu từ **Metrics** (cụ thể là các biểu đồ Histogram như `lcp.bucket`, `fcp.bucket`). Nếu gửi dạng Trace, Dashboard sẽ báo `No Data`.

**✅ Giải pháp:** Bắt buộc phải sử dụng `MeterProvider` và đẩy dữ liệu dưới dạng Histogram Metrics.

### Bước 1: Cài đặt thư viện cần thiết
```bash
npm install @opentelemetry/sdk-metrics @opentelemetry/exporter-metrics-otlp-http @opentelemetry/semantic-conventions
```

### Bước 2: Setup MeterProvider ở Frontend
Tạo file `WebVitals.tsx` (dùng cho Next.js App Router):
```tsx
'use client';

import { useEffect } from 'react';
import { useReportWebVitals } from 'next/web-vitals';
import { MeterProvider, PeriodicExportingMetricReader } from '@opentelemetry/sdk-metrics';
import { OTLPMetricExporter } from '@opentelemetry/exporter-metrics-otlp-http';
import { resourceFromAttributes } from '@opentelemetry/resources';
import { ATTR_SERVICE_NAME } from '@opentelemetry/semantic-conventions';

let isInstrumented = false;
let histograms: Record<string, any> = {};

export default function WebVitals() {
  useEffect(() => {
    if (typeof window !== 'undefined' && !isInstrumented) {
      isInstrumented = true;

      const metricExporter = new OTLPMetricExporter({
        // Trỏ về API Route nội bộ để giấu Token
        url: '/api/vitals?type=metrics', 
      });

      const meterProvider = new MeterProvider({
        resource: resourceFromAttributes({
          [ATTR_SERVICE_NAME]: 'your-frontend-service-name',
        }),
      });

      meterProvider.addMetricReader(new PeriodicExportingMetricReader({
        exporter: metricExporter,
        exportIntervalMillis: 10000,
      }));

      const meter = meterProvider.getMeter('next-web-vitals');
      
      // Tạo Histograms chuẩn cho SigNoz
      histograms = {
        FCP: meter.createHistogram('fcp', { description: 'First Contentful Paint', unit: 'ms' }),
        LCP: meter.createHistogram('lcp', { description: 'Largest Contentful Paint', unit: 'ms' }),
        CLS: meter.createHistogram('cls', { description: 'Cumulative Layout Shift' }),
        INP: meter.createHistogram('inp', { description: 'Interaction to Next Paint', unit: 'ms' }),
        TTFB: meter.createHistogram('ttfb', { description: 'Time To First Byte', unit: 'ms' }),
      };
    }
  }, []);

  useReportWebVitals((metric) => {
    if (isInstrumented && histograms[metric.name]) {
      histograms[metric.name].record(metric.value, {
        'web_vital.id': metric.id,
        'web_vital.rating': metric.rating || 'unknown',
      });
    }
  });

  return null;
}
```

### Bước 3: Tạo API Route Proxy ẩn Token
Tạo file `app/api/vitals/route.ts` (để tránh lộ `Authorization Token` trên browser):
```typescript
import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const body = await req.arrayBuffer();
    const type = req.nextUrl.searchParams.get('type');
    
    // Phân luồng: traces hoặc metrics
    const endpointSuffix = type === 'metrics' ? '/v1/metrics' : '/v1/traces';
    const otelEndpoint = `https://otel.your-domain.com${endpointSuffix}`;

    const res = await fetch(otelEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': req.headers.get('content-type') || 'application/json',
        Authorization: 'Bearer YOUR_SUPER_SECRET_TOKEN',
      },
      body,
    });

    return new NextResponse('OK', { status: 200 });
  } catch (error) {
    return new NextResponse('Internal Server Error', { status: 500 });
  }
}
```

---

## 2. Giám Sát CI/CD (GitHub Actions)

**⚠️ Vấn đề thường gặp:** Các Action có sẵn trên Github Marketplace (như `inception-health/otel-export-trace-action`) thường chứa bug ngầm (lỗi khi quét artifacts của Node 20) khiến Pipeline crash thất bại. Ngoài ra, dashboard CI/CD của SigNoz yêu cầu bắt buộc các thẻ Tag cụ thể (`repository.name`, `job.status`) mới hiển thị được dữ liệu.

**✅ Giải pháp:** Dùng trực tiếp binary `otel-cli` để gửi trace chuẩn nhất, nhanh nhất và không bao giờ lỗi vặt.

Thêm đoạn script sau vào cuối cùng của mọi file `.github/workflows/deploy.yml`:
```yaml
      - name: Install otel-cli
        if: always() # Chạy kể cả khi build lỗi
        run: curl -sL https://github.com/equinix-labs/otel-cli/releases/download/v0.4.4/otel-cli_0.4.4_linux_amd64.tar.gz | tar xz otel-cli

      - name: Send CI/CD Trace to SigNoz
        if: always()
        run: |
          # 0 là OK, 2 là Error
          STATUS_CODE=$([ "${{ job.status }}" = "success" ] && echo 0 || echo 2)
          
          # Lưu ý: Bắt buộc truyền repository.name thì Dashboard CI/CD mới nhận
          ./otel-cli span --service "github-actions" --name "Deploy Your App Name" \
            --attrs "job.status=${{ job.status }},repository.name=${{ github.repository }},github.run_id=${{ github.run_id }}" \
            --endpoint "https://otel.your-domain.com" \
            --protocol "http/protobuf" \
            --status-code "$STATUS_CODE" \
            --otlp-headers "Authorization=Bearer YOUR_SUPER_SECRET_TOKEN"
```
*(Chú ý cờ `--otlp-headers` thay vì `--header` ở các phiên bản cũ).*

---

## 3. Cấu Hình Endpoint SigNoz Collector

**Rule of Thumb:**
- Port mặc định nhận tín hiệu OTLP/HTTP trên SigNoz Collector là `4318`.
- Nginx hoặc Cloudflare proxy tới `4318` thì ở endpoint bắn lên chỉ cần khai báo `https://otel.your-domain.com` (các SDK sẽ tự động nối đuôi `/v1/traces` hoặc `/v1/metrics`).
- Nếu dùng Proxy thủ công (như Next.js API Route) sử dụng hàm `fetch()`, bắt buộc phải gõ đầy đủ đuôi `/v1/traces` hoặc `/v1/metrics` vào URL.
