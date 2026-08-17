from engine.financial_analysis import (
    calculate_annual_revenue,
    calculate_project_cost,
    calculate_payback_period,
    calculate_roi,
    calculate_financial_analysis,
)


# ================================================================
# TEST 1 — ANNUAL REVENUE
# ================================================================

def test_annual_revenue():

    revenue = calculate_annual_revenue(
        annual_energy_yield_kwh=100_000,
        electricity_tariff_inr_per_kwh=5.0,
    )

    assert revenue == 500_000.0

    print("PASS: test_annual_revenue")


# ================================================================
# TEST 2 — PROJECT COST
# ================================================================

def test_project_cost():

    cost = calculate_project_cost(
        installed_capacity_mw=10,
        cost_per_mw=5_000_000,
    )

    assert cost == 50_000_000.0

    print("PASS: test_project_cost")


# ================================================================
# TEST 3 — ADDITIONAL INSTALLATION COST
# ================================================================

def test_additional_installation():

    cost = calculate_project_cost(
        installed_capacity_mw=10,
        cost_per_mw=5_000_000,
        additional_installation_percent=10,
    )

    assert cost == 55_000_000.0

    print("PASS: test_additional_installation")


# ================================================================
# TEST 4 — PAYBACK
# ================================================================

def test_payback():

    payback = calculate_payback_period(
        total_project_cost=50_000_000,
        annual_revenue=10_000_000,
    )

    assert payback == 5.0

    print("PASS: test_payback")


# ================================================================
# TEST 5 — ZERO REVENUE
# ================================================================

def test_zero_revenue():

    payback = calculate_payback_period(
        total_project_cost=50_000_000,
        annual_revenue=0,
    )

    assert payback is None

    print("PASS: test_zero_revenue")


# ================================================================
# TEST 6 — ROI
# ================================================================

def test_roi():

    roi = calculate_roi(
        total_project_cost=50_000_000,
        annual_revenue=10_000_000,
    )

    assert roi == 20.0

    print("PASS: test_roi")


# ================================================================
# TEST 7 — HIGHER TARIFF
# ================================================================

def test_higher_tariff_increases_revenue():

    low_tariff = calculate_annual_revenue(
        annual_energy_yield_kwh=100_000,
        electricity_tariff_inr_per_kwh=4,
    )

    high_tariff = calculate_annual_revenue(
        annual_energy_yield_kwh=100_000,
        electricity_tariff_inr_per_kwh=8,
    )

    assert high_tariff > low_tariff

    print(
        "PASS: test_higher_tariff_increases_revenue"
    )


# ================================================================
# TEST 8 — HIGHER CAPACITY INCREASES COST
# ================================================================

def test_higher_capacity_increases_cost():

    small = calculate_project_cost(
        installed_capacity_mw=10,
        cost_per_mw=5_000_000,
    )

    large = calculate_project_cost(
        installed_capacity_mw=20,
        cost_per_mw=5_000_000,
    )

    assert large > small

    print(
        "PASS: test_higher_capacity_increases_cost"
    )


# ================================================================
# TEST 9 — COMPLETE FINANCIAL ANALYSIS
# ================================================================

def test_complete_financial_analysis():

    result = calculate_financial_analysis(
        annual_energy_yield_kwh=100_000,
        installed_capacity_mw=10,
        electricity_tariff_inr_per_kwh=5,
        cost_per_mw=5_000_000,
    )

    assert result[
        "estimated_annual_revenue"
    ] == 500_000.0

    assert result[
        "estimated_project_cost"
    ] == 50_000_000.0

    assert result[
        "payback_period_years"
    ] == 100.0

    assert result[
        "roi_percent"
    ] == 1.0

    print(
        "PASS: test_complete_financial_analysis"
    )


# ================================================================
# TEST 10 — INVALID NEGATIVE VALUES
# ================================================================

def test_negative_values():

    try:
        calculate_annual_revenue(
            annual_energy_yield_kwh=-100,
            electricity_tariff_inr_per_kwh=5,
        )
        assert False

    except ValueError:
        pass

    try:
        calculate_project_cost(
            installed_capacity_mw=-10,
            cost_per_mw=5_000_000,
        )
        assert False

    except ValueError:
        pass

    print(
        "PASS: test_negative_values"
    )


# ================================================================
# MAIN
# ================================================================

def main():

    print()
    print("======================================")
    print("FINANCIAL ANALYSIS VALIDATION")
    print("======================================")
    print()

    test_annual_revenue()
    test_project_cost()
    test_additional_installation()
    test_payback()
    test_zero_revenue()
    test_roi()
    test_higher_tariff_increases_revenue()
    test_higher_capacity_increases_cost()
    test_complete_financial_analysis()
    test_negative_values()

    print()
    print("======================================")
    print("ALL FINANCIAL TESTS PASSED")
    print("======================================")


if __name__ == "__main__":
    main()