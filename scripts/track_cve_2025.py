#!/usr/bin/env python3
"""
Hardened CVE-2025 article tracker.

- Uses environment variables for secrets (no hardcoded API keys).
- Provides a fallback GitHub PAT placeholder as requested: "<-yourGitHubPatToken->"
- Safe request handling with timeout + retries.
- Atomic writes for JSON + README.
- Idempotent README update using explicit markers.
- Sanitizes all external text to prevent HTML or Markdown injection.
"""

import os
import sys
import time
import json
import logging
import tempfile
import requests
import re
import html
from datetime import datetime
from typing import List, Dict, Any, Optional

# ---------------- Configuration ----------------
# Provide real values via environment variables when running:
# export GOOGLE_CSE_API_KEY="..."
# export GOOGLE_CSE_ID="..."
# export GH_TOKEN="..."  # optional; fallback placeholder used below

GOOGLE_API_KEY = os.getenv("GOOGLE_CSE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
# Per your request, include placeholder fallback for GitHub PAT
GH_TOKEN = os.getenv("GH_TOKEN", "<-yourGitHubPatToken->")

OUTPUT_FILE = os.getenv("OUTPUT_FILE", "cve_2025_articles.json")
README_FILE = os.getenv("README_FILE", "README.md")  # prefer repo-root README.md
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_BACKOFF = float(os.getenv("RETRY_BACKOFF", "2"))  # exponential
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "15"))
USER_AGENT = "cve-2025-tracker/1.0 (+https://github.com/your/repo)"

# HEADERS for README section markers (idempotent updates)
README_SECTION_START = "<!-- CVE-SUMMARY-START -->"
README_SECTION_END = "<!-- CVE-SUMMARY-END -->"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
    logging.error("Missing Google CSE credentials. Set GOOGLE_CSE_API_KEY and GOOGLE_CSE_ID in environment.")
    # do not sys.exit here if you want to allow dry-run; but normally we need keys
    # sys.exit(1)

KEYWORDS = [
    "CVE-2025",
    "zero-day",
    "0day",
    "\"exploited in the wild\"",
    "\"known exploited\"",
    "victims",
    "affected"
]

CVE_RE = re.compile(r"(CVE-\d{4}-\d{4,7})", re.IGNORECASE)


# ---------------- Helper functions ----------------
def safe_request(url: str, params: dict, retries: int = MAX_RETRIES) -> Optional[dict]:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    attempt = 0
    while attempt < retries:
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 200:
                try:
                    return resp.json()
                except ValueError:
                    logging.warning("Response not valid JSON.")
                    return None
            elif resp.status_code in (429, 503):
                wait = (RETRY_BACKOFF ** attempt)
                logging.warning("Rate limited/service unavailable (status %s). Backing off %ss.", resp.status_code, wait)
                time.sleep(wait)
            else:
                logging.error("HTTP %s: %s", resp.status_code, resp.text[:500])
                return None
        except requests.RequestException as e:
            logging.warning("Request exception: %s. Retrying... (%d/%d)", e, attempt + 1, retries)
            time.sleep(RETRY_BACKOFF ** attempt)
        attempt += 1
    logging.error("Exceeded retries for URL: %s", url)
    return None


def extract_cve(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    m = CVE_RE.search(text)
    return m.group(1).upper() if m else None


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    if not date_str:
        return None
    s = date_str.strip()
    # Try isoformat
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        pass
    # Try common formats
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            continue
    m = re.search(r"(\d{4}-\d{2}-\d{2})", s)
    if m:
        try:
            return datetime.strptime(m.group(1), "%Y-%m-%d")
        except Exception:
            pass
    return None


def remove_html_tags(text: str) -> str:
    # Basic removal of HTML tags
    return re.sub(r"<[^>]*>", "", text)


def sanitize_for_markdown(text: Optional[str], maxlen: int = 500) -> str:
    """
    Sanitize incoming text so it cannot inject HTML/JS via README:
    - Remove HTML tags
    - Escape HTML entities
    - Replace pipe '|' with HTML entity &#124; to avoid breaking markdown tables
    - Replace backticks and other potentially problematic characters
    - Truncate to maxlen
    """
    if not text:
        return ""
    t = str(text)
    t = remove_html_tags(t)                 # strip tags
    t = html.escape(t, quote=True)          # convert <,>,&,"
    # Replace pipe with entity so it won't break table columns
    t = t.replace("|", "&#124;")
    # Replace backticks with HTML entity
    t = t.replace("`", "&#96;")
    # Remove control characters
    t = re.sub(r"[\x00-\x1f\x7f]", "", t)
    # Shorten overly long snippets
    if len(t) > maxlen:
        t = t[:maxlen].rstrip() + "…"
    return t


def atomic_write_file(path: str, data: str, encoding: str = "utf-8"):
    dirn = os.path.dirname(path) or "."
    with tempfile.NamedTemporaryFile("w", delete=False, dir=dirn, encoding=encoding) as tmp:
        tmp.write(data)
        temp_name = tmp.name
    os.replace(temp_name, path)
    logging.info("Atomically wrote file: %s", path)


# ---------------- Core logic ----------------
def fetch_articles(keywords: List[str]) -> List[Dict[str, Any]]:
    base_url = "https://www.googleapis.com/customsearch/v1"
    results = []
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        logging.error("Google CSE credentials not set. fetch_articles will return empty list.")
        return results

    for q in keywords:
        params = {"q": q, "key": GOOGLE_API_KEY, "cx": GOOGLE_CSE_ID}
        logging.info("Querying CSE for: %s", q)
        data = safe_request(base_url, params)
        if not data:
            continue
        items = data.get("items", [])
        for it in items:
            title = it.get("title") or ""
            link = it.get("link") or ""
            snippet = it.get("snippet") or ""
            pub = None
            # Try to get publish date from common places
            pagemap = it.get("pagemap", {})
            if isinstance(pagemap, dict):
                metatags = pagemap.get("metatags")
                if isinstance(metatags, list) and metatags:
                    meta0 = metatags[0]
                    pub = meta0.get("article:published_time") or meta0.get("og:published_time") or meta0.get("date")
            pub = pub or it.get("published") or it.get("isoDate") or None
            results.append({
                "title": title,
                "link": link,
                "snippet": snippet,
                "publish_date_raw": pub,
                "raw": it
            })
        # polite sleep to reduce rate risk
        time.sleep(1.0)
    return results


def summarize_articles(articles: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    summary: Dict[str, Dict[str, Any]] = {}
    for art in articles:
        combined = " ".join(filter(None, [art.get("title"), art.get("snippet")]))
        cve = extract_cve(combined)
        if not cve:
            continue
        if cve not in summary:
            summary[cve] = {"article_count": 0, "first_observed_date": None, "victims": set()}
        summary[cve]["article_count"] += 1

        # Parse publish date
        pub_dt = parse_date(art.get("publish_date_raw"))
        if pub_dt:
            cur = summary[cve]["first_observed_date"]
            if cur is None or pub_dt < cur:
                summary[cve]["first_observed_date"] = pub_dt

        # Basic victim detection and store snippet truncated
        snippet = (art.get("snippet") or "").lower()
        if any(key in snippet for key in ("victim", "affected", "compromised", "ransom")):
            snippet_short = (art.get("snippet") or "")[:400]
            summary[cve]["victims"].add(snippet_short)

    # Convert to safe serializable structure and sanitize text
    out: Dict[str, Dict[str, Any]] = {}
    for cve, data in summary.items():
        victims_list = [sanitize_for_markdown(v, maxlen=500) for v in data["victims"]]
        out[cve] = {
            "article_count": data["article_count"],
            "first_observed_date": data["first_observed_date"].isoformat() if data["first_observed_date"] else None,
            "victims": victims_list
        }
    return out


def write_articles_json(path: str, data: List[Dict[str, Any]]):
    # Strip raw bulky fields and sanitize a compact version for storage/publication
    slim = []
    for it in data:
        slim.append({
            "title": sanitize_for_markdown(it.get("title") or ""),
            "link": it.get("link") or "",
            "snippet": sanitize_for_markdown(it.get("snippet") or ""),
            "publish_date_raw": it.get("publish_date_raw")
        })
    atomic_write_file(path, json.dumps(slim, indent=2, ensure_ascii=False))


def update_readme_section(readme_path: str, summary: Dict[str, Dict[str, Any]]):
    """
    Idempotently update README between markers.
    If markers do not exist, append the full section at the end.
    """
    # Build markdown table safely (cells sanitized already)
    lines = []
    lines.append(README_SECTION_START)
    lines.append("")
    lines.append("## CVE Summary for 2025")
    lines.append("")
    lines.append("| CVE ID | Article Count | First Observed Date | Victims Mentioned |")
    lines.append("|--------|---------------|---------------------|-------------------|")
    for cve, d in sorted(summary.items()):
        victims = " ; ".join(d.get("victims", [])) or "N/A"
        first_date = d.get("first_observed_date") or "N/A"
        # Cells are already sanitized but ensure no newlines
        victims = victims.replace("\n", " ").strip()
        line = f"| {cve} | {d.get('article_count',0)} | {first_date} | {victims} |"
        lines.append(line)
    lines.append("")
    lines.append(README_SECTION_END)
    new_section = "\n".join(lines) + "\n"

    existing = ""
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            existing = f.read()

    if README_SECTION_START in existing and README_SECTION_END in existing:
        # Replace existing section (between markers)
        pattern = re.compile(
            re.escape(README_SECTION_START) + r".*?" + re.escape(README_SECTION_END),
            flags=re.DOTALL
        )
        updated = pattern.sub(new_section.strip(), existing)
        # Ensure newline termination
        if not updated.endswith("\n"):
            updated += "\n"
        atomic_write_file(readme_path, updated)
        logging.info("Replaced existing README CVE section.")
    else:
        # Append the section
        appended = existing + ("\n" if existing and not existing.endswith("\n") else "") + new_section
        atomic_write_file(readme_path, appended)
        logging.info("Appended new README CVE section.")


def main():
    articles = fetch_articles(KEYWORDS)
    logging.info("Fetched %d articles", len(articles))

    summary = summarize_articles(articles)
    logging.info("Summarized %d CVEs", len(summary))

    # Write sanitized JSON output
    try:
        write_articles_json(OUTPUT_FILE, articles)
    except Exception as e:
        logging.error("Failed to write articles JSON: %s", e)

    # Update README idempotently and safely
    try:
        update_readme_section(README_FILE, summary)
    except Exception as e:
        logging.error("Failed to update README: %s", e)


if __name__ == "__main__":
    main()
