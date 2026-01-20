"""
Minimal SSE smoke test.

Usage:
  python backend/scripts/sse_smoke_test.py \
    --url http://localhost:8000/api/v1/conversations/<conversation_id>/messages \
    --token <JWT> \
    --message "hello"

This prints received SSE events and exits when it sees [DONE].
"""

import argparse
import json
import sys
import time
from typing import Optional

import requests


def _iter_sse_lines(resp: requests.Response):
    # Stream raw bytes and decode as UTF-8 incrementally.
    for raw in resp.iter_lines(decode_unicode=True):
        # requests yields lines without trailing newline
        if raw is None:
            continue
        yield raw


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True, help="SSE POST endpoint URL")
    p.add_argument("--token", required=True, help="Bearer token")
    p.add_argument("--message", required=True, help="User message content")
    p.add_argument("--timeout", type=int, default=900, help="Request timeout seconds")
    args = p.parse_args()

    headers = {
        "Authorization": f"Bearer {args.token}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
        "Cache-Control": "no-cache",
    }
    body = {"content": args.message, "message": args.message}

    started = time.time()
    with requests.post(args.url, headers=headers, json=body, stream=True, timeout=args.timeout) as resp:
        print("status:", resp.status_code)
        if resp.status_code != 200:
            print(resp.text)
            return 2

        buffer_data: Optional[str] = None
        for line in _iter_sse_lines(resp):
            if not line:
                # event boundary
                buffer_data = None
                continue

            if line.startswith(":"):
                # keep-alive comment
                continue

            if not line.startswith("data:"):
                continue

            data = line[5:].lstrip()
            if data == "[DONE]":
                print("[DONE]")
                return 0

            # Pretty print JSON if possible
            if data.startswith("{"):
                try:
                    print(json.loads(data))
                    continue
                except Exception:
                    pass

            print(data)

    elapsed = time.time() - started
    print(f"stream ended without [DONE] after {elapsed:.1f}s", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())


