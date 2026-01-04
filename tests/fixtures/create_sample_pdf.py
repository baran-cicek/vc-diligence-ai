#!/usr/bin/env python3
"""
Helper script to create a sample PDF with startup data table.
Run this to generate the sample.pdf fixture.
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import os

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(SCRIPT_DIR, 'sample.pdf')


def create_sample_pdf():
    """Create a sample PDF with startup data in table format"""
    doc = SimpleDocTemplate(OUTPUT_PATH, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    title = Paragraph("Startup Portfolio Report", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.3 * inch))

    # Create table data
    data = [
        ['Name', 'Cash (€)', 'Monthly Burn (€)', 'Revenue Growth'],
        ['TechStartup', '€500,000', '€50,000', '15%'],
        ['GrowthCo', '€1,000,000', '€80,000', '25%'],
    ]

    # Create table
    table = Table(data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])

    # Style the table
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))

    elements.append(table)

    # Build PDF
    doc.build(elements)
    print(f"Created sample PDF: {OUTPUT_PATH}")


if __name__ == '__main__':
    create_sample_pdf()
