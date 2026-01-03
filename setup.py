from setuptools import setup, find_packages

setup(
    name="vc-diligence-ai",
    version="1.0.0",
    description="Automated financial KPI extraction for venture capital due diligence",
    author="Baran Cicek",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "pandas>=2.0.0",
        "pdfplumber>=0.10.0",
        "litellm>=1.40.0",
    ],
)
