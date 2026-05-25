# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

Production analytics system for a business. Designed to explore Claude Code capabilities — skills, agents, data pipelines, and automated analysis workflows. Treat all code as production-grade, not experimental.

## Architecture

This repo follows a modular analytics system design:

- **`agents/`** — Agent definitions (markdown prompt files) that perform specific analytical tasks (e.g., funnel analysis, anomaly detection). Each agent is a self-contained prompt with clear inputs/outputs.
- **`skills/`** — Reusable Claude Code skills (`.claude/skills/`) for domain-specific operations (e.g., computing drop-off rates, generating readouts).
- **`data/raw/`** — Source data files. Never modified directly.
- **`data/processed/`** — Transformed/cleaned data outputs.
- **`outputs/`** — Generated reports, readouts, PDFs, and analysis artifacts.
- **`working/`** — Design docs, specs, and in-progress planning documents.
- **`src/`** — Python modules for reusable logic (features, models, utils).

## Conventions

- Agents chain: analysis agent → writer agent → audience-specific outputs (leadership, product, data team).
- Raw data is immutable. All transformations write to `data/processed/` or `outputs/`.
- Agent outputs go to `outputs/` with date-stamped filenames (e.g., `funnel_readout_2026-05-25.md`).
- Design decisions and system specs live in `working/`.
- Python code follows the global CLAUDE.md standards (type hints, NumPy docstrings, polars for perf, pandas for quick work).

## Stack

- **Python 3.10+** — pandas, polars, numpy, scikit-learn, matplotlib, seaborn
- **Claude Code agents** — markdown-defined, chained via orchestration
- **Output formats** — markdown readouts, PDF decks, CSV exports
