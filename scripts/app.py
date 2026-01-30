#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Dict, List

import pandas as pd
import altair as alt
import streamlit as st


@dataclass
class BibEntry:
    authors: List[str]
    year: int
    venue: str


SECTION_KEYS = {"ijournal_papers", "reviewed_iconference"}


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


def load_ijournal_entries(bib_path: Path) -> List[BibEntry]:
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


def build_count_dataframe(entries: List[BibEntry]) -> pd.DataFrame:
    rows = []
    for entry in entries:
        first_author = entry.authors[0]
        rows.append({"year": entry.year, "author": first_author, "venue": entry.venue, "count": 1})
    if not rows:
        return pd.DataFrame(columns=["year", "author", "venue", "count"])
    df = pd.DataFrame(rows)
    df = df.groupby(["year", "author", "venue"], as_index=False)["count"].sum()
    return df


def build_all_author_dataframe(entries: List[BibEntry]) -> pd.DataFrame:
    rows = []
    for entry in entries:
        for author in entry.authors:
            rows.append({"year": entry.year, "author": author, "count": 1})
    if not rows:
        return pd.DataFrame(columns=["year", "author", "count"])
    df = pd.DataFrame(rows)
    df = df.groupby(["year", "author"], as_index=False)["count"].sum()
    return df


def main() -> None:
    st.set_page_config(page_title="International Journal First Authors", layout="wide")
    st.title("International Journal + International Conference: First Author Counts by Year")

    bib_path = Path(__file__).resolve().parents[1] / "main.bib"
    if not bib_path.exists():
        st.error(f"main.bib not found: {bib_path}")
        return

    entries = load_ijournal_entries(bib_path)
    df = build_count_dataframe(entries)
    df_all = build_all_author_dataframe(entries)

    if df.empty:
        st.warning("No entries found in ijournal_papers or reviewed_iconference.")
        return

    years = sorted(df["year"].unique())
    selected_years = st.multiselect("Years", years, default=years)

    authors = sorted(df["author"].unique())
    selected_authors = st.multiselect("First authors", authors, default=authors)

    all_authors = sorted(df_all["author"].unique())
    selected_all_authors = st.multiselect("All authors", all_authors, default=all_authors)

    filtered = df[df["year"].isin(selected_years) & df["author"].isin(selected_authors)]
    if filtered.empty:
        st.info("No data for the selected filters.")
        return

    chart = (
        alt.Chart(filtered)
        .mark_bar()
        .encode(
            x=alt.X("year:O", title="Year"),
            y=alt.Y("sum(count):Q", title="Count"),
            color=alt.Color("author:N", title="First author"),
            tooltip=["year:O", "author:N", alt.Tooltip("sum(count):Q", title="Count")],
        )
        .properties(height=420)
    )

    st.altair_chart(chart, use_container_width=True)

    st.subheader("Counts by First Author (colored by year)")
    top_first_authors = (
        filtered.groupby("author", as_index=False)["count"].sum()
        .sort_values("count", ascending=False)
        .head(30)["author"]
        .tolist()
    )
    filtered_top = filtered[filtered["author"].isin(top_first_authors)]
    chart_by_author = (
        alt.Chart(filtered_top)
        .mark_bar()
        .encode(
            x=alt.X("author:N", title="First author", sort="-y"),
            y=alt.Y("sum(count):Q", title="Count"),
            color=alt.Color("year:O", title="Year"),
            tooltip=["author:N", "year:O", alt.Tooltip("sum(count):Q", title="Count")],
        )
        .properties(height=420)
    )
    st.altair_chart(chart_by_author, use_container_width=True)

    st.subheader("Counts by All Authors (colored by year)")
    filtered_all = df_all[df_all["year"].isin(selected_years) & df_all["author"].isin(selected_all_authors)]
    if filtered_all.empty:
        st.info("No data for the selected all-author filters.")
    else:
        top_all_authors = (
            filtered_all.groupby("author", as_index=False)["count"].sum()
            .sort_values("count", ascending=False)
            .head(30)["author"]
            .tolist()
        )
        filtered_all_top = filtered_all[filtered_all["author"].isin(top_all_authors)]
        chart_by_all_authors = (
            alt.Chart(filtered_all_top)
            .mark_bar()
            .encode(
                x=alt.X("author:N", title="Author", sort="-y"),
                y=alt.Y("sum(count):Q", title="Count"),
                color=alt.Color("year:O", title="Year"),
                tooltip=["author:N", "year:O", alt.Tooltip("sum(count):Q", title="Count")],
            )
            .properties(height=420)
        )
        st.altair_chart(chart_by_all_authors, use_container_width=True)

    st.subheader("K. Kawaharazuka: Counts by Year (colored by venue)")
    kk_filtered = filtered[filtered["author"] == "K. Kawaharazuka"]
    if kk_filtered.empty:
        st.info("No entries for K. Kawaharazuka in the selected filters.")
    else:
        chart_kk = (
            alt.Chart(kk_filtered)
            .mark_bar()
            .encode(
                x=alt.X("year:O", title="Year"),
                y=alt.Y("sum(count):Q", title="Count"),
                color=alt.Color("venue:N", title="Venue"),
                tooltip=["year:O", "venue:N", alt.Tooltip("sum(count):Q", title="Count")],
            )
            .properties(height=420)
        )
        st.altair_chart(chart_kk, use_container_width=True)
    st.dataframe(filtered.sort_values(["year", "author"]))


if __name__ == "__main__":
    main()
