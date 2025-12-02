#!/usr/bin/env python3
"""
VC Due Diligence MVP - Einfachster CSV Analyzer
"""
import pandas as pd
import sys

def analyze_csv(filepath: str) -> dict:
    """
    Analysiert eine CSV mit Startup-Daten.
    Erwartete Spalten: name, cash, monthly_burn, revenue_growth
    """
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"❌ Datei nicht gefunden: {filepath}")
        sys.exit(1)
    
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
        csv_file = sys.argv[1]
    else:
        csv_file = "data/startups.csv"
    
    print(f"📁 Analysiere: {csv_file}")
    results = analyze_csv(csv_file)
    print_report(results)
