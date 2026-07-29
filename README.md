# Customer Success Lifecycle Journey Map

An interactive, color-coded map of the full customer lifecycle built from a real cross-functional CS program and generalized for public sharing.

**Live demo:** [melissamcgowan.github.io/Customer-Journey-Map](https://melissamcgowan.github.io/Customer-Journey-Map/)
**PDF version:** [Customer_Success_Journey_Map.pdf](Customer_Success_Journey_Map.pdf)

## What it does

Turns a dense, color-coded Excel journey map into two things:

- An interactive web page with two views: the full customer lifecycle, and an Onboarding deep-dive; each broken into stages, color-coded to match the original workbook's own formatting
- A clean PDF export of the same map

Each stage contains expandable cards, one per touchpoint, showing:

- The trigger that kicks it off
- Objectives for that touchpoint
- Who's involved (role chips, with notes on specific responsibilities)
- Key activities, numbered in sequence
- Templates & collateral used
- Systems of record touched
- Success metrics
- A "moment of value" flag where one exists

A role filter dims every card except the ones a given role touches; useful for showing any one team member exactly where they show up across the whole customer lifecycle, without hunting through a wide spreadsheet.

## Why this exists

Most journey maps live and die as a static slide or spreadsheet nobody opens twice. This turns one into something you can filter, click through, and hand to a new hire or cross-functional partner without a 45-minute walkthrough.

It's also the connective layer for the rest of this portfolio. This is the map that the health score model, save-play automation, onboarding sequences, and playbook router all automate pieces of. This project documents the underlying human process; the others automate parts of it.

## How it's built

A three-step pipeline:

1. **`extract.py`** - reads the source Excel workbook (two sheets: full lifecycle, and a high-touch onboarding deep-dive), using cell fill colors and merged header ranges to auto-detect stage groupings, then pulls structured fields (trigger, objectives, roles, activities, templates, systems, metrics) into JSON
2. **`sanitize.py`** - strips real names, tool names, and internal references, replacing them with generic role/system labels, with a verification pass confirming nothing flagged remains
3. **`build_html.py`** / **`build_pdf.py`** - render the sanitized JSON into the interactive page and the PDF

## Tech

Python (`openpyxl` for the Excel parse, standard library otherwise), vanilla HTML/CSS/JS for the front end. No build step, no dependencies beyond `openpyxl`. Deploys via GitHub Pages.

## Part of a larger portfolio

This is the foundational artifact in a broader AI-powered CS automation portfolio; see the [profile README](https://github.com/melissamcgowan/melissamcgowan) for the full set of projects that build on top of the process this map documents.

*Note: this is a sample/sanitized version - names and internal tool references have been generalized for public sharing. Process structure and content reflect real Customer Success program design work.*
