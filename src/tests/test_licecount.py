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

    def test_returns_verbatim_if_complete(self, lice_df):
        df = licecount.fill_missing_lice(lice_df)
        assert df.query('Uke <=7').iloc[:, :6].to_dict('list') == lice_df.to_dict('list')

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

    def test_does_not_interpolate_big_gaps(self, lice_df):
        lice_df.loc[2, "Uke"] = 10
        df = licecount.fill_missing_lice(lice_df)
        assert df["Voksne hunnlus"][:6].fillna(-1).values.tolist() == [
            1, 2, -1, -1, -1, 3,
        ]

    def test_indicates_if_value_is_interpolated(self, lice_df):
        lice_df.loc[1, "Voksne hunnlus"] = float('nan')
        df = licecount.fill_missing_lice(lice_df)
        assert df["Rådata mangler"].values.tolist() == [0, 1, 0, 1, 1, 0, 0, 0, 1, 1]


class Test_consecutive:
    def test_all_zeros(self):
        v = licecount.consecutive([0, 0, 0, 0])
        assert v.tolist() == [4, 4, 4, 4]

    def test_four_groups(self):
        v = licecount.consecutive([3, 3, 0, 0, 0, 5, 7, 7])
        assert v.tolist() == [2, 2, 3, 3, 3, 1, 2, 2]

    def test_empty(self):
        v = licecount.consecutive([])
        assert v.tolist() == []
