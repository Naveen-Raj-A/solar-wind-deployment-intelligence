"""Validation tests for the Energy Yield Service."""

from engine.energy_yield import (
    estimate_hybrid_energy_yield,
    estimate_solar_energy_yield,
    estimate_wind_energy_yield,
)


def test_solar_yield_formula_and_losses():
    result = estimate_solar_energy_yield(
        installed_capacity_mw=10,
        capacity_factor=0.25,
        system_efficiency=0.95,
        operational_loss=0.05,
    )

    expected = 10 * 8760 * 0.25 * 0.95 * 0.95
    assert result["annual_energy_mwh"] == round(expected, 2)


def test_higher_solar_irradiance_increases_yield():
    low = estimate_solar_energy_yield(
        installed_capacity_mw=10,
        solar_irradiance_kwh_m2_day=4.0,
    )
    high = estimate_solar_energy_yield(
        installed_capacity_mw=10,
        solar_irradiance_kwh_m2_day=6.0,
    )

    assert high["capacity_factor"] > low["capacity_factor"]
    assert high["annual_energy_mwh"] > low["annual_energy_mwh"]


def test_higher_wind_speed_increases_yield():
    low = estimate_wind_energy_yield(
        installed_capacity_mw=10,
        wind_speed_ms=5.0,
    )
    high = estimate_wind_energy_yield(
        installed_capacity_mw=10,
        wind_speed_ms=8.0,
    )

    assert high["capacity_factor"] > low["capacity_factor"]
    assert high["annual_energy_mwh"] > low["annual_energy_mwh"]


def test_capacity_factor_increases_yield():
    low = estimate_solar_energy_yield(
        installed_capacity_mw=10,
        capacity_factor=0.20,
    )
    high = estimate_solar_energy_yield(
        installed_capacity_mw=10,
        capacity_factor=0.30,
    )

    assert high["annual_energy_mwh"] > low["annual_energy_mwh"]


def test_hybrid_is_sum_of_components():
    result = estimate_hybrid_energy_yield(
        installed_capacity_mw=20,
        solar_capacity_factor=0.25,
        wind_capacity_factor=0.35,
        solar_capacity_share=0.50,
    )

    assert result["solar_capacity_mw"] == 10.0
    assert result["wind_capacity_mw"] == 10.0
    assert result["annual_energy_mwh"] == round(
        result["solar"]["annual_energy_mwh"]
        + result["wind"]["annual_energy_mwh"],
        2,
    )


def test_zero_operational_loss_increases_yield():
    lossy = estimate_solar_energy_yield(
        installed_capacity_mw=10,
        capacity_factor=0.25,
        system_efficiency=0.95,
        operational_loss=0.10,
    )
    clean = estimate_solar_energy_yield(
        installed_capacity_mw=10,
        capacity_factor=0.25,
        system_efficiency=0.95,
        operational_loss=0.0,
    )

    assert clean["annual_energy_mwh"] > lossy["annual_energy_mwh"]


if __name__ == "__main__":
    tests = [
        test_solar_yield_formula_and_losses,
        test_higher_solar_irradiance_increases_yield,
        test_higher_wind_speed_increases_yield,
        test_capacity_factor_increases_yield,
        test_hybrid_is_sum_of_components,
        test_zero_operational_loss_increases_yield,
    ]

    for test in tests:
        test()
        print(f"PASS: {test.__name__}")
