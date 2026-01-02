# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VC Diligence AI is a Python tool for automated financial KPI extraction for venture capital due diligence. It analyzes CSV files containing startup financial data and generates reports with metrics like burn rate, runway, and growth rankings.

## Commands

```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run analysis
python src/extract.py data/startups.csv
python src/extract.py                    # defaults to data/startups.csv
```

## Architecture

Single-module CLI tool (`src/extract.py`) with two main functions:
- `analyze_csv(filepath)` - Reads CSV and calculates metrics (burn rate, runway, top growers)
- `print_report(results)` - Formats and outputs the analysis report

## Data Format

CSV files must have columns: `name`, `cash`, `monthly_burn`, `revenue_growth`
- `revenue_growth` is a decimal (0.15 = 15%)
- See `data/startups.csv` for example format
