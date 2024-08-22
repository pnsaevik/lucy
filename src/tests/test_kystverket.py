from lucy.data import kystverket
import os
import pytest


username = os.getenv('KYSTVERKET_USERNAME')
password = os.getenv('KYSTVERKET_PASSWORD')


@pytest.mark.skipif(
    condition=username is None or password is None,
    reason="Username and/or password for Kystverket is not set",
)
class Test_ais:
    def test_returns_dataframe(self):
        df = kystverket.ais(
            user=username,
            passwd=password,
            mmsi=259016200,  # PIA
            start='2024-07-27 11:03',
            stop='2024-07-27 11:04',
        )
        assert len(df) > 0
        assert list(df.columns) == [
            'mmsi', 'datetime_utc', 'longitude', 'latitude',
            'course_over_ground', 'speed_over_ground', 'message_number',
            'calc_speed', 'sec_to_previous', 'dist_to_previous',
        ]