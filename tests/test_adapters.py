from pathlib import Path

from wavecal.adapters import read_altimeter_csv, read_buoy_csv, read_legacy_txt


def test_read_normalized_csv_examples():
    altimeter = read_altimeter_csv("examples/data/scilly_altimeter_sample.csv")
    buoy = read_buoy_csv("examples/data/scilly_buoy_sample.csv")
    assert len(altimeter) == 32
    assert len(buoy) == 32
    assert altimeter[0].mission == "Jason-3"
    assert buoy[0].station_id == "sw-isles-of-scilly-wavenet"


def test_read_legacy_txt_four_column_fallback(tmp_path: Path):
    legacy = tmp_path / "parameter_0_25km.txt"
    legacy.write_text(
        "cycle_number\tpass_number\tlon\tlat\talt\torb_alt_rate\trange_ku\trange_c\trange_rms_ku\trange_numval_ku\tswh_ku\tswh_rms_ku\tswh_numval_ku\tbathymetry\ttime\n"
        "3.584\t0.651\t20.000\t508968900.65382409\n",
        encoding="utf-8",
    )
    records = read_legacy_txt(legacy, lat=49.9, lon=-6.5, window_name="0-25km")
    assert len(records) == 1
    assert records[0].swh_m == 3.584
    assert records[0].swh_numval == 20
    assert records[0].window_name == "0-25km"
    assert records[0].time.year == 2016
