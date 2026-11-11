#!/bin/bash
# 用途：通过 file_presigned_url 下载 MOMA Space 文件
# 用法：PRESIGNED_URL=<url> FILEPATH=<相对路径> bash download_file.sh
# 兼容用法：FILEPATH=<相对路径> SPACE_ROOT=<space_root> TASK_ID=<task_id> bash download_file.sh
# Step 1 优先 curl，失败时执行 Step 2 urllib
set -euo pipefail

FILEPATH="${FILEPATH:-docs/report.pdf}"
SPACE_ROOT="${SPACE_ROOT:-<SPACE_root>}"
TASK_ID="${TASK_ID:-<TASK>}"
PRESIGNED_URL="${PRESIGNED_URL:-}"
RESP=""

mkdir -p /tmp/.moma-tmp
TMP_FILE="/tmp/.moma-tmp/$(basename "$FILEPATH")"

# 未从外部传入 URL 时，兼容旧用法：由脚本调用 presigned_url API。
if [[ -z "$PRESIGNED_URL" ]]; then
  RESP=$(moma moma-space api POST_api_v1_tools_file_presigned_url --json --data "$(
    jq -n \
      --arg fp "$FILEPATH" \
      --arg space "$SPACE_ROOT" \
      --arg task "$TASK_ID" \
      '{filepath:$fp, space_root:$space, task_id:$task}'
  )")
  PRESIGNED_URL=$(echo "$RESP" | jq -r '.url')
fi

URL="$PRESIGNED_URL"

if [[ -z "$URL" || "$URL" == "null" ]]; then
  echo "ERROR: presigned url is empty or null, resp=$RESP"
  exit 1
fi

# Step 1：curl 下载
if curl -sSfL -o "$TMP_FILE" "$URL"; then
  echo "Downloaded via curl: $TMP_FILE"
  ls -la "$TMP_FILE"
  exit 0
fi

# Step 2：curl 失败，fallback 到 urllib
echo "curl failed, falling back to urllib..."
PRESIGNED_URL="$URL" TMP_FILE="$TMP_FILE" python3 -c "
import os, urllib.request
url = os.environ['PRESIGNED_URL']
out = os.environ['TMP_FILE']
with urllib.request.urlopen(url) as r:
    data = r.read()
with open(out, 'wb') as f:
    f.write(data)
print(f'Saved {len(data)} bytes to {out}')
"
ls -la "$TMP_FILE"
