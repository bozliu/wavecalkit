from wavecal.geo import haversine_km, normalize_longitude_180, west_longitude_to_360


def test_west_longitude_to_360():
    assert abs(west_longitude_to_360(6.19793888888889) - 353.8020611111111) < 1e-12


def test_normalize_longitude_180():
    assert abs(normalize_longitude_180(353.8020611111111) - -6.197938888888899) < 1e-12


def test_haversine_known_scale():
    distance = haversine_km(49.816667, -6.545167, 49.90650, -6.545167)
    assert 9.9 < distance < 10.1
