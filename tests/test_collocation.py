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
