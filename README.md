# VC Diligence AI

Automated financial KPI extraction for venture capital due diligence.

## 🚀 What it does

- Analyzes CSV files with startup financial data
- Calculates key metrics: Burn Rate, Runway, Growth Rankings
- Outputs clean, formatted reports
- Built for VCs, angels, and startup analysts

## 📊 Example Output
📊 VC DUE DILIGENCE REPORT
==================================================
Startups analyzed: 5
Total Cash: €23,300,000
🔥 Avg Burn Rate: €132,000/month
⏳ Avg Runway: 24.5 months

🚀 TOP GROWTH STARTUPS:
- GreenHydrogen: 30.0% MoM
- BatteryX: 22.0% MoM
- SolarTech: 15.0% MoM


## 🛠️ Quick Start

~~~bash
# 1. Clone & setup
git clone https://github.com/YOUR-USERNAME/vc-diligence-ai.git
cd vc-diligence-ai
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Run analysis
python src/extract.py data/startups.csv
~~~

## 📁 Project Structure

vc-diligence-ai/
├── src/              # Source code
│   └── extract.py    # Main analysis module
├── data/             # Sample data
├── tests/            # Unit tests (coming soon)
├── requirements.txt  # Python dependencies
└── README.md         # This file

## 🎯 Roadmap

- CSV analysis & reporting
- PDF document parsing
- AI-powered data extraction
- Web dashboard interface
- API for integration with VC tools
