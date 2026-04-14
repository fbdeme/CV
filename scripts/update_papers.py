#!/usr/bin/env python3
"""
Fetch latest publications from Semantic Scholar and merge with existing data.
Preserves manually-added entries (source: "manual" or "google_scholar").
"""

import json
import time
import urllib.request
import urllib.error
from pathlib import Path

AUTHOR_ID = "2387416140"
API_BASE = "https://api.semanticscholar.org/graph/v1"
FIELDS = "title,year,venue,authors,externalIds,url,citationCount,abstract,publicationDate"
DATA_FILE = Path(__file__).parent.parent / "data" / "publications.json"


def fetch_papers():
    """Fetch all papers for the author from Semantic Scholar."""
    url = f"{API_BASE}/author/{AUTHOR_ID}/papers?fields={FIELDS}&limit=100"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "MingyuJeon-CV-Updater/1.0")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            return data.get("data", [])
    except urllib.error.HTTPError as e:
        print(f"API error: {e.code} {e.reason}")
        return []


def is_relevant_paper(paper):
    """Filter out papers that don't belong to this author (disambiguation)."""
    # Known irrelevant papers by Semantic Scholar ID (other Mingyu Jeons)
    irrelevant_ids = {
        "b35e192cea8953072c680eca3082d3a0c2af886f",  # Jovian polar haze (astrophysics)
        "c78ade49c42ca8c4115d0a70c91cc929bb583732",  # School-age children stress (nursing)
        "6ed5068ac488e1e0a9ad533b1961e1207b3a7bff",  # Duplicate SMoG entry
    }
    return paper.get("paperId") not in irrelevant_ids


def paper_to_entry(paper):
    """Convert a Semantic Scholar paper to our JSON format."""
    ext_ids = paper.get("externalIds", {})
    arxiv_id = ext_ids.get("ArXiv")
    doi = ext_ids.get("DOI")

    authors = [a["name"] for a in paper.get("authors", [])]
    venue = paper.get("venue", "") or ""
    year = paper.get("year")

    # Generate a stable ID from the Semantic Scholar paper ID
    ss_id = paper.get("paperId", "")

    return {
        "id": f"ss-{ss_id[:12]}",
        "title": paper.get("title", ""),
        "authors": authors,
        "venue": venue,
        "venue_full": venue,
        "year": year,
        "type": "preprint" if "arxiv" in venue.lower() else "conference",
        "badges": [],
        "arxiv": arxiv_id,
        "doi": doi,
        "semantic_scholar_id": ss_id,
        "pdf": None,
        "code": None,
        "project": None,
        "abstract": paper.get("abstract"),
        "highlight": False,
        "source": "semantic_scholar",
    }


def merge_papers(existing_papers, new_papers):
    """Merge new papers into existing list, preserving manual entries and overrides."""
    # Index existing papers by semantic_scholar_id and by id
    by_ss_id = {}
    by_id = {}
    for p in existing_papers:
        if p.get("semantic_scholar_id"):
            by_ss_id[p["semantic_scholar_id"]] = p
        by_id[p["id"]] = p

    merged = list(existing_papers)  # Start with all existing

    for new_p in new_papers:
        ss_id = new_p.get("semantic_scholar_id")
        if ss_id and ss_id in by_ss_id:
            # Already exists — update citation count and abstract only
            existing = by_ss_id[ss_id]
            # Don't overwrite manually curated fields
            continue
        elif new_p["id"] in by_id:
            continue
        else:
            # New paper — add it
            merged.append(new_p)
            print(f"  + Added: {new_p['title']}")

    return merged


def main():
    print("Fetching papers from Semantic Scholar...")
    raw_papers = fetch_papers()
    print(f"  Found {len(raw_papers)} papers")

    # Filter
    relevant = [p for p in raw_papers if is_relevant_paper(p)]
    print(f"  {len(relevant)} relevant after filtering")

    new_entries = [paper_to_entry(p) for p in relevant]

    # Load existing
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            data = json.load(f)
        existing = data.get("papers", [])
    else:
        data = {}
        existing = []

    # Merge
    merged = merge_papers(existing, new_entries)

    # Sort by year desc
    merged.sort(key=lambda p: (p.get("year") or 0), reverse=True)

    # Save
    from datetime import date
    data["last_updated"] = date.today().isoformat()
    data["source"] = "merged: semantic_scholar + google_scholar + manual"
    data["papers"] = merged

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Done. Total papers: {len(merged)}")


if __name__ == "__main__":
    main()
