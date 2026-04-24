#!/bin/bash
# Ganti placeholder ngrok URL sebelum push ke repo
# Usage: bash inject_ngrok.sh https://abc123.ngrok-free.app

NGROK_URL="${1:-}"

if [ -z "$NGROK_URL" ]; then
    # Auto-detect dari ngrok API jika sedang berjalan
    NGROK_URL=$(curl -s http://127.0.0.1:4040/api/tunnels 2>/dev/null | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    for t in d.get('tunnels', []):
        if t.get('proto') == 'https':
            print(t['public_url'])
            break
except: pass
")
fi

if [ -z "$NGROK_URL" ]; then
    echo "Usage: bash inject_ngrok.sh https://YOUR_NGROK_URL"
    echo "       OR start ngrok first and run without arguments"
    exit 1
fi

# Strip trailing slash
NGROK_URL="${NGROK_URL%/}"

echo "[*] Injecting: $NGROK_URL"
sed -i "s|https://YOUR_NGROK_DOMAIN|$NGROK_URL|g" .vscode/settings.json
echo "[+] Done. .vscode/settings.json updated:"
grep otlpEndpoint .vscode/settings.json
