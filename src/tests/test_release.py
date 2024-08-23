from lucy import release
import pytest
import pandas as pd
import numpy as np


@pytest.fixture()
def df_biomass():
    return pd.DataFrame(dict(
        endTime=['2023-12-31 23:00'] * 2,
        reportTime=['2024-01-05 12:00'] * 2,
        reportReceipt=['AR1234', 'AR2345'],
        siteNr=[12345, 23456],
        specieCode=['071101'] * 2,
        numFish=[132435, 213243],
        avgWeight=[0.1, 0.1],
        organization=["123412341234", "4124215234213"],
        mainOperator=["123412341234", "4124215234213"],
    ))


@pytest.fixture()
def df_lice():
    return pd.DataFrame(dict(
            farmid=[12345, 12345, 23456],
            naf=[0.1, 0.2, 0.3],
            npa=[0.01, 0.02, 0.03],
            nch=[0.04, 0.05, 0.06],
            Lat=[60, 60, 70],
            Lon=[4, 4, 5],
            temp=[6, 7, 8],
            date=np.array([
                '2024-01-01',
                '2024-01-08',
                '2024-01-01',
            ]).astype('datetime64[ns]'),
        ))


class Test_create_licebiomass:
    def test_returns_expected_result(self, df_biomass, df_lice):
        result = release.create_licebiomass(df_biomass, df_lice)
        assert result == (
            'Fishfarm: 12345  (60.0,4.0)\n'
            '2024 01 01 132435.0 0.1 - null null null null\n'
            '2024 01 01 null null - 6.0 0.04 0.01 0.1\n'
            '2024 01 08 null null - 7.0 0.05 0.02 0.2\n'
            'Fishfarm: 23456  (70.0,5.0)\n'
            '2024 01 01 213243.0 0.1 - null null null null\n'
            '2024 01 01 null null - 8.0 0.06 0.03 0.3\n')
