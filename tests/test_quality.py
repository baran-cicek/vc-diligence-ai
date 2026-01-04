"""
Tests for data quality validation functionality.
Tests the check_data_quality function for various warning conditions.
"""
import pytest
import pandas as pd
from vc_diligence.extract import check_data_quality


def test_long_runway_warning():
    """Test warning for unusually long runway (>120 months)"""
    df = pd.DataFrame([{
        'name': 'LongRunwayStartup',
        'cash': 1500000,
        'monthly_burn': 10000,  # 150 months runway
        'revenue_growth': 0.10
    }])

    warnings = check_data_quality(df)

    assert len(warnings) > 0
    assert any('LongRunwayStartup' in w[0] and 'long runway' in w[1].lower() for w in warnings)


def test_zero_burn_rate_warning():
    """Test warning for zero burn rate"""
    df = pd.DataFrame([{
        'name': 'ZeroBurnStartup',
        'cash': 500000,
        'monthly_burn': 0,
        'revenue_growth': 0.15
    }])

    warnings = check_data_quality(df)

    assert len(warnings) > 0
    assert any('ZeroBurnStartup' in w[0] and ('zero' in w[1].lower() or 'burn' in w[1].lower()) for w in warnings)


def test_negative_growth_warning():
    """Test warning for significant negative growth (<-0.5)"""
    df = pd.DataFrame([{
        'name': 'DeclineStartup',
        'cash': 300000,
        'monthly_burn': 25000,
        'revenue_growth': -0.6  # -60% growth
    }])

    warnings = check_data_quality(df)

    assert len(warnings) > 0
    assert any('DeclineStartup' in w[0] and 'growth' in w[1].lower() for w in warnings)


def test_critical_runway_warning():
    """Test critical warning for runway less than 1 month"""
    df = pd.DataFrame([{
        'name': 'CriticalStartup',
        'cash': 20000,
        'monthly_burn': 30000,  # Less than 1 month
        'revenue_growth': 0.05
    }])

    warnings = check_data_quality(df)

    assert len(warnings) > 0
    # Should have CRITICAL warning
    assert any('CriticalStartup' in w[0] and 'CRITICAL' in w[1] for w in warnings)


def test_normal_data_no_warnings():
    """Test that normal data produces no warnings"""
    df = pd.DataFrame([{
        'name': 'HealthyStartup',
        'cash': 500000,
        'monthly_burn': 50000,  # 10 months runway
        'revenue_growth': 0.20  # 20% growth
    }])

    warnings = check_data_quality(df)

    # Should have no warnings for this healthy startup
    healthy_warnings = [w for w in warnings if 'HealthyStartup' in w[0]]
    assert len(healthy_warnings) == 0
