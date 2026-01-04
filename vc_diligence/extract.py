#!/usr/bin/env python3
"""
VC Diligence AI - Financial KPI Extraction

Automated extraction of burn rate, runway, and growth metrics from startup
pitch decks and financial documents. Supports CSV, PDF, and AI-powered extraction.

Features:
- Multi-provider AI support (6 providers)
- Batch processing with progress tracking
- Cost estimation for API calls
- Data quality validation
"""
import pandas as pd
import pdfplumber
import re
import sys
import os
import argparse
import json
from datetime import datetime
from tqdm import tqdm
import numpy as np

# Provider configuration: provider_name -> (model_id, env_var)
PROVIDERS = {
    'anthropic': ('claude-3-5-haiku-20241022', 'ANTHROPIC_API_KEY'),
    'openai': ('gpt-4o-mini', 'OPENAI_API_KEY'),
    'google': ('gemini/gemini-1.5-flash', 'GOOGLE_API_KEY'),
    'groq': ('groq/llama-3.3-70b-versatile', 'GROQ_API_KEY'),
    'mistral': ('mistral/mistral-small-latest', 'MISTRAL_API_KEY'),
    'deepseek': ('deepseek/deepseek-chat', 'DEEPSEEK_API_KEY'),
}

# Cost per 1K tokens (input, output) in USD
PROVIDER_COSTS = {
    'groq': (0, 0),  # Free tier
    'anthropic': (0.003, 0.015),
    'openai': (0.00015, 0.0006),
    'google': (0.000075, 0.0003),
    'mistral': (0.0002, 0.0006),
    'deepseek': (0.00014, 0.00028),
}

MAX_PDF_PAGES = 50


class NumpyEncoder(json.JSONEncoder):
    """JSON encoder that handles numpy types."""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def detect_provider() -> str | None:
    """Auto-detect available provider by checking environment variables."""
    for provider, (_, env_var) in PROVIDERS.items():
        if os.environ.get(env_var):
            return provider
    return None


def get_provider_error_message() -> str:
    """Generate error message with setup instructions for all providers."""
    msg = "No API key found. Set one of the following environment variables:\n\n"
    instructions = [
        ("ANTHROPIC_API_KEY", "Anthropic", "https://console.anthropic.com/"),
        ("OPENAI_API_KEY", "OpenAI", "https://platform.openai.com/api-keys"),
        ("GOOGLE_API_KEY", "Google AI", "https://aistudio.google.com/apikey"),
        ("GROQ_API_KEY", "Groq", "https://console.groq.com/keys"),
        ("MISTRAL_API_KEY", "Mistral", "https://console.mistral.ai/api-keys/"),
        ("DEEPSEEK_API_KEY", "DeepSeek", "https://platform.deepseek.com/api_keys"),
    ]
    for env_var, name, url in instructions:
        msg += f"  {env_var:<20} - {name:<12} ({url})\n"
    msg += "\nExample:\n  export ANTHROPIC_API_KEY='your-key-here'\n"
    return msg


def estimate_cost(text: str, provider: str) -> float:
    """
    Estimate API cost based on text length and provider.
    Returns estimated cost in USD.
    """
    # Rough approximation: OpenAI/Anthropic use ~4 chars per token
    input_tokens = len(text) / 4
    output_tokens = 500  # Conservative estimate for JSON response

    input_cost, output_cost = PROVIDER_COSTS.get(provider, (0, 0))

    # Calculate total: (tokens / 1000) * (cost per 1K tokens)
    total_cost = (input_tokens / 1000 * input_cost) + (output_tokens / 1000 * output_cost)
    return total_cost


def parse_pdf(filepath: str) -> pd.DataFrame:
    """
    Extracts startup data from a text-based PDF.
    Supports table format or key-value pairs.
    Returns DataFrame with columns: name, cash, monthly_burn, revenue_growth
    """
    records = []

    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                # Try table extraction first (most reliable for structured data)
                tables = page.extract_tables()
                for table in tables:
                    if not table:
                        continue
                    # Find header row
                    header = None
                    for i, row in enumerate(table):
                        row_lower = [str(cell).lower() if cell else '' for cell in row]
                        if 'name' in row_lower and any(x in ''.join(row_lower) for x in ['cash', 'burn', 'growth']):
                            header = row_lower
                            data_rows = table[i+1:]
                            break

                    if header:
                        for row in data_rows:
                            if not row or not any(row):
                                continue
                            record = {}
                            for j, cell in enumerate(row):
                                if j < len(header):
                                    # Normalize: remove (€) or any parentheses, lowercase, replace spaces/hyphens with underscores
                                    col = re.sub(r'\s*\([^)]*\)', '', header[j]).strip().lower().replace(' ', '_').replace('-', '_')
                                    record[col] = cell
                            if record.get('name'):
                                records.append(record)

                # Fallback: parse text for key-value patterns if no tables found
                if not records:
                    text = page.extract_text() or ''
                    # Look for patterns like "Name: StartupX, Cash: 1000000"
                    startup_blocks = re.split(r'\n(?=name\s*[:\-])', text, flags=re.IGNORECASE)
                    for block in startup_blocks:
                        record = {}
                        for field in ['name', 'cash', 'monthly_burn', 'revenue_growth']:
                            pattern = rf'{field}\s*[:\-]\s*([^\n,;]+)'
                            match = re.search(pattern, block, re.IGNORECASE)
                            if match:
                                record[field] = match.group(1).strip()
                        if record.get('name'):
                            records.append(record)
    except Exception as e:
        print(f"PDF parsing error: {e}")
        sys.exit(1)

    if not records:
        print("No startup data found in PDF. Expected table or key-value format.")
        sys.exit(1)

    df = pd.DataFrame(records)

    # Convert numeric columns
    for col in ['cash', 'monthly_burn', 'revenue_growth']:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: _parse_number(x) if pd.notna(x) else None)

    required = ['name', 'cash', 'monthly_burn', 'revenue_growth']
    missing = [c for c in required if c not in df.columns]
    if missing:
        print(f"Missing required fields in PDF: {', '.join(missing)}")
        sys.exit(1)

    return df


def _parse_number(value):
    """Converts string to number, handling currency symbols and formats."""
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).replace(',', '').replace('€', '').replace('$', '').replace('%', '').strip()
    try:
        return float(s)
    except ValueError:
        return None


def parse_pdf_with_ai(filepath: str, provider: str) -> pd.DataFrame:
    """
    Extracts startup data from a PDF using AI-powered analysis.
    Uses litellm for unified API access across multiple providers.
    Returns DataFrame with columns: name, cash, monthly_burn, revenue_growth
    """
    try:
        from litellm import completion
    except ImportError:
        print("litellm not installed. Run: pip install litellm")
        sys.exit(1)

    model_id, env_var = PROVIDERS[provider]

    if not os.environ.get(env_var):
        print(f"{env_var} not set for provider '{provider}'")
        sys.exit(1)

    # Extract text from PDF with page limit
    text_content = ""
    try:
        with pdfplumber.open(filepath) as pdf:
            total_pages = len(pdf.pages)

            # Cap pages at 50 to prevent expensive API calls on large documents
            # Most pitch decks are <20 pages; financial data is typically early in doc
            if total_pages > MAX_PDF_PAGES:
                print(f"⚠️  PDF has {total_pages} pages. Processing first {MAX_PDF_PAGES} to control costs.")
                pages_to_process = pdf.pages[:MAX_PDF_PAGES]
            else:
                pages_to_process = pdf.pages

            for page in pages_to_process:
                page_text = page.extract_text()
                if page_text:
                    text_content += page_text + "\n"
    except Exception as e:
        print(f"PDF reading error: {e}")
        sys.exit(1)

    if not text_content.strip():
        print("No text content found in PDF")
        sys.exit(1)

    # Cost estimation and confirmation
    estimated_cost = estimate_cost(text_content, provider)
    if estimated_cost > 0.10 and provider != 'groq':
        print(f"⚠️  Estimated cost: ${estimated_cost:.2f} ({provider})")
        response = input("Continue? [y/N]: ").strip().lower()
        if response != 'y':
            print("Aborted by user.")
            sys.exit(0)

    prompt = f"""Extract startup financial data from this document. Return ONLY valid JSON array.

Each startup needs these exact fields:
- name: company name (string)
- cash: total cash/funding in numeric form (number, no currency symbols)
- monthly_burn: monthly burn rate in numeric form (number, no currency symbols)
- revenue_growth: monthly revenue growth as decimal (e.g., 0.15 for 15%)

Document content:
{text_content}

Return format (JSON array only, no markdown):
[{{"name": "...", "cash": ..., "monthly_burn": ..., "revenue_growth": ...}}]"""

    try:
        response = completion(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        result = response.choices[0].message.content.strip()

        # Clean response (remove markdown code blocks if present)
        if result.startswith("```"):
            result = re.sub(r'^```(?:json)?\n?', '', result)
            result = re.sub(r'\n?```$', '', result)

        data = json.loads(result)
        if not isinstance(data, list):
            data = [data]

    except json.JSONDecodeError as e:
        print(f"AI returned invalid JSON: {e}")
        print(f"   Response: {result[:200]}...")
        sys.exit(1)
    except Exception as e:
        print(f"AI extraction error: {e}")
        sys.exit(1)

    if not data:
        print("AI found no startup data in document")
        sys.exit(1)

    df = pd.DataFrame(data)

    # Validate required fields
    required = ['name', 'cash', 'monthly_burn', 'revenue_growth']
    missing = [c for c in required if c not in df.columns]
    if missing:
        print(f"AI extraction missing fields: {', '.join(missing)}")
        sys.exit(1)

    # Ensure numeric types
    for col in ['cash', 'monthly_burn', 'revenue_growth']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    print(f"🤖 AI extraction ({provider}): Found {len(df)} startup(s)")
    return df


def load_data(filepath: str, use_ai: bool = False, provider: str | None = None) -> pd.DataFrame:
    """Loads data from CSV or PDF based on file extension."""
    ext = os.path.splitext(filepath)[1].lower()

    if ext == '.csv':
        try:
            return pd.read_csv(filepath)
        except FileNotFoundError:
            print(f"File not found: {filepath}")
            sys.exit(1)
    elif ext == '.pdf':
        if use_ai:
            return parse_pdf_with_ai(filepath, provider)
        return parse_pdf(filepath)
    else:
        print(f"Unsupported file type: {ext}. Use .csv or .pdf")
        sys.exit(1)


def analyze_data(df: pd.DataFrame) -> dict:
    """
    Analyzes startup data DataFrame.
    Expected columns: name, cash, monthly_burn, revenue_growth
    """
    # Filter for valid burn rates when calculating runway
    valid_burn = df[df['monthly_burn'] > 0]
    valid_count = len(valid_burn)

    # Base calculations
    results = {
        'startup_count': len(df),
        'avg_burn_rate': df['monthly_burn'].mean(),
        'avg_runway': (valid_burn['cash'] / valid_burn['monthly_burn']).mean() if valid_count > 0 else None,
        'runway_based_on': valid_count if valid_count < len(df) else None,
        'total_cash': df['cash'].sum(),
        'top_growers': []
    }

    # Top 3 growth
    if 'revenue_growth' in df.columns:
        top_3 = df.nlargest(3, 'revenue_growth')
        results['top_growers'] = top_3[['name', 'revenue_growth']].to_dict('records')

    return results


def check_data_quality(df: pd.DataFrame) -> list:
    """
    Checks for suspicious data points and returns warnings.
    Returns list of (company_name, warning_message) tuples.
    """
    warnings = []

    for _, row in df.iterrows():
        name = row['name']
        cash = row['cash']
        burn = row['monthly_burn']
        growth = row['revenue_growth']

        # Critical: Less than 1 month runway (check first as highest priority)
        if burn > 0 and cash / burn < 1:
            warnings.append((name, "CRITICAL: Less than 1 month runway"))
        # Zero or negative burn rate
        elif burn <= 0:
            warnings.append((name, "Zero or negative burn rate - incomplete data?"))
        # Unusually long runway (>120 months = 10 years)
        elif burn > 0 and cash / burn > 120:
            warnings.append((name, "Unusually long runway - verify burn rate"))

        # Significant negative growth (worse than -50%)
        if pd.notna(growth) and growth < -0.5:
            warnings.append((name, "Significant negative growth - verify data"))

    return warnings[:4]  # Max 4 warnings


def generate_report(df: pd.DataFrame) -> str:
    """
    Generates a formatted report string from startup data.

    Args:
        df: DataFrame with columns: name, cash, monthly_burn, revenue_growth

    Returns:
        Formatted report string
    """
    results = analyze_data(df)
    warnings = check_data_quality(df)

    lines = []
    lines.append("=" * 50)
    lines.append("📊 VC DUE DILIGENCE REPORT")
    lines.append("=" * 50)
    lines.append(f"Startups analyzed: {results['startup_count']}")
    lines.append(f"Total Cash: €{results['total_cash']:,.0f}")
    lines.append(f"🔥 Avg Burn Rate: €{results['avg_burn_rate']:,.0f}/month")

    if results['avg_runway'] is not None:
        runway_str = f"⏳ Avg Runway: {results['avg_runway']:.1f} months"
        if results.get('runway_based_on') is not None:
            runway_str += f" (based on {results['runway_based_on']} startups)"
        lines.append(runway_str)
    else:
        lines.append("⏳ Avg Runway: N/A (no valid burn rates)")

    if results['top_growers']:
        lines.append("🚀 TOP GROWTH STARTUPS:")
        for startup in results['top_growers']:
            growth_pct = startup['revenue_growth'] * 100
            lines.append(f"   • {startup['name']}: {growth_pct:.1f}% MoM")

    lines.append("=" * 50)

    if warnings:
        lines.append("")
        lines.append("🚩 DATA QUALITY WARNINGS:")
        for name, message in warnings:
            lines.append(f"   • {name}: {message}")

    return "\n".join(lines)


def print_warnings(warnings: list):
    """Prints data quality warnings if any exist."""
    if not warnings:
        return

    print("🚩 DATA QUALITY WARNINGS:")
    for name, message in warnings:
        print(f"   • {name}: {message}")
    print()

def print_report(results: dict):
    """Formats and prints the analysis report."""
    print("\n" + "="*50)
    print("📊 VC DUE DILIGENCE REPORT")
    print("="*50)
    print(f"Startups analyzed: {results['startup_count']}")
    print(f"Total Cash: €{results['total_cash']:,.0f}")
    print(f"🔥 Avg Burn Rate: €{results['avg_burn_rate']:,.0f}/month")
    if results['avg_runway'] is not None:
        runway_str = f"⏳ Avg Runway: {results['avg_runway']:.1f} months"
        if results.get('runway_based_on') is not None:
            runway_str += f" (based on {results['runway_based_on']} startups)"
        print(runway_str)
    else:
        print("⏳ Avg Runway: N/A (no valid burn rates)")

    if results['top_growers']:
        print("🚀 TOP GROWTH STARTUPS:")
        for startup in results['top_growers']:
            growth_pct = startup['revenue_growth'] * 100
            print(f"   • {startup['name']}: {growth_pct:.1f}% MoM")

    print("="*50 + "\n")

def main():
    parser = argparse.ArgumentParser(
        description="VC Due Diligence - Financial KPI Extraction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python extract.py data/startups.csv           # Standard CSV analysis
  python extract.py data/report.pdf             # Standard PDF parsing
  python extract.py data/report.pdf --ai        # AI extraction (auto-detect provider)
  python extract.py data/report.pdf --ai --provider openai
  python extract.py data/*.pdf                  # Batch process multiple files
  python extract.py file1.csv file2.pdf --output results.json
        """
    )
    parser.add_argument(
        "files",
        nargs="*",
        default=["data/startups.csv"],
        help="Input file(s) (CSV or PDF). Default: data/startups.csv"
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Save combined results to JSON file"
    )
    parser.add_argument(
        "--ai",
        action="store_true",
        help="Use AI-powered extraction for PDF files"
    )
    parser.add_argument(
        "--provider",
        choices=["anthropic", "openai", "google", "groq", "mistral", "deepseek", "auto"],
        default="auto",
        help="AI provider (default: auto-detect from available API keys)"
    )

    args = parser.parse_args()

    # Handle empty files list (use default)
    files = args.files if args.files else ["data/startups.csv"]

    # Handle AI mode
    provider = None
    if args.ai:
        if args.provider == "auto":
            provider = detect_provider()
            if not provider:
                print(get_provider_error_message())
                sys.exit(1)
        else:
            provider = args.provider
            _, env_var = PROVIDERS[provider]
            if not os.environ.get(env_var):
                print(f"{env_var} not set for provider '{provider}'")
                print(get_provider_error_message())
                sys.exit(1)

    # Single file processing (original behavior)
    if len(files) == 1:
        print(f"📁 Analyzing: {files[0]}")
        df = load_data(files[0], use_ai=args.ai, provider=provider)
        results = analyze_data(df)
        print_report(results)
        warnings = check_data_quality(df)
        print_warnings(warnings)

        # Save to JSON if --output specified
        if args.output:
            output_data = {
                "processed_at": datetime.now().isoformat(),
                "files_processed": 1,
                "results": results,
                "startups": df.to_dict('records')
            }
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2, cls=NumpyEncoder)
            print(f"📄 Results saved to: {args.output}")
        return

    # Batch processing for multiple files
    print(f"📁 Batch processing {len(files)} file(s)...")
    all_dfs = []
    successful = 0
    failed = 0

    # Process each file independently; failures don't block subsequent files
    for filepath in tqdm(files, desc="Processing files"):
        try:
            df = load_data(filepath, use_ai=args.ai, provider=provider)
            all_dfs.append(df)
            successful += 1
        except SystemExit:
            # load_data calls sys.exit on error, catch and continue batch
            failed += 1
            tqdm.write(f"  ✗ Failed: {filepath}")
        except Exception as e:
            failed += 1
            tqdm.write(f"  ✗ Failed: {filepath} ({e})")

    print(f"\n✓ {successful}/{len(files)} files processed successfully")

    if not all_dfs:
        print("No files were processed successfully.")
        sys.exit(1)

    # Combine all DataFrames
    combined_df = pd.concat(all_dfs, ignore_index=True)
    results = analyze_data(combined_df)
    print_report(results)
    warnings = check_data_quality(combined_df)
    print_warnings(warnings)

    # Save to JSON if --output specified
    if args.output:
        output_data = {
            "processed_at": datetime.now().isoformat(),
            "files_processed": successful,
            "results": results,
            "startups": combined_df.to_dict('records')
        }
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2, cls=NumpyEncoder)
        print(f"📄 Results saved to: {args.output}")


if __name__ == "__main__":
    main()
