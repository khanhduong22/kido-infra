# SigNoz Alert Notification Channels

## Trạng thái hiện tại
- **Grafana alerts**: đã config gửi cả Slack + Telegram ✅
- **SigNoz alerts**: cần config thủ công qua UI

## SigNoz — Thêm Telegram Notification Channel

1. Vào **https://signoz.khanhdp.com**
2. Login: `khanhdev4@gmail.com`
3. **Settings** → **Notification Channels** → **+ New Channel**
4. Type: **Telegram**
5. Nhập:
   - Bot Token: _(liên hệ admin)_
   - Chat ID: `807207301`
6. Click **Test** → verify nhận tin nhắn
7. **Save**

## Grafana Alert Contacts

Truy cập: **https://grafana.khanhdp.com** → Alerting → Contact points

| Channel | Type | UID | Status |
|---------|------|-----|--------|
| Slack Kido | Slack | dficjsab92ltsf | ✅ Active |
| Telegram Khánh | Telegram | cfk60s68xcjr4e | ✅ Active |

### Notification Policy
Mọi alert gửi đến **cả 2 channels**:
- Route 1: Slack Kido
- Route 2: Telegram Khánh (continue: true)

## Alert Rules

| Alert | Condition | Channels |
|-------|-----------|----------|
| [🔥 KHẨN CẤP] Đầy ổ cứng VPS! | Disk > 77GB | Slack + Telegram |

## Thêm alert mới (Grafana)

1. Alerting → Alert rules → + New alert rule
2. Đặt query (ClickHouse data source: `afk5t1ojwwbuod`)
3. Set threshold
4. Notification → chọn existing contact points

## Lưu ý
- SigNoz API không gọi được qua curl (SPA intercept mọi request)
- Phải config SigNoz notification channels qua UI
- Grafana API hoạt động bình thường (curl + basic auth)
