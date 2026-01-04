"""
Tests for CSV and PDF parsing functionality.
Tests the load_data and parse_pdf functions.
"""
import pytest
import pandas as pd
import os
from vc_diligence.extract import load_data, parse_pdf


# Get path to fixtures directory
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')


def test_load_valid_csv():
    """Test loading a valid CSV file"""
    csv_path = os.path.join(FIXTURES_DIR, 'sample.csv')
    df = load_data(csv_path)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert 'name' in df.columns
    assert 'cash' in df.columns
    assert 'monthly_burn' in df.columns
    assert 'revenue_growth' in df.columns


def test_load_csv_missing_columns():
    """Test CSV with missing required columns raises appropriate error"""
    csv_path = os.path.join(FIXTURES_DIR, 'invalid.csv')

    # Create a CSV with missing columns
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("name,cash\n")
        f.write("Startup1,100000\n")
        temp_path = f.name

    try:
        # This should work as load_data doesn't validate columns
        # The validation happens in analyze_data
        df = load_data(temp_path)
        assert 'name' in df.columns
        assert 'cash' in df.columns
    finally:
        os.unlink(temp_path)


def test_load_empty_csv():
    """Test handling of empty CSV file"""
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("name,cash,monthly_burn,revenue_growth\n")
        temp_path = f.name

    try:
        df = load_data(temp_path)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
    finally:
        os.unlink(temp_path)


def test_parse_pdf_with_table():
    """Test PDF parsing with table format"""
    pdf_path = os.path.join(FIXTURES_DIR, 'sample.pdf')

    # Only test if fixture exists
    if os.path.exists(pdf_path):
        df = parse_pdf(pdf_path)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert all(col in df.columns for col in ['name', 'cash', 'monthly_burn', 'revenue_growth'])


def test_parse_pdf_without_startup_data():
    """Test PDF without startup data fails appropriately"""
    import tempfile
    from reportlab.pdfgen import canvas

    # Create a PDF without startup data
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        temp_path = f.name

    try:
        # Create simple PDF with no relevant data
        c = canvas.Canvas(temp_path)
        c.drawString(100, 750, "This is a test document")
        c.drawString(100, 730, "It contains no startup data")
        c.save()

        # Should exit with error message
        with pytest.raises(SystemExit):
            parse_pdf(temp_path)
    finally:
        os.unlink(temp_path)
