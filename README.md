# VC Diligence AI

Automated financial KPI extraction for venture capital due diligence.

## What it does

- Analyzes CSV or PDF files with startup financial data
- Calculates key metrics: Burn Rate, Runway, Growth Rankings
- AI-powered data extraction with multi-provider support
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

Note: Virtual environment must be activated before running commands. Look for `(.venv)` in prompt.

## Quick Start

~~~bash
# Analyze CSV file
python src/extract.py data/startups.csv

# Analyze PDF file (text-based PDFs with tables or key-value format)
python src/extract.py data/startups.pdf

# AI-powered PDF extraction (auto-detects available API key)
python src/extract.py data/report.pdf --ai

# AI extraction with specific provider
python src/extract.py data/report.pdf --ai --provider openai
~~~

## AI-Powered Extraction

The `--ai` flag enables AI-powered data extraction for PDF files, useful when standard parsing fails on complex or unstructured documents.

### Provider Comparison

| Provider   | Model                | Cost/1M tokens | Speed  | Quality | Free Tier          |
|------------|----------------------|----------------|--------|---------|-------------------|
| **Groq**   | Llama3-70B           | Free           | Fast   | Good    | Yes (generous)    |
| **Google** | Gemini 1.5 Flash     | $0.075         | Fast   | Good    | Yes ($0 credit)   |
| **DeepSeek** | DeepSeek V2        | $0.14          | Medium | Good    | Yes ($5 credit)   |
| **Mistral** | Mistral Small       | $0.20          | Fast   | Good    | Yes (limited)     |
| **OpenAI** | GPT-4o-mini          | $0.15          | Fast   | Great   | No                |
| **Anthropic** | Claude 3.5 Haiku  | $0.25          | Fast   | Great   | No                |

*Recommendation: Start with Groq (free) or Google (free tier), upgrade to OpenAI/Anthropic for best quality.*

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
python src/extract.py data/report.pdf --ai

# Specific provider
python src/extract.py data/report.pdf --ai --provider groq
python src/extract.py data/report.pdf --ai --provider google
python src/extract.py data/report.pdf --ai --provider openai

# Show help
python src/extract.py --help
~~~

## Example Output

~~~
📁 Analyzing: data/report.pdf
🤖 AI extraction (groq): Found 5 startup(s)

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

## Troubleshooting

**litellm not found**: Activate virtual environment, run `pip install -r requirements.txt`

**No API key found**: Set environment variable permanently (see API Key Setup)

**Model deprecated**: Check provider documentation for current model names

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
- [x] AI-powered data extraction
- [ ] Web dashboard interface
- [ ] API for integration with VC tools
