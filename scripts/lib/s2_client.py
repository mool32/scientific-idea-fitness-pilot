"""Minimal Semantic Scholar API client. Stdlib only.

S2 Graph API endpoints used:
- POST /graph/v1/paper/batch — bulk lookup, up to 500 IDs per call.
  Body: {"ids": ["ARXIV:2401.12345", ...]}
  Query: ?fields=citationCount,publicationDate,...

Rate limits:
- Unauthenticated: 1 request / second (per docs); empirically tighter, expect 429s.
- Authenticated (x-api-key header): 1 req / sec for /paper/batch (per docs).
- Recommendation: register at semanticscholar.org/product/api for higher quotas.

Set S2_API_KEY env var to use authenticated rate.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Iterable

from .config import S2_API_BASE


class S2Error(Exception):
    pass


class S2Client:
    def __init__(
        self,
        api_key: str | None = None,
        rate_limit_seconds: float = 1.05,
        max_retries: int = 5,
    ) -> None:
        self.api_key = api_key or os.environ.get("S2_API_KEY")
        self.rate_limit = rate_limit_seconds
        self.max_retries = max_retries
        self._last_request_time: float = 0.0

    def _wait(self) -> None:
        elapsed = time.monotonic() - self._last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)

    def _request(self, url: str, body: dict | None) -> dict | list:
        backoff = 2.0
        last_err: Exception | None = None
        for attempt in range(self.max_retries):
            self._wait()
            data = json.dumps(body).encode("utf-8") if body is not None else None
            headers = {"User-Agent": "scientific-idea-fitness-pilot/0.1 (research)"}
            if data is not None:
                headers["Content-Type"] = "application/json"
            if self.api_key:
                headers["x-api-key"] = self.api_key
            req = urllib.request.Request(url, data=data, headers=headers, method="POST" if data else "GET")
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    self._last_request_time = time.monotonic()
                    return json.loads(resp.read())
            except urllib.error.HTTPError as e:
                self._last_request_time = time.monotonic()
                if e.code == 429:
                    last_err = e
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                # Read body for diagnostics; don't retry 4xx other than 429.
                try:
                    err_body = e.read().decode("utf-8", errors="replace")[:500]
                except Exception:
                    err_body = ""
                raise S2Error(f"HTTP {e.code} {e.reason}: {err_body}") from e
            except urllib.error.URLError as e:
                last_err = e
                time.sleep(backoff)
                backoff *= 2
        raise S2Error(f"max retries exceeded: {last_err}")

    def batch_papers(
        self,
        ids: list[str],
        fields: list[str],
    ) -> list[dict | None]:
        """Look up papers by ID. ids is e.g. ["ARXIV:2401.12345", ...] (max 500).

        Returns list aligned with input order; None for IDs not found by S2.
        """
        if len(ids) > 500:
            raise ValueError("S2 batch endpoint max is 500 ids per call")
        url = f"{S2_API_BASE}/paper/batch?fields={','.join(fields)}"
        result = self._request(url, body={"ids": ids})
        if not isinstance(result, list):
            raise S2Error(f"unexpected batch response shape: {type(result).__name__}")
        return result

    def batch_papers_chunked(
        self,
        ids: Iterable[str],
        fields: list[str],
        chunk_size: int = 500,
    ) -> Iterable[tuple[str, dict | None]]:
        """Yield (id, paper-or-None) pairs, transparently batching."""
        buf: list[str] = []
        for sid in ids:
            buf.append(sid)
            if len(buf) >= chunk_size:
                results = self.batch_papers(buf, fields)
                yield from zip(buf, results)
                buf = []
        if buf:
            results = self.batch_papers(buf, fields)
            yield from zip(buf, results)
