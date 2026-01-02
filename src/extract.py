#!/usr/bin/env python3
"""
VC Due Diligence MVP - CSV & PDF Analyzer
"""
import pandas as pd
import pdfplumber
import re
import sys
import os

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
                                    col = header[j].replace(' ', '_').replace('-', '_')
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
        print(f"❌ PDF parsing error: {e}")
        sys.exit(1)

    if not records:
        print("❌ No startup data found in PDF. Expected table or key-value format.")
        sys.exit(1)

    df = pd.DataFrame(records)

    # Convert numeric columns
    for col in ['cash', 'monthly_burn', 'revenue_growth']:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: _parse_number(x) if pd.notna(x) else None)

    required = ['name', 'cash', 'monthly_burn', 'revenue_growth']
    missing = [c for c in required if c not in df.columns]
    if missing:
        print(f"❌ Missing required fields in PDF: {', '.join(missing)}")
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


def load_data(filepath: str) -> pd.DataFrame:
    """Loads data from CSV or PDF based on file extension."""
    ext = os.path.splitext(filepath)[1].lower()

    if ext == '.csv':
        try:
            return pd.read_csv(filepath)
        except FileNotFoundError:
            print(f"❌ Datei nicht gefunden: {filepath}")
            sys.exit(1)
    elif ext == '.pdf':
        return parse_pdf(filepath)
    else:
        print(f"❌ Unsupported file type: {ext}. Use .csv or .pdf")
        sys.exit(1)


def analyze_data(df: pd.DataFrame) -> dict:
    """
    Analyzes startup data DataFrame.
    Expected columns: name, cash, monthly_burn, revenue_growth
    """
    # Basis-Berechnungen
    results = {
        'startup_count': len(df),
        'avg_burn_rate': df['monthly_burn'].mean(),
        'avg_runway': (df['cash'] / df['monthly_burn']).mean(),
        'total_cash': df['cash'].sum(),
        'top_growers': []
    }

    # Top 3 Wachstum
    if 'revenue_growth' in df.columns:
        top_3 = df.nlargest(3, 'revenue_growth')
        results['top_growers'] = top_3[['name', 'revenue_growth']].to_dict('records')

    return results

def print_report(results: dict):
    """Formatiert die Ergebnisse schön."""
    print("\n" + "="*50)
    print("📊 VC DUE DILIGENCE REPORT")
    print("="*50)
    print(f"Startups analysiert: {results['startup_count']}")
    print(f"Gesamt Cash: €{results['total_cash']:,.0f}")
    print(f"🔥 Durchschn. Burn Rate: €{results['avg_burn_rate']:,.0f}/Monat")
    print(f"⏳ Durchschn. Runway: {results['avg_runway']:.1f} Monate")
    
    if results['top_growers']:
        print("\n🚀 TOP WACHSTUMS-STARTUPS:")
        for startup in results['top_growers']:
            growth_pct = startup['revenue_growth'] * 100
            print(f"   • {startup['name']}: {growth_pct:.1f}% MoM")
    
    print("="*50 + "\n")

if __name__ == "__main__":
    # Einfache CLI
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = "data/startups.csv"

    print(f"📁 Analysiere: {input_file}")
    df = load_data(input_file)
    results = analyze_data(df)
    print_report(results)
