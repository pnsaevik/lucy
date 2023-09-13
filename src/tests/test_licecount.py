from lucy import licecount
import pandas as pd
import pytest


class Test_cleanup_lice:
    @pytest.fixture()
    def lice_df(self):
        return pd.DataFrame(data={
            "Fastsittende lus": [1., 2., 3., 4., 5., 6.],
            "Lus i bevegelige stadier": [1., 2., 3., 4., 5., 6.],
            "Voksne hunnlus": [1., 2., 3., 4., 5., 6.],
            "Lokalitetsnummer": [10, 10, 10, 20, 20, 20],
            "Uke": [5, 6, 7, 5, 6, 7],
            "År": 2020,
        })

    def test_includes_the_same_columns(self, lice_df):
        df = licecount.fill_missing_lice(lice_df)
        assert set(lice_df.columns) - set(df.columns) == set()

    def test_adds_two_weeks(self, lice_df):
        df = licecount.fill_missing_lice(lice_df)
        assert df.iloc[-2:]["Uke"].values.tolist() == [8, 9]

    def test_interpolates_missing_licecount(self, lice_df):
        lice_df.loc[1, "Voksne hunnlus"] = float('nan')
        df = licecount.fill_missing_lice(lice_df)
        assert df.loc[1, "Voksne hunnlus"] == 2

    def test_interpolates_missing_row(self, lice_df):
        df = licecount.fill_missing_lice(lice_df.iloc[[0, 2, 3, 4, 5]])
        assert df.loc[1, "Uke"] == 6
        assert df.loc[1, "Voksne hunnlus"] == 2

    def test_indicates_if_value_is_interpolated(self, lice_df):
        lice_df.loc[1, "Voksne hunnlus"] = float('nan')
        df = licecount.fill_missing_lice(lice_df)
        assert df["Interpolert"].values.tolist() == [0, 1, 0, 1, 1, 0, 0, 0, 1, 1]
