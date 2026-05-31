from datetime import datetime, timezone

from wavecal.models import AltimeterRecord, BuoyRecord
from wavecal.qc import filter_altimeter, filter_buoy


def test_altimeter_qc_rejects_nan_and_source_flags():
    records = [
        AltimeterRecord(
            time=datetime(2020, 1, 1, tzinfo=timezone.utc),
            lat=0,
            lon=0,
            swh_m=float("nan"),
        ),
        AltimeterRecord(
            time=datetime(2020, 1, 1, 1, tzinfo=timezone.utc),
            lat=0,
            lon=0,
            swh_m=2.0,
            rain_flag="rain",
        ),
        AltimeterRecord(
            time=datetime(2020, 1, 1, 2, tzinfo=timezone.utc),
            lat=0,
            lon=0,
            swh_m=2.5,
            swh_numval=20,
            quality_flag="good",
        ),
    ]
    filtered = filter_altimeter(
        records,
        min_swh_numval=17,
        reject_rain_flags={"rain"},
        reject_quality_flags={"bad"},
    )
    assert len(filtered) == 1
    assert filtered[0].swh_m == 2.5


def test_buoy_qc_rejects_flags_and_short_window_spikes():
    records = [
        BuoyRecord(
            time=datetime(2020, 1, 1, 0, tzinfo=timezone.utc),
            station_id="station",
            lat=0,
            lon=0,
            swh_m=2.0,
            qc_flag="good",
        ),
        BuoyRecord(
            time=datetime(2020, 1, 1, 1, tzinfo=timezone.utc),
            station_id="station",
            lat=0,
            lon=0,
            swh_m=9.0,
            qc_flag="good",
        ),
        BuoyRecord(
            time=datetime(2020, 1, 1, 2, tzinfo=timezone.utc),
            station_id="station",
            lat=0,
            lon=0,
            swh_m=2.3,
            qc_flag="bad",
        ),
    ]
    filtered = filter_buoy(
        records,
        reject_qc_flags={"bad"},
        max_swh_jump_m=3.0,
        jump_window_hours=2.0,
    )
    assert [record.swh_m for record in filtered] == [2.0]
