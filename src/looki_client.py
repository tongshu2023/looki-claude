#!/usr/bin/env python3
"""
Looki L1 API Client — 零依赖(只用 Python 标准库)

用法:
    python looki_client.py me
    python looki_client.py moments 2026-04-20
    python looki_client.py search "薄荷" --page-size 20
    python looki_client.py calendar 2026-03-22 2026-04-21
    python looki_client.py files <moment_id>
    python looki_client.py for-you --group comic --limit 20

作为库使用:
    from looki_client import LookiClient
    c = LookiClient()
    me = c.me()
    moments = c.moments_on_date("2026-04-20")
    hits = c.search("薄荷", page_size=20)
"""

import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

# Windows 控制台默认 GBK,会把中文打成乱码。强制 UTF-8。
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


class LookiError(Exception):
    pass


class LookiClient:
    DEFAULT_BASE = "https://open.looki.tech/api/v1"
    CRED_PATH = Path.home() / ".looki" / "credentials.json"

    def __init__(self, api_key: str = None, base_url: str = None):
        if api_key is None or base_url is None:
            cred = self._load_credentials()
            api_key = api_key or cred.get("api_key") or os.environ.get("LOOKI_API_KEY")
            base_url = base_url or cred.get("base_url") or os.environ.get(
                "LOOKI_BASE_URL", self.DEFAULT_BASE
            )
        if not api_key:
            raise LookiError(
                "未找到 API Key。请跑 setup 脚本或设置 LOOKI_API_KEY 环境变量。"
            )
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    @classmethod
    def _load_credentials(cls) -> dict:
        if cls.CRED_PATH.exists():
            return json.loads(cls.CRED_PATH.read_text(encoding="utf-8"))
        return {}

    def _request(self, path: str, params: dict = None) -> dict:
        url = f"{self.base_url}{path}"
        if params:
            clean = {k: v for k, v in params.items() if v is not None}
            url += "?" + urllib.parse.urlencode(clean)
        req = urllib.request.Request(url, headers={"x-api-key": self.api_key})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore")
            if e.code == 429:
                raise LookiError(f"限流 (60 req/min)。响应: {body}")
            raise LookiError(f"HTTP {e.code}: {body}")
        except urllib.error.URLError as e:
            raise LookiError(f"网络错误: {e.reason}")

    # ---- 7 个端点 ----

    def me(self) -> dict:
        return self._request("/me")

    def moments_on_date(self, date: str) -> dict:
        """date 格式 YYYY-MM-DD"""
        return self._request("/moments", {"on_date": date})

    def search(
        self,
        query: str,
        start_date: str = None,
        end_date: str = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        return self._request(
            "/moments/search",
            {
                "query": query,
                "start_date": start_date,
                "end_date": end_date,
                "page": page,
                "page_size": page_size,
            },
        )

    def calendar(self, start_date: str, end_date: str) -> dict:
        return self._request(
            "/moments/calendar",
            {"start_date": start_date, "end_date": end_date},
        )

    def moment_detail(self, moment_id: str) -> dict:
        return self._request(f"/moments/{moment_id}")

    def moment_files(
        self,
        moment_id: str,
        highlight: bool = None,
        cursor_id: str = None,
        limit: int = 20,
    ) -> dict:
        return self._request(
            f"/moments/{moment_id}/files",
            {"highlight": highlight, "cursor_id": cursor_id, "limit": limit},
        )

    def for_you(
        self,
        group: str = None,
        liked: bool = None,
        recorded_from: str = None,
        recorded_to: str = None,
        cursor_id: str = None,
        limit: int = 20,
        order_by: str = None,
    ) -> dict:
        return self._request(
            "/for_you/items",
            {
                "group": group,
                "liked": liked,
                "recorded_from": recorded_from,
                "recorded_to": recorded_to,
                "cursor_id": cursor_id,
                "limit": limit,
                "order_by": order_by,
            },
        )


# ---- CLI ----

def _print_json(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    c = LookiClient()
    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "me":
        _print_json(c.me())
    elif cmd == "moments":
        if not args:
            sys.exit("用法: moments <YYYY-MM-DD>")
        _print_json(c.moments_on_date(args[0]))
    elif cmd == "search":
        if not args:
            sys.exit("用法: search <query> [--page-size N]")
        query = args[0]
        page_size = 20
        if "--page-size" in args:
            page_size = int(args[args.index("--page-size") + 1])
        _print_json(c.search(query, page_size=page_size))
    elif cmd == "calendar":
        if len(args) < 2:
            sys.exit("用法: calendar <start_date> <end_date>")
        _print_json(c.calendar(args[0], args[1]))
    elif cmd == "detail":
        if not args:
            sys.exit("用法: detail <moment_id>")
        _print_json(c.moment_detail(args[0]))
    elif cmd == "files":
        if not args:
            sys.exit("用法: files <moment_id>")
        _print_json(c.moment_files(args[0]))
    elif cmd == "for-you":
        group = None
        limit = 20
        if "--group" in args:
            group = args[args.index("--group") + 1]
        if "--limit" in args:
            limit = int(args[args.index("--limit") + 1])
        _print_json(c.for_you(group=group, limit=limit))
    else:
        sys.exit(f"未知命令: {cmd}")


if __name__ == "__main__":
    main()
