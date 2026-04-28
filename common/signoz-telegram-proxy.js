const http = require('http');

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const CHAT_ID = process.env.TELEGRAM_CHAT_ID;
const PORT = 9200;

function sendTelegram(text) {
  const data = JSON.stringify({ chat_id: CHAT_ID, text, parse_mode: 'HTML' });
  const options = {
    hostname: 'api.telegram.org',
    path: `/bot${BOT_TOKEN}/sendMessage`,
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Content-Length': data.length }
  };
  const req = require('https').request(options, (res) => {
    let body = '';
    res.on('data', (c) => body += c);
    res.on('end', () => console.log(`Telegram response: ${res.statusCode} ${body.substring(0, 100)}`));
  });
  req.on('error', (e) => console.error(`Telegram error: ${e.message}`));
  req.write(data);
  req.end();
}

function formatAlert(payload) {
  try {
    // SigNoz alert format
    const alerts = payload.alerts || [payload];
    const lines = [];
    for (const alert of alerts) {
      const status = alert.status === 'firing' ? '🔴' : '✅';
      const name = alert.labels?.alertname || alert.name || 'Alert';
      const severity = alert.labels?.severity || '';
      const summary = alert.annotations?.summary || alert.description || alert.message || JSON.stringify(alert).substring(0, 200);
      lines.push(`${status} <b>${name}</b>${severity ? ` [${severity}]` : ''}\n${summary}`);
    }
    return lines.join('\n\n') || JSON.stringify(payload).substring(0, 500);
  } catch (e) {
    return JSON.stringify(payload).substring(0, 500);
  }
}

const server = http.createServer((req, res) => {
  if (req.method === 'GET' && req.url === '/health') {
    res.writeHead(200);
    return res.end('ok');
  }
  if (req.method !== 'POST') {
    res.writeHead(405);
    return res.end('method not allowed');
  }
  let body = '';
  req.on('data', (c) => body += c);
  req.on('end', () => {
    console.log(`Received: ${body.substring(0, 200)}`);
    try {
      const payload = JSON.parse(body);
      const text = formatAlert(payload);
      sendTelegram(text);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ ok: true }));
    } catch (e) {
      // Even if parse fails, try to forward raw text
      sendTelegram(body.substring(0, 500));
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ ok: true }));
    }
  });
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`SigNoz→Telegram proxy listening on :${PORT}`);
});
