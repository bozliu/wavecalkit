from datetime import datetime, timezone

from wavecal.collocation import assign_window, collocate, parse_window_specs
from wavecal.models import AltimeterRecord, BuoyRecord


def test_window_assignment():
    windows = parse_window_specs(["0-25", "25-50", "50-75", "75-100"])
    assert assign_window(10, windows) == "0-25km"
    assert assign_window(25, windows) == "25-50km"
    assert assign_window(100, windows) is None


def test_exact_and_tolerance_collocation():
    windows = parse_window_specs(["0-25"])
    alt = [
        AltimeterRecord(
            time=datetime(2020, 1, 1, 0, 10, tzinfo=timezone.utc),
            lat=49.90650,
            lon=-6.545167,
            swh_m=2.0,
        )
    ]
    buoy = [
        BuoyRecord(
            time=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc),
            station_id="station",
            lat=49.816667,
            lon=-6.545167,
            swh_m=1.8,
        )
    ]
    assert collocate(alt, buoy, station_lat=49.816667, station_lon=-6.545167, windows=windows) == []
    pairs = collocate(
        alt,
        buoy,
        station_lat=49.816667,
        station_lon=-6.545167,
        windows=windows,
        time_window="30min",
    )
    assert len(pairs) == 1
    assert pairs[0].delta_time_minutes == 10
    assert pairs[0].window_name == "0-25km"


def test_collocation_aggregation_modes():
    windows = parse_window_specs(["0-25"])
    buoy = [
        BuoyRecord(
            time=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc),
            station_id="station",
            lat=49.816667,
            lon=-6.545167,
            swh_m=2.0,
        )
    ]
    altimeter = [
        AltimeterRecord(
            time=datetime(2020, 1, 1, 0, minute, tzinfo=timezone.utc),
            lat=49.90650,
            lon=-6.545167,
            swh_m=swh,
        )
        for minute, swh in [(5, 1.8), (10, 2.2), (15, 2.6)]
    ]
    mean_pairs = collocate(
        altimeter,
        buoy,
        station_lat=49.816667,
        station_lon=-6.545167,
        windows=windows,
        time_window="30min",
        aggregation="mean",
    )
    assert len(mean_pairs) == 1
    assert mean_pairs[0].matched_altimeter_count == 3
    assert abs(mean_pairs[0].altimeter.swh_m - 2.2) < 1e-12

    nearest_pairs = collocate(
        altimeter,
        buoy,
        station_lat=49.816667,
        station_lon=-6.545167,
        windows=windows,
        time_window="30min",
        aggregation="nearest",
    )
    assert nearest_pairs[0].altimeter.swh_m == 1.8
    assert nearest_pairs[0].matched_altimeter_count == 3
