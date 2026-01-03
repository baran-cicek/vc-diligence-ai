#!/usr/bin/env python3
"""
VC Due Diligence CLI - Financial KPI Extraction

This is a CLI wrapper that imports from the vc_diligence package.
For programmatic usage, import directly: from vc_diligence.extract import load_data, generate_report
"""
import sys
import os

# Add repo root to path for running without pip install
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vc_diligence.extract import main

if __name__ == "__main__":
    main()
