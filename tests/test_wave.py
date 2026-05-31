from wavecal.wave import deep_water_wave_power_kw_per_m


def test_wave_power_screening_formula():
    value = deep_water_wave_power_kw_per_m(2.0, 8.0)
    assert value is not None
    assert 15.5 < value < 16.0
    assert deep_water_wave_power_kw_per_m(2.0, None) is None
    assert deep_water_wave_power_kw_per_m(-1.0, 8.0) is None
