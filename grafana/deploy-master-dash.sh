#!/bin/bash
# Deploy Master Navigation Dashboard to Grafana
GRAFANA_URL="http://localhost:3000"
GRAFANA_USER="admin"
GRAFANA_PASS="KidoOps2026!"

echo "→ Deploying Master Home Dashboard..."
curl -s -X POST "$GRAFANA_URL/api/dashboards/db" \
  -u "$GRAFANA_USER:$GRAFANA_PASS" \
  -H "Content-Type: application/json" \
  -d '{
  "overwrite": true,
  "dashboard": {
    "id": null,
    "uid": "master-navigation",
    "title": "🏠 Kido Master Center",
    "tags": ["master", "home"],
    "timezone": "browser",
    "schemaVersion": 38,
    "panels": [
      {
        "type": "dashlist",
        "title": "🗂️ Danh sách Dashboards hệ thống",
        "gridPos": { "x": 0, "y": 0, "w": 14, "h": 14 },
        "options": {
          "keepTime": false,
          "showStarred": true,
          "showRecentlyViewed": true,
          "showSearch": true,
          "showHeadings": true,
          "maxItems": 20,
          "query": "",
          "tags": []
        }
      },
      {
        "type": "text",
        "title": "💡 Ý tưởng cho Super Overview Dashboard",
        "gridPos": { "x": 14, "y": 0, "w": 10, "h": 14 },
        "options": {
          "mode": "markdown",
          "content": "### Gợi ý Brainstorm\nThay vì phải bấm vào List bên trái để đi xem từng bảng, ta có thể xây dựng một bảng gộp duy nhất. Dưới đây là các ứng cử viên cần cân nhắc thả vào:\n\n1. **Khối Hạ Tầng (Node Exporter):** CPU / RAM / Disk Usage chung của toàn bộ máy chủ VPS.\n2. **Khối Ứng Dụng (Loki/Scraper):** Góc hiển thị Log lỗi `[FATAL EXCEPTION]` để biết khi nào tool cào bị hỏng.\n3. **Khối Cơ Sở Dữ Liệu (TimescaleDB):** Số lượng kết nối (Connections) hoặc tình trạng rỗng kho dữ liệu.\n4. **Khối Docker (Telegraf/cAdvisor):** Top 3 container đang ngốn RAM nhiều nhất (như con grafana hoặc postgres).\n\n*Chúng ta sẽ lược bỏ những biểu đồ rườm rà (network I/O, paging, inode...) và chỉ đưa vào số liệu sống còn.*"
        }
      }
    ]
  }
}' | python3 -c "import sys,json; r=json.load(sys.stdin); print('Dashboard:', r.get('status','?'), r.get('url',''))"
