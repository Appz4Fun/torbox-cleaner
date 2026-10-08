"""Minimal TorBox API client (stdlib only).

Docs: https://api-docs.torbox.app/
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

BASE_URL = "https://api.torbox.app/v1/api"
PAGE_SIZE = 1000


@dataclass(frozen=True)
class Kind:
    """One category of cloud item and the endpoints that manage it."""

    key: str
    label: str
    list_path: str
    control_path: str
    id_field: str


KINDS: dict[str, Kind] = {
    "torrents": Kind("torrents", "torrent", "torrents/mylist", "torrents/controltorrent", "torrent_id"),
    "usenet": Kind("usenet", "usenet", "usenet/mylist", "usenet/controlusenetdownload", "usenet_id"),
    "webdl": Kind("webdl", "webdl", "webdl/mylist", "webdl/controlwebdownload", "webdl_id"),
}


@dataclass(frozen=True)
class Item:
    kind: Kind
    id: int
    name: str
    size: int


class TorBoxError(RuntimeError):
    pass


class TorBoxClient:
    def __init__(self, api_key: str, base_url: str = BASE_URL, timeout: float = 60.0, max_retries: int = 5):
        if not api_key:
            raise TorBoxError("TORBOX_API_KEY is empty")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

    def _request(self, method: str, path: str, *, query: dict | None = None, body: dict | None = None):
        url = f"{self.base_url}/{path}"
        if query:
            url += "?" + urllib.parse.urlencode(query)
        data = json.dumps(body).encode() if body is not None else None
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "User-Agent": "torbox-cleaner/0.1",
        }
        if data is not None:
            headers["Content-Type"] = "application/json"

        for attempt in range(self.max_retries + 1):
            req = urllib.request.Request(url, data=data, method=method, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    payload = json.load(resp)
            except urllib.error.HTTPError as e:
                # Back off on rate limiting and transient server errors.
                if e.code in (429, 500, 502, 503, 504) and attempt < self.max_retries:
                    retry_after = e.headers.get("Retry-After")
                    time.sleep(float(retry_after) if retry_after and retry_after.isdigit() else 2 ** attempt)
                    continue
                try:
                    detail = json.load(e).get("detail")
                except Exception:
                    detail = e.reason
                raise TorBoxError(f"{method} {path} failed: HTTP {e.code}: {detail}") from None
            except urllib.error.URLError as e:
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)
                    continue
                raise TorBoxError(f"{method} {path} failed: {e.reason}") from None

            if not payload.get("success"):
                raise TorBoxError(f"{method} {path} failed: {payload.get('error')}: {payload.get('detail')}")
            return payload.get("data")
        raise TorBoxError(f"{method} {path} failed after {self.max_retries} retries")

    def list_items(self, kind: Kind) -> list[Item]:
        items: list[Item] = []
        offset = 0
        while True:
            page = self._request(
                "GET",
                kind.list_path,
                query={"bypass_cache": "true", "offset": offset, "limit": PAGE_SIZE},
            ) or []
            for raw in page:
                items.append(Item(kind, int(raw["id"]), raw.get("name") or "", int(raw.get("size") or 0)))
            if len(page) < PAGE_SIZE:
                return items
            offset += PAGE_SIZE

    def delete_item(self, item: Item) -> None:
        self._request(
            "POST",
            item.kind.control_path,
            body={item.kind.id_field: item.id, "operation": "delete"},
        )
