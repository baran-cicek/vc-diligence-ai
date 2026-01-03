# VC Diligence AI
![](assets/vc-diligence-ai-ascii.png)

Automated financial KPI extraction for venture capital due diligence.

## What it does

- Analyzes CSV or PDF files with startup financial data
- Calculates key metrics: Burn Rate, Runway, Growth Rankings
- AI-powered data extraction with multi-provider support
- Data quality validation and warnings
- Outputs clean, formatted reports
- Built for VCs, angels, and startup analysts

## Example Output

~~~
📁 Analyzing: data/messy_pitch_deck.pdf
🤖 AI extraction (groq): Found 1 startup(s)
==================================================
📊 VC DUE DILIGENCE REPORT
==================================================
Startups analyzed: 1
Total Cash: €4,200,000
🔥 Avg Burn Rate: €180,000/month
⏳ Avg Runway: 23.3 months
🚀 TOP GROWTH STARTUPS:
   • QuantumBio: 35.0% MoM
==================================================
~~~

## Installation

From GitHub (recommended):
~~~bash
git clone https://github.com/baran-cicek/vc-diligence-ai.git
cd vc-diligence-ai
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
~~~

Note: Virtual environment must be activated before running commands. Look for `(.venv)` in prompt.

## Quick Start

~~~bash
# Analyze CSV file
python src/extract.py data/startups.csv

# Analyze PDF file (text-based PDFs with tables or key-value format)
python src/extract.py data/startups.pdf

# AI-powered PDF extraction (auto-detects available API key)
python src/extract.py data/messy_pitch_deck.pdf --ai

# AI extraction with specific provider
python src/extract.py data/messy_pitch_deck.pdf --ai --provider openai
~~~

## AI-Powered Extraction

The `--ai` flag enables AI-powered data extraction for PDF files, useful when standard parsing fails on complex or unstructured documents.

Supported providers: Anthropic (Claude) • OpenAI (GPT) • Google (Gemini) • Groq • Mistral • DeepSeek

*Recommendation: Start with Groq (free, no credit card required)*

### API Key Setup

Set the environment variable for your chosen provider:

~~~bash
# Anthropic (Claude)
export ANTHROPIC_API_KEY='your-key-here'
# Get key: https://console.anthropic.com/

# OpenAI
export OPENAI_API_KEY='your-key-here'
# Get key: https://platform.openai.com/api-keys

# Google AI (Gemini)
export GOOGLE_API_KEY='your-key-here'
# Get key: https://aistudio.google.com/apikey

# Groq (Free)
export GROQ_API_KEY='your-key-here'
# Get key: https://console.groq.com/keys

# Mistral
export MISTRAL_API_KEY='your-key-here'
# Get key: https://console.mistral.ai/api-keys/

# DeepSeek
export DEEPSEEK_API_KEY='your-key-here'
# Get key: https://platform.deepseek.com/api_keys
~~~

#### Permanent Setup

Mac/Linux (bash):
~~~bash
echo 'export GROQ_API_KEY=your-key-here' >> ~/.bashrc
source ~/.bashrc
~~~

Mac/Linux (zsh):
~~~bash
echo 'export GROQ_API_KEY=your-key-here' >> ~/.zshrc
source ~/.zshrc
~~~

Windows: Set system environment variable via Settings > System > Environment Variables

Verify:
~~~bash
echo $GROQ_API_KEY
~~~

### Usage Examples

~~~bash
# Auto-detect provider (uses first available API key)
python src/extract.py data/messy_pitch_deck.pdf --ai

# Specific provider
python src/extract.py data/messy_pitch_deck.pdf --ai --provider groq
python src/extract.py data/messy_pitch_deck.pdf --ai --provider google
python src/extract.py data/messy_pitch_deck.pdf --ai --provider openai

# Show help
python src/extract.py --help
~~~

## Python Package Usage

Install locally:
~~~bash
pip install .
~~~

Use in your code:
~~~python
from vc_diligence.extract import load_data, generate_report

df = load_data("pitch.pdf", use_ai=True, provider="groq")
report = generate_report(df)
print(report)
~~~

## Troubleshooting

**litellm not found**: Activate virtual environment, run `pip install -r requirements.txt`

**No API key found**: Set environment variable permanently (see API Key Setup)

**Model deprecated**: Check provider documentation for current model names

## Project Structure

~~~
vc-diligence-ai/
├── vc_diligence/         # Python package
│   ├── __init__.py
│   └── extract.py        # Core implementation
├── src/
│   └── extract.py        # CLI wrapper
├── data/                 # Sample data
├── assets/               # Images
├── setup.py              # pip install support
├── requirements.txt
├── LICENSE
└── README.md
~~~

## Roadmap

- [x] CSV analysis & reporting
- [x] PDF document parsing
- [x] AI-powered data extraction
- [x] API for integration with VC tools
- [ ] Web dashboard interface
