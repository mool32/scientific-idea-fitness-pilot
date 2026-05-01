"""Minimal arXiv API client. Stdlib only.

arXiv API behavior worth knowing:
- Documented courtesy: ≥3 seconds between requests.
- Single query max_results capped at 2000; pagination via `start`.
- `submittedDate:[YYYYMMDDHHMM TO YYYYMMDDHHMM]` filters by v1 submission.
- Sort by `submittedDate ascending` keeps pagination stable across days.
- Atom XML response.
"""

from __future__ import annotations

import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Iterator

from .config import ARXIV_API_BASE, ARXIV_PAGE_SIZE, ARXIV_RATE_LIMIT_SECONDS

ATOM_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}


@dataclass
class ArxivPaper:
    arxiv_id: str  # e.g. "2401.12345v1"
    arxiv_id_base: str  # e.g. "2401.12345" (no version)
    title: str
    abstract: str
    submitted_date: str  # ISO date string YYYY-MM-DD of v1 submission
    updated_date: str
    primary_category: str
    categories: list[str]
    authors: list[str]
    doi: str | None
    journal_ref: str | None
    pdf_url: str | None

    def to_dict(self) -> dict:
        return {
            "arxiv_id": self.arxiv_id,
            "arxiv_id_base": self.arxiv_id_base,
            "title": self.title,
            "abstract": self.abstract,
            "submitted_date": self.submitted_date,
            "updated_date": self.updated_date,
            "primary_category": self.primary_category,
            "categories": self.categories,
            "authors": self.authors,
            "doi": self.doi,
            "journal_ref": self.journal_ref,
            "pdf_url": self.pdf_url,
        }


class ArxivClient:
    def __init__(self, rate_limit_seconds: float = ARXIV_RATE_LIMIT_SECONDS) -> None:
        self.rate_limit = rate_limit_seconds
        self._last_request_time: float = 0.0

    def _wait(self) -> None:
        elapsed = time.monotonic() - self._last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)

    def _fetch(self, params: dict[str, str]) -> bytes:
        self._wait()
        url = f"{ARXIV_API_BASE}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": "scientific-idea-fitness-pilot/0.1 (research)"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        self._last_request_time = time.monotonic()
        return data

    def search(
        self,
        category: str,
        date_from: str,  # YYYY-MM-DD
        date_to: str,  # YYYY-MM-DD
        page_size: int = ARXIV_PAGE_SIZE,
        max_results: int | None = None,
    ) -> Iterator[ArxivPaper]:
        """Stream papers in `category` submitted in [date_from, date_to] inclusive.

        Pagination: arXiv returns up to page_size per request; we step `start` until
        an empty page or `max_results` reached.
        """
        # arXiv date format: YYYYMMDDHHMM
        df = date_from.replace("-", "") + "0000"
        dt = date_to.replace("-", "") + "2359"
        query = f"cat:{category} AND submittedDate:[{df} TO {dt}]"
        start = 0
        yielded = 0
        consecutive_empty = 0
        while True:
            params = {
                "search_query": query,
                "start": str(start),
                "max_results": str(page_size),
                "sortBy": "submittedDate",
                "sortOrder": "ascending",
            }
            xml_bytes = self._fetch(params)
            root = ET.fromstring(xml_bytes)
            entries = root.findall("atom:entry", ATOM_NS)
            if not entries:
                consecutive_empty += 1
                # arXiv occasionally returns transient empty pages; allow one retry.
                if consecutive_empty >= 2:
                    return
                continue
            consecutive_empty = 0
            for entry in entries:
                paper = _parse_entry(entry)
                if paper is None:
                    continue
                yield paper
                yielded += 1
                if max_results is not None and yielded >= max_results:
                    return
            start += page_size


def _parse_entry(entry: ET.Element) -> ArxivPaper | None:
    id_el = entry.find("atom:id", ATOM_NS)
    if id_el is None or not id_el.text:
        return None
    # id is full URL like "http://arxiv.org/abs/2401.12345v2"
    raw_id = id_el.text.rsplit("/", 1)[-1]
    if "v" in raw_id:
        base = raw_id.rsplit("v", 1)[0]
    else:
        base = raw_id
    title_el = entry.find("atom:title", ATOM_NS)
    summary_el = entry.find("atom:summary", ATOM_NS)
    published_el = entry.find("atom:published", ATOM_NS)
    updated_el = entry.find("atom:updated", ATOM_NS)
    primary_cat_el = entry.find("arxiv:primary_category", ATOM_NS)
    cats = [c.attrib["term"] for c in entry.findall("atom:category", ATOM_NS) if "term" in c.attrib]
    authors = [
        (a.findtext("atom:name", default="", namespaces=ATOM_NS) or "").strip()
        for a in entry.findall("atom:author", ATOM_NS)
    ]
    doi_el = entry.find("arxiv:doi", ATOM_NS)
    journal_el = entry.find("arxiv:journal_ref", ATOM_NS)
    pdf_url = None
    for link in entry.findall("atom:link", ATOM_NS):
        if link.attrib.get("title") == "pdf":
            pdf_url = link.attrib.get("href")
            break
    return ArxivPaper(
        arxiv_id=raw_id,
        arxiv_id_base=base,
        title=(title_el.text or "").strip().replace("\n ", " ") if title_el is not None else "",
        abstract=(summary_el.text or "").strip().replace("\n", " ") if summary_el is not None else "",
        submitted_date=(published_el.text or "")[:10] if published_el is not None else "",
        updated_date=(updated_el.text or "")[:10] if updated_el is not None else "",
        primary_category=primary_cat_el.attrib.get("term", "") if primary_cat_el is not None else "",
        categories=cats,
        authors=[a for a in authors if a],
        doi=doi_el.text.strip() if (doi_el is not None and doi_el.text) else None,
        journal_ref=journal_el.text.strip() if (journal_el is not None and journal_el.text) else None,
        pdf_url=pdf_url,
    )
