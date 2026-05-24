#!/bin/bash
set -u

PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
APP_NAME="com.ifsherlock.dockercopilot"
APP_PORT="12712"
CGI_BASE="/cgi/ThirdParty/${APP_NAME}/index.cgi"
BACKEND_BASE="http://127.0.0.1:${APP_PORT}"
LOG_FILE="/tmp/dockercopilot_cgi.log"

URI_NO_QUERY="${REQUEST_URI%%\?*}"
REL_PATH="/"
case "$URI_NO_QUERY" in
  *index.cgi*)
    REL_PATH="${URI_NO_QUERY#*index.cgi}"
    ;;
esac

if [ -z "$REL_PATH" ]; then
  REL_PATH="/"
fi
case "$REL_PATH" in
  /*) ;;
  *) REL_PATH="/${REL_PATH}" ;;
esac

TARGET_URL="${BACKEND_BASE}${REL_PATH}"
if [ -n "${QUERY_STRING:-}" ]; then
  TARGET_URL="${TARGET_URL}?${QUERY_STRING}"
fi

{
  echo "[$(date '+%F %T')] method=${REQUEST_METHOD:-GET} uri=${REQUEST_URI:-} rel=${REL_PATH} target=${TARGET_URL} host=${HTTP_HOST:-${SERVER_NAME:-}}"
} >> "$LOG_FILE" 2>&1 || true

HEADER_FILE=$(mktemp /tmp/dockercopilot-cgi-header.XXXXXX)
BODY_FILE=$(mktemp /tmp/dockercopilot-cgi-body.XXXXXX)
OUT_FILE=""
cleanup() {
  rm -f "$HEADER_FILE" "$BODY_FILE" "$OUT_FILE"
}
trap cleanup EXIT

curl_args=(
  -sS
  -L
  -D "$HEADER_FILE"
  -o "$BODY_FILE"
  -X "${REQUEST_METHOD:-GET}"
  -H "Host: ${HTTP_HOST:-127.0.0.1:${APP_PORT}}"
  -H "X-Forwarded-Host: ${HTTP_HOST:-${SERVER_NAME:-127.0.0.1}}"
  -H "X-Forwarded-Proto: ${REQUEST_SCHEME:-http}"
  -H "X-Forwarded-Prefix: ${CGI_BASE}"
  -H "X-Original-URI: ${REQUEST_URI:-}"
  "$TARGET_URL"
)

[ -n "${HTTP_ACCEPT:-}" ] && curl_args+=( -H "Accept: ${HTTP_ACCEPT}" )
[ -n "${HTTP_ACCEPT_LANGUAGE:-}" ] && curl_args+=( -H "Accept-Language: ${HTTP_ACCEPT_LANGUAGE}" )
[ -n "${HTTP_USER_AGENT:-}" ] && curl_args+=( -H "User-Agent: ${HTTP_USER_AGENT}" )
[ -n "${HTTP_COOKIE:-}" ] && curl_args+=( -H "Cookie: ${HTTP_COOKIE}" )
[ -n "${HTTP_AUTHORIZATION:-}" ] && curl_args+=( -H "Authorization: ${HTTP_AUTHORIZATION}" )
[ -n "${CONTENT_TYPE:-}" ] && curl_args+=( -H "Content-Type: ${CONTENT_TYPE}" )

case "${REQUEST_METHOD:-GET}" in
  GET|HEAD)
    ;;
  *)
    curl_args+=( --data-binary @- )
    ;;
esac

if ! curl "${curl_args[@]}" >> "$LOG_FILE" 2>&1; then
  echo "Status: 502 Bad Gateway"
  echo "Content-Type: text/plain; charset=utf-8"
  echo
  echo "CGI proxy failed: ${TARGET_URL}"
  exit 0
fi

STATUS_LINE=$(head -n 1 "$HEADER_FILE" | tr -d '\r')
STATUS_CODE=$(printf '%s\n' "$STATUS_LINE" | awk '{print $2}')
STATUS_TEXT=$(printf '%s\n' "$STATUS_LINE" | cut -d' ' -f3-)
CONTENT_TYPE=$(awk 'BEGIN{IGNORECASE=1} /^Content-Type:/ {sub(/\r$/, ""); print substr($0,15); exit}' "$HEADER_FILE")

rewrite_text_response() {
  local src="$1"
  local dst="$2"
  sed \
    -e "s|\"/assets/|\"${CGI_BASE}/assets/|g" \
    -e "s|'/assets/|'${CGI_BASE}/assets/|g" \
    -e "s|url(/assets/|url(${CGI_BASE}/assets/|g" \
    -e "s|\"/api/|\"${CGI_BASE}/api/|g" \
    -e "s|'/api/|'${CGI_BASE}/api/|g" \
    -e "s|\"/logo.png\"|\"${CGI_BASE}/logo.png\"|g" \
    -e "s|'/logo.png'|'${CGI_BASE}/logo.png'|g" \
    -e "s|\"/manifest.json\"|\"${CGI_BASE}/manifest.json\"|g" \
    -e "s|'/manifest.json'|'${CGI_BASE}/manifest.json'|g" \
    -e "s|\"/sw.js\"|\"${CGI_BASE}/sw.js\"|g" \
    -e "s|'/sw.js'|'${CGI_BASE}/sw.js'|g" \
    -e "s|\"/m\"|\"${CGI_BASE}/m\"|g" \
    -e "s|'/m'|'${CGI_BASE}/m'|g" \
    -e "s|\"/manager\"|\"${CGI_BASE}/manager\"|g" \
    -e "s|'/manager'|'${CGI_BASE}/manager'|g" \
    "$src" > "$dst"
}

if [ "${REQUEST_METHOD:-GET}" != "HEAD" ]; then
  case "$CONTENT_TYPE" in
    text/html*|application/javascript*|text/javascript*|text/css*|application/json*|text/plain*)
      OUT_FILE=$(mktemp /tmp/dockercopilot-cgi-out.XXXXXX)
      rewrite_text_response "$BODY_FILE" "$OUT_FILE"
      if printf '%s' "$CONTENT_TYPE" | grep -qi '^text/html'; then
        TMP_FILE=$(mktemp /tmp/dockercopilot-cgi-html.XXXXXX)
        sed "s|</head>|  <script>window.__API_BASE_URL='${CGI_BASE}'; window.__CGI_BASE_URL='${CGI_BASE}';</script></head>|" "$OUT_FILE" > "$TMP_FILE"
        mv -f "$TMP_FILE" "$OUT_FILE"
      fi
      ;;
  esac
fi

[ -n "$STATUS_CODE" ] || STATUS_CODE=200

echo "Status: ${STATUS_CODE} ${STATUS_TEXT}"
while IFS= read -r line; do
  line="${line%$'\r'}"
  [ -z "$line" ] && break
  case "$line" in
    HTTP/*)
      continue
      ;;
    [Cc]ontent-[Ll]ength:*|[Tt]ransfer-[Ee]ncoding:*|[Cc]onnection:*|[Kk]eep-[Aa]live:*|[Cc]ontent-[Ee]ncoding:*)
      continue
      ;;
    [Ll]ocation:*)
      location_value="${line#*: }"
      case "$location_value" in
        http://127.0.0.1:${APP_PORT}/*)
          location_value="${CGI_BASE}${location_value#http://127.0.0.1:${APP_PORT}}"
          ;;
        /*)
          location_value="${CGI_BASE}${location_value}"
          ;;
      esac
      echo "Location: ${location_value}"
      ;;
    *)
      echo "$line"
      ;;
  esac
done < "$HEADER_FILE"
echo

if [ "${REQUEST_METHOD:-GET}" != "HEAD" ]; then
  if [ -n "$OUT_FILE" ] && [ -f "$OUT_FILE" ]; then
    cat "$OUT_FILE"
  else
    cat "$BODY_FILE"
  fi
fi
