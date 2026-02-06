#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import re
from typing import Dict, List

import pandas as pd


SECTION_KEYS = {"ijournal_papers", "reviewed_iconference"}
OUTPUT_HTML = Path(__file__).resolve().parents[1] / "bib_charts.html"


@dataclass
class BibEntry:
    authors: List[str]
    year: int
    venue: str


def _clean_bib_value(text: str) -> str:
    cleaned = text.strip().rstrip(",")
    cleaned = cleaned.strip("{}").strip()
    return cleaned


def _normalize_venue_label(venue: str) -> str:
    match = re.match(r"^(.*?)(19|20)\d{2}$", venue)
    if match:
        return match.group(1)
    return venue


def _parse_entry(lines: List[str]) -> BibEntry | None:
    fields: Dict[str, str] = {}
    for line in lines:
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip().lower()
        value = _clean_bib_value(value)
        fields[key] = value
    if "author" not in fields or "year" not in fields:
        return None

    authors_raw = fields["author"].replace(" and ", ",")
    authors = [a.strip() for a in authors_raw.split(",") if a.strip()]
    year_match = re.search(r"\d{4}", fields["year"])
    venue_value = fields.get("journal") or fields.get("booktitle")
    venue = _normalize_venue_label(venue_value) if venue_value else "Unknown"
    if not authors or not year_match:
        return None
    return BibEntry(authors=authors, year=int(year_match.group(0)), venue=venue)


def load_entries(bib_path: Path) -> List[BibEntry]:
    entries: List[BibEntry] = []
    in_section = False
    current_lines: List[str] = []
    in_entry = False

    with bib_path.open("r", encoding="utf-8") as fh:
        for raw_line in fh:
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("%"):
                in_section = any(key in line for key in SECTION_KEYS)
                continue
            if not in_section:
                continue

            if line.startswith("@"):
                in_entry = True
                current_lines = []
                continue
            if in_entry and line == "}":
                entry = _parse_entry(current_lines)
                if entry:
                    entries.append(entry)
                in_entry = False
                current_lines = []
                continue
            if in_entry:
                current_lines.append(line)

    return entries


def build_first_author_df(entries: List[BibEntry]) -> pd.DataFrame:
    rows = []
    for entry in entries:
        rows.append({"year": entry.year, "author": entry.authors[0], "venue": entry.venue, "count": 1})
    if not rows:
        return pd.DataFrame(columns=["year", "author", "venue", "count"])
    df = pd.DataFrame(rows)
    df = df.groupby(["year", "author", "venue"], as_index=False)["count"].sum()
    return df


def build_all_author_df(entries: List[BibEntry]) -> pd.DataFrame:
    rows = []
    for entry in entries:
        for author in entry.authors:
            rows.append({"year": entry.year, "author": author, "count": 1})
    if not rows:
        return pd.DataFrame(columns=["year", "author", "count"])
    df = pd.DataFrame(rows)
    df = df.groupby(["year", "author"], as_index=False)["count"].sum()
    return df


def _stacked_traces(df: pd.DataFrame, x_col: str, stack_col: str, value_col: str, x_order: List, series_order: List) -> List[Dict]:
    traces = []
    for series in series_order:
        subset = df[df[stack_col] == series]
        counts = []
        for x_value in x_order:
            match = subset[subset[x_col] == x_value]
            counts.append(int(match[value_col].sum()) if not match.empty else 0)
        traces.append({"type": "bar", "name": series, "x": x_order, "y": counts})
    return traces


def _top_n_authors(df: pd.DataFrame, author_col: str, count_col: str, n: int = 30) -> List[str]:
    totals = df.groupby(author_col, as_index=False)[count_col].sum()
    totals = totals.sort_values(count_col, ascending=False).head(n)
    return totals[author_col].tolist()


def build_html(bib_path: Path) -> str:
    entries = load_entries(bib_path)
    df_first = build_first_author_df(entries)
    df_all = build_all_author_df(entries)

    if df_first.empty:
        raise RuntimeError("No entries found in ijournal_papers or reviewed_iconference.")

    years = sorted(df_first["year"].unique().tolist())

    first_authors = sorted(df_first["author"].unique().tolist())
    traces_year_by_first = _stacked_traces(
        df_first,
        x_col="year",
        stack_col="author",
        value_col="count",
        x_order=years,
        series_order=first_authors,
    )

    top_first_authors = _top_n_authors(df_first, "author", "count", n=30)
    df_first_top = df_first[df_first["author"].isin(top_first_authors)]
    traces_first_by_author = _stacked_traces(
        df_first_top,
        x_col="author",
        stack_col="year",
        value_col="count",
        x_order=top_first_authors,
        series_order=years,
    )

    top_all_authors = _top_n_authors(df_all, "author", "count", n=30)
    df_all_top = df_all[df_all["author"].isin(top_all_authors)]
    traces_all_by_author = _stacked_traces(
        df_all_top,
        x_col="author",
        stack_col="year",
        value_col="count",
        x_order=top_all_authors,
        series_order=years,
    )

    kk_df = df_first[df_first["author"] == "K. Kawaharazuka"]
    kk_venues = sorted(kk_df["venue"].unique().tolist())
    traces_kk = _stacked_traces(
        kk_df,
        x_col="year",
        stack_col="venue",
        value_col="count",
        x_order=years,
        series_order=kk_venues,
    )

    context = {
        "traces_year_by_first": traces_year_by_first,
        "traces_first_by_author": traces_first_by_author,
        "traces_all_by_author": traces_all_by_author,
        "traces_kk": traces_kk,
        "years": years,
    }

    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>International Journal + International Conference Counts</title>
  <script src=\"https://cdn.plot.ly/plotly-2.27.0.min.js\"></script>
  <style>
    body {{ font-family: "Helvetica Neue", Arial, sans-serif; margin: 24px; color: #1f1f1f; }}
    h1 {{ font-size: 24px; margin-bottom: 8px; }}
    h2 {{ font-size: 18px; margin-top: 32px; }}
    .chart {{ width: 100%; height: 480px; }}
    .note {{ color: #666; font-size: 13px; margin-top: 4px; }}
  </style>
</head>
<body>
  <h1>International Journal + International Conference Counts</h1>
  <div class=\"note\">Data source: main.bib (% ijournal_papers + % reviewed_iconference)</div>

  <h2>Counts by Year (First Author)</h2>
  <div id=\"chart-year-first\" class=\"chart\"></div>

  <h2>Counts by First Author (Top 30, colored by year)</h2>
  <div id=\"chart-first-author\" class=\"chart\"></div>

  <h2>Counts by All Authors (Top 30, colored by year)</h2>
  <div id=\"chart-all-author\" class=\"chart\"></div>

  <h2>K. Kawaharazuka: Counts by Year (colored by venue)</h2>
  <div id=\"chart-kk\" class=\"chart\"></div>

  <script>
    const data = {json.dumps(context, ensure_ascii=False)};

    Plotly.newPlot("chart-year-first", data.traces_year_by_first, {{
      barmode: "stack",
      xaxis: {{ title: "Year", type: "category" }},
      yaxis: {{ title: "Count" }},
      margin: {{ t: 20 }}
    }}, {{responsive: true}});

    Plotly.newPlot("chart-first-author", data.traces_first_by_author, {{
      barmode: "stack",
      xaxis: {{ title: "First Author", type: "category" }},
      yaxis: {{ title: "Count" }},
      margin: {{ t: 20 }}
    }}, {{responsive: true}});

    Plotly.newPlot("chart-all-author", data.traces_all_by_author, {{
      barmode: "stack",
      xaxis: {{ title: "Author", type: "category" }},
      yaxis: {{ title: "Count" }},
      margin: {{ t: 20 }}
    }}, {{responsive: true}});

    Plotly.newPlot("chart-kk", data.traces_kk, {{
      barmode: "stack",
      xaxis: {{ title: "Year", type: "category" }},
      yaxis: {{ title: "Count" }},
      margin: {{ t: 20 }}
    }}, {{responsive: true}});
  </script>
</body>
</html>
"""


def main() -> None:
    bib_path = Path(__file__).resolve().parents[1] / "main.bib"
    html = build_html(bib_path)
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"Wrote {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
