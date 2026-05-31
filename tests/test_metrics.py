from wavecal.adapters import read_altimeter_csv, read_buoy_csv
from wavecal.collocation import collocate, parse_window_specs
from wavecal.metrics import compute_metrics_for_pairs


def test_golden_legacy_regression_equations():
    pairs = collocate(
        read_altimeter_csv("examples/data/scilly_altimeter_sample.csv"),
        read_buoy_csv("examples/data/scilly_buoy_sample.csv"),
        station_lat=49.816667,
        station_lon=-6.545167,
        windows=parse_window_specs(["0-25", "25-50", "50-75", "75-100"]),
    )
    metrics = {item.window_name: item for item in compute_metrics_for_pairs(pairs)}
    expected = {
        "0-25km": (0.90, 0.14),
        "25-50km": (0.83, 0.21),
        "50-75km": (0.86, 0.17),
        "75-100km": (0.90, 0.08),
    }
    assert set(metrics) == set(expected)
    for window_name, (slope, intercept) in expected.items():
        assert abs(metrics[window_name].slope - slope) < 1e-9
        assert abs(metrics[window_name].intercept - intercept) < 1e-9
        assert metrics[window_name].n == 8
        assert metrics[window_name].r > 0.999
