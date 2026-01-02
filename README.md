# VC Diligence AI

Automated financial KPI extraction for venture capital due diligence.

## What it does

- Analyzes CSV or PDF files with startup financial data
- Calculates key metrics: Burn Rate, Runway, Growth Rankings
- Outputs clean, formatted reports
- Built for VCs, angels, and startup analysts

## Installation

From GitHub (recommended):
~~~bash
git clone https://github.com/baran-cicek/vc-diligence-ai.git
cd vc-diligence-ai
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
~~~

## Quick Start

~~~bash
# Analyze CSV file
python src/extract.py data/startups.csv

# Analyze PDF file (text-based PDFs with tables or key-value format)
python src/extract.py data/startups.pdf
~~~

## Example Output

~~~
📊 VC DUE DILIGENCE REPORT
==================================================
Startups analyzed: 5
Total Cash: €23,300,000
🔥 Avg Burn Rate: €132,000/month
⏳ Avg Runway: 31.3 months

🚀 TOP GROWTH STARTUPS:
• GreenHydrogen: 30.0% MoM
• BatteryX: 22.0% MoM
• SolarTech: 15.0% MoM
==================================================
~~~

## Project Structure

~~~
vc-diligence-ai/
├── src/              # Source code
│   └── extract.py    # Main analysis module
├── data/             # Sample data
├── tests/            # Unit tests (coming soon)
├── requirements.txt  # Python dependencies
└── README.md         # This file
~~~

## Roadmap

- [x] CSV analysis & reporting
- [x] PDF document parsing
- [ ] AI-powered data extraction
- [ ] Web dashboard interface
- [ ] API for integration with VC tools
