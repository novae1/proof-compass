#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
import time
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

import requests


SPACE_BASE_URL = "https://delta-lab-ai-lean-finder.hf.space"
CALL_ENDPOINT = f"{SPACE_BASE_URL}/gradio_api/call/retrieve"
DEFAULT_CACHE_PATH = (
    Path(__file__).resolve().parents[2] / "outputs" / "cache" / "leanfinder_query_cache.json"
)


class LeanFinderParseError(RuntimeError):
    pass


class LeanFinderRequestError(RuntimeError):
    pass


def _extract_name_from_formal(formal_statement: str) -> str | None:
    first_line = formal_statement.strip().splitlines()[0] if formal_statement.strip() else ""
    match = re.match(
        r"^(theorem|lemma|def|abbrev|axiom|class|structure|instance)\s+([^\s:{\[]+)",
        first_line,
    )
    if match:
        return match.group(2)
    return None


class _ResultTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.results: list[dict[str, Any]] = []
        self._current_row: dict[str, Any] | None = None
        self._td_index = 0
        self._capture_formal = False
        self._capture_informal = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag == "tr":
            self._current_row = {
                "rank": None,
                "formal_parts": [],
                "informal_parts": [],
                "doc_url": None,
                "full_name": None,
            }
            self._td_index = 0
            return

        if self._current_row is None:
            return

        if tag == "td":
            self._td_index += 1
            return

        if tag == "code" and self._td_index == 2:
            self._capture_formal = True
            return

        if tag == "span" and self._td_index == 3:
            self._capture_informal = True
            return

        if tag == "button" and self._td_index == 2:
            onclick = attrs_dict.get("onclick") or ""
            css_class = attrs_dict.get("class") or ""
            if "doc-button" in css_class:
                match = re.search(r"window\.open\('([^']+)'", onclick)
                if match:
                    url = html.unescape(match.group(1))
                    self._current_row["doc_url"] = url
                    self._current_row["full_name"] = _extract_full_name(url)

    def handle_endtag(self, tag: str) -> None:
        if tag == "code":
            self._capture_formal = False
            return
        if tag == "span":
            self._capture_informal = False
            return
        if tag == "tr" and self._current_row is not None:
            formal = "".join(self._current_row["formal_parts"]).strip()
            informal = "".join(self._current_row["informal_parts"]).strip()
            if formal:
                parsed_name = _extract_name_from_formal(formal)
                self.results.append(
                    {
                        "rank": self._current_row["rank"],
                        "formal_statement": formal,
                        "informal_statement": informal,
                        "doc_url": self._current_row["doc_url"],
                        "full_name": parsed_name or self._current_row["full_name"],
                    }
                )
            self._current_row = None
            self._td_index = 0
            self._capture_formal = False
            self._capture_informal = False

    def handle_data(self, data: str) -> None:
        if self._current_row is None:
            return
        if self._td_index == 1 and self._current_row["rank"] is None:
            text = data.strip()
            if text.isdigit():
                self._current_row["rank"] = int(text)
        if self._capture_formal:
            self._current_row["formal_parts"].append(data)
        elif self._capture_informal:
            self._current_row["informal_parts"].append(data)


def _extract_full_name(doc_url: str | None) -> str | None:
    if not doc_url:
        return None
    parsed = urlparse(doc_url)
    query = parse_qs(parsed.query)
    patterns = query.get("pattern")
    if patterns:
        return patterns[0]
    return None


def _load_cache(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _save_cache(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _cache_key(query: str, k: int) -> str:
    return json.dumps({"query": query, "k": k}, ensure_ascii=False, sort_keys=True)


def _extract_complete_payload(response: requests.Response) -> list[Any]:
    event_name: str | None = None
    data_payload: str | None = None
    for raw_line in response.iter_lines(decode_unicode=True):
        if raw_line is None:
            continue
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("event:"):
            event_name = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            data_payload = line.split(":", 1)[1].strip()
            if event_name == "complete":
                try:
                    parsed = json.loads(data_payload)
                except json.JSONDecodeError as exc:
                    raise LeanFinderParseError("Could not decode LeanFinder completion payload.") from exc
                if not isinstance(parsed, list):
                    raise LeanFinderParseError("LeanFinder completion payload was not a list.")
                return parsed
    raise LeanFinderParseError("Did not receive a complete payload from LeanFinder.")


def _parse_results_html(results_html: str) -> list[dict[str, Any]]:
    parser = _ResultTableParser()
    parser.feed(results_html)
    parser.close()
    if not parser.results:
        raise LeanFinderParseError("Could not parse any theorem rows from LeanFinder HTML.")
    return parser.results


class LeanFinderClient:
    def __init__(
        self,
        *,
        cache_path: Path | None = DEFAULT_CACHE_PATH,
        timeout_s: float = 60.0,
        max_attempts: int = 3,
        backoff_s: float = 2.0,
    ) -> None:
        self.cache_path = cache_path
        self.timeout_s = timeout_s
        self.max_attempts = max_attempts
        self.backoff_s = backoff_s
        self._cache = _load_cache(cache_path) if cache_path else {}

    def retrieve(self, query: str, *, k: int = 5, use_cache: bool = True) -> list[dict[str, Any]]:
        query = query.strip()
        if not query:
            raise ValueError("Query must be non-empty.")
        if k < 1:
            raise ValueError("k must be at least 1.")

        key = _cache_key(query, k)
        if use_cache and key in self._cache:
            cached = self._cache[key]
            results = cached.get("results")
            if isinstance(results, list):
                return results

        payload = {"data": [query, k, "Normal"]}
        last_error: Exception | None = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                event_id = self._start_request(payload)
                results = self._read_results(event_id)
                if use_cache and self.cache_path:
                    self._cache[key] = {
                        "query": query,
                        "k": k,
                        "fetched_at": int(time.time()),
                        "results": results,
                    }
                    _save_cache(self.cache_path, self._cache)
                return results
            except (requests.RequestException, LeanFinderParseError, LeanFinderRequestError) as exc:
                last_error = exc
                if attempt < self.max_attempts:
                    time.sleep(self.backoff_s * attempt)
                continue

        raise LeanFinderRequestError(f"LeanFinder request failed after {self.max_attempts} attempts: {last_error}")

    def _start_request(self, payload: dict[str, Any]) -> str:
        response = requests.post(CALL_ENDPOINT, json=payload, timeout=self.timeout_s)
        response.raise_for_status()
        body = response.json()
        event_id = body.get("event_id")
        if not isinstance(event_id, str) or not event_id:
            raise LeanFinderRequestError("LeanFinder did not return an event_id.")
        return event_id

    def _read_results(self, event_id: str) -> list[dict[str, Any]]:
        stream_url = f"{CALL_ENDPOINT}/{event_id}"
        with requests.get(stream_url, stream=True, timeout=self.timeout_s) as response:
            response.raise_for_status()
            payload = _extract_complete_payload(response)
        if not payload:
            raise LeanFinderParseError("LeanFinder completion payload was empty.")
        results_html = payload[0]
        if not isinstance(results_html, str) or not results_html.strip():
            raise LeanFinderParseError("LeanFinder completion payload did not contain HTML results.")
        return _parse_results_html(results_html)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query the public LeanFinder Space and parse results.")
    parser.add_argument("--query", required=True, help="LeanFinder query text.")
    parser.add_argument("--k", type=int, default=5, help="Number of results to request.")
    parser.add_argument("--no-cache", action="store_true", help="Disable on-disk caching.")
    parser.add_argument("--cache-path", type=Path, default=DEFAULT_CACHE_PATH)
    parser.add_argument("--json", action="store_true", help="Print full parsed JSON instead of a brief summary.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    client = LeanFinderClient(cache_path=None if args.no_cache else args.cache_path)
    results = client.retrieve(args.query, k=args.k, use_cache=not args.no_cache)

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return 0

    print(f"query: {args.query}")
    print(f"results: {len(results)}")
    for result in results:
        rank = result.get("rank")
        full_name = result.get("full_name") or "<unknown>"
        formal = result.get("formal_statement", "").splitlines()[0]
        print(f"[{rank}] {full_name}")
        print(f"    {formal}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
