import json
import os
import sys
import urllib.request

KEY = os.environ.get("XAI_API_KEY", "").strip()
if not KEY:
    print("NO_KEY", file=sys.stderr)
    sys.exit(2)

prompt_path = sys.argv[1]
out_json = sys.argv[2]
prompt = open(prompt_path, encoding="utf-8").read().strip()

body = {
    "model": "grok-imagine-image-2.0",
    "prompt": prompt,
    "n": 1,
    "aspect_ratio": "16:9",
    "resolution": "2k",
    "quality": "medium",
    "response_format": "url",
}
req = urllib.request.Request(
    "https://api.x.ai/v1/images/generations",
    data=json.dumps(body).encode("utf-8"),
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {KEY}",
    },
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=180) as resp:
        raw = resp.read()
        code = resp.status
except urllib.error.HTTPError as e:
    raw = e.read()
    code = e.code

open(out_json, "wb").write(raw)
print(f"HTTP {code}")
print(raw[:4000].decode("utf-8", "replace"))
if code >= 400:
    sys.exit(1)
