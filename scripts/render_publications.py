#!/usr/bin/env python3
"""
Render publications HTML from JSON-LD ontology.

Reads data/publications.jsonld → generates the Publications section
and replaces it between markers in index.html.
"""

import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent.parent
JSONLD_FILE = ROOT / "data" / "publications.jsonld"
HTML_FILE = ROOT / "index.html"

MARKER_START = "<!-- PUBLICATIONS:START -->"
MARKER_END = "<!-- PUBLICATIONS:END -->"


def load_ontology():
    with open(JSONLD_FILE, encoding="utf-8") as f:
        return json.load(f)


def resolve_agents(agent_ids, agents_map, self_id="agent:mingyu-jeon"):
    """Render author list with self bolded."""
    parts = []
    for aid in agent_ids:
        agent = agents_map.get(aid, {})
        name = escape(agent.get("name", aid))
        if aid == self_id:
            parts.append(f"<strong>{name}</strong>")
        else:
            parts.append(name)
    return ", ".join(parts)


def resolve_venue(venue_id, venues_map):
    """Return (display_name, url_or_none) for a venue."""
    venue = venues_map.get(venue_id, {})
    name = venue.get("name", venue_id)
    url = venue.get("url")
    return name, url


def render_badges(badges):
    parts = []
    for b in badges:
        cls = "badge"
        bl = b.lower()
        if "award" in bl:
            cls += " award"
        elif bl == "oral":
            cls += " oral"
        parts.append(f'<span class="{cls}">{escape(b)}</span>')
    return "\n            ".join(parts)


def render_archives(archives):
    """Render [arXiv / paper / ...] link list."""
    links = []
    for a in archives:
        label = a["type"]
        if label == "openreview":
            label = "paper"
        elif label == "engrxiv":
            label = "paper"
        url = a["url"]
        links.append(f'<a href="{url}">{escape(label)}</a>')
    return links


def render_work(work, agents_map, venues_map):
    """Render a single Work as an HTML table block."""
    # Sort manifestations: conference > workshop > journal > preprint, then by year desc
    # Use venue tier from venues_map for sorting
    tier_order = {"conference": 0, "journal": 1, "journal-domestic": 1, "workshop": 2, "preprint": 3}

    def manifestation_sort_key(m):
        venue = venues_map.get(m.get("presentedAt", ""), {})
        tier = venue.get("tier", "preprint")
        return (tier_order.get(tier, 9), -(m.get("year", 0)))

    manifestations = sorted(work.get("manifestations", []), key=manifestation_sort_key)

    if not manifestations:
        return ""

    primary = manifestations[0]
    others = manifestations[1:]

    # Thumbnail
    thumb = work.get("thumbnail")
    if thumb:
        img_html = f'<img src="{thumb}" alt="{escape(work.get("label", ""))}" width="160" height="120" class="paper-thumb">'
    else:
        label_text = escape(work.get("label", ""))
        # Split label into two lines for placeholder
        words = label_text.split()
        mid = len(words) // 2
        line1 = " ".join(words[:mid]) if mid > 0 else words[0] if words else ""
        line2 = " ".join(words[mid:]) if mid > 0 else ""
        placeholder_text = f"{line1}<br>{line2}" if line2 else line1
        img_html = f'<div class="paper-img-placeholder">{placeholder_text}</div>'

    # Primary manifestation
    title = escape(primary.get("title", ""))
    year = primary.get("year", "")

    # Authors: use manifestation-level if present, else work-level
    author_ids = primary.get("authors") or work.get("contributors", [])
    authors_html = resolve_agents(author_ids, agents_map)

    # Venue
    venue_id = primary.get("presentedAt", "")
    venue_name, venue_url = resolve_venue(venue_id, venues_map)
    if venue_url:
        venue_html = f'<a href="{venue_url}">{escape(venue_name)}</a>'
    else:
        venue_html = f'{escape(venue_name)}'

    # Badges
    badges_html = render_badges(primary.get("badges", []))

    # Links: archives + code
    links = render_archives(primary.get("archives", []))
    code = work.get("code")
    if code:
        code_url = code.get("url", "") if isinstance(code, dict) else code
        links.append(f'<a href="{code_url}">code</a>')

    links_html = " / ".join(links)

    # Build primary HTML
    html = f"""    <!-- Work: {escape(work.get("label", ""))} -->
    <table width="100%" border="0" cellspacing="0" cellpadding="20" class="paper-group">
    <tr>
        <td width="25%" valign="middle" class="paper-img-cell">
            {img_html}
        </td>
        <td width="75%" valign="top">
            <span class="paper-title">{title}</span>
            <br>
            {authors_html}
            <br>
            <em>{venue_html}</em>, {year}
            {badges_html}
"""

    if links_html:
        html += f"            [{links_html}]\n"

    # Related manifestations
    for other in others:
        o_title = escape(other.get("title", ""))
        o_year = other.get("year", "")
        o_author_ids = other.get("authors") or work.get("contributors", [])
        o_authors_html = resolve_agents(o_author_ids, agents_map)
        o_venue_id = other.get("presentedAt", "")
        o_venue_name, o_venue_url = resolve_venue(o_venue_id, venues_map)
        if o_venue_url:
            o_venue_html = f'<a href="{o_venue_url}">{escape(o_venue_name)}</a>'
        else:
            o_venue_html = f'{escape(o_venue_name)}'

        o_badges_html = render_badges(other.get("badges", []))
        o_links = render_archives(other.get("archives", []))
        o_links_html = " / ".join(o_links)

        html += f"""            <p class="related-paper">
                <span class="related-arrow">&rarr;</span>
                {o_title}
                <br>
                {o_authors_html}
                &mdash; <em>{o_venue_html}</em>, {o_year}
                {o_badges_html}
"""
        if o_links_html:
            html += f"                [{o_links_html}]\n"
        html += "            </p>\n"

    html += """        </td>
    </tr>
    </table>
"""
    return html


def render_all(ontology):
    """Render all works into HTML."""
    # Build lookup maps
    agents_map = {a["@id"]: a for a in ontology.get("agents", [])}
    venues_map = {v["@id"]: v for v in ontology.get("venues", [])}

    works = ontology.get("works", [])

    # Sort works by latest manifestation year (descending)
    def work_max_year(w):
        years = [m.get("year", 0) for m in w.get("manifestations", [])]
        return max(years) if years else 0

    works_sorted = sorted(works, key=work_max_year, reverse=True)

    blocks = []
    for work in works_sorted:
        block = render_work(work, agents_map, venues_map)
        if block:
            blocks.append(block)

    return "\n".join(blocks)


def update_html(publications_html):
    """Replace content between markers in index.html."""
    content = HTML_FILE.read_text(encoding="utf-8")

    start_idx = content.find(MARKER_START)
    end_idx = content.find(MARKER_END)

    if start_idx == -1 or end_idx == -1:
        print(f"ERROR: Markers not found in {HTML_FILE}")
        print(f"  Add '{MARKER_START}' and '{MARKER_END}' to index.html")
        return False

    new_content = (
        content[: start_idx + len(MARKER_START)]
        + "\n"
        + publications_html
        + "\n    "
        + content[end_idx:]
    )

    HTML_FILE.write_text(new_content, encoding="utf-8")
    return True


def main():
    print("Loading ontology...")
    ontology = load_ontology()

    works = ontology.get("works", [])
    total_manifestations = sum(len(w.get("manifestations", [])) for w in works)
    print(f"  {len(works)} works, {total_manifestations} manifestations")

    print("Rendering HTML...")
    html = render_all(ontology)

    print("Updating index.html...")
    if update_html(html):
        print("Done!")
    else:
        print("Failed to update HTML.")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
