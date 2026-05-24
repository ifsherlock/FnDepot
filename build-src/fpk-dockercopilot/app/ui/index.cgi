#!/bin/bash
set -u

PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
LOG_FILE="/tmp/dockercopilot_cgi.log"
APP_PORT="12712"

{
  echo "[$(date '+%F %T')] start REQUEST_URI=${REQUEST_URI:-} HTTP_HOST=${HTTP_HOST:-} SERVER_NAME=${SERVER_NAME:-}"
} >> "$LOG_FILE" 2>&1 || true

cat <<'EOF'
Content-Type: text/html; charset=utf-8
Cache-Control: no-store

<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Docker Copilot</title>
  <style>
    html, body { margin: 0; padding: 0; width: 100%; height: 100%; background: #0f172a; color: #e5e7eb; font-family: sans-serif; }
    #status { position: fixed; inset: 0; display: flex; align-items: center; justify-content: center; text-align: center; white-space: pre-wrap; padding: 24px; box-sizing: border-box; background: #0f172a; z-index: 2; }
    #app { width: 100%; height: 100%; border: 0; display: block; background: #fff; }
    #hint { margin-top: 12px; font-size: 14px; opacity: 0.85; }
    a { color: #93c5fd; }
  </style>
</head>
<body>
  <div id="status">
    <div>
      <div id="main">CGI 已执行，正在计算目标地址…</div>
      <div id="hint"></div>
    </div>
  </div>
  <iframe id="app"></iframe>
  <script>
    (function () {
      var statusEl = document.getElementById('status');
      var mainEl = document.getElementById('main');
      var hintEl = document.getElementById('hint');
      var frame = document.getElementById('app');

      var host = window.location.hostname || '127.0.0.1';
      var pageProtocol = window.location.protocol || 'http:';
      var target = 'http://' + host + ':12712/manager';

      mainEl.textContent = 'CGI 已执行，正在加载：' + target;
      if (pageProtocol === 'https:') {
        hintEl.textContent = '当前页面是 HTTPS，目标是 HTTP 端口，浏览器可能因混合内容策略拒绝内嵌。';
      }

      console.log('[dockercopilot-cgi] page protocol =', pageProtocol);
      console.log('[dockercopilot-cgi] target =', target);

      frame.onload = function () {
        console.log('[dockercopilot-cgi] iframe loaded');
        statusEl.style.display = 'none';
      };

      frame.onerror = function () {
        console.error('[dockercopilot-cgi] iframe load error');
        hintEl.innerHTML = 'iframe 加载失败，请直接访问：<a href="' + target + '" target="_blank" rel="noreferrer">' + target + '</a>';
      };

      frame.src = target;

      setTimeout(function () {
        if (statusEl.style.display !== 'none') {
          hintEl.innerHTML = '仍未完成加载。请查看 F12 Console / Network。<br>当前页面协议：' + pageProtocol + '<br>目标地址：<a href="' + target + '" target="_blank" rel="noreferrer">' + target + '</a>';
        }
      }, 8000);
    })();
  </script>
</body>
</html>
EOF
