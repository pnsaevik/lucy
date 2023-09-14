from lucy import licecount
import pandas as pd
import pytest


class Test_cleanup_lice:
    @pytest.fixture()
    def lice_df(self):
        return pd.DataFrame(
            data={
                "nch": [1., 2., 3., 4., 5., 6.],
                "npa": [1., 2., 3., 4., 5., 6.],
                "naf": [1., 2., 3., 4., 5., 6.],
                "farmid": [10, 10, 10, 20, 20, 20],
                "date": ['2020-01-06', '2020-01-13', '2020-01-20'] * 2,
            },
            index=pd.RangeIndex(stop=6, name='id'),
        )

    def test_returns_verbatim_if_complete(self, lice_df):
        df = licecount.fill_missing_lice(lice_df)
        assert df.iloc[:, :-1].to_dict('list') == lice_df.to_dict('list')

    def test_interpolates_missing_licecount(self, lice_df):
        lice_df.loc[1, "naf"] = float('nan')
        df = licecount.fill_missing_lice(lice_df)
        assert df.loc[1, "naf"] == 2

    def test_interpolates_missing_row(self, lice_df):
        df = licecount.fill_missing_lice(lice_df.iloc[[0, 2, 3, 4, 5]])
        assert df.loc[1, "date"] == '2020-01-13'
        assert df.loc[1, "naf"] == 2

    def test_does_not_interpolate_big_gaps(self, lice_df):
        lice_df.loc[2, "date"] = '2020-02-17'
        df = licecount.fill_missing_lice(lice_df)
        assert df["naf"][:7].values.tolist() == [1, 2, 0, 0, 0, 0, 3]

    def test_indicates_if_value_is_interpolated(self, lice_df):
        lice_df.loc[1, "naf"] = float('nan')
        df = licecount.fill_missing_lice(lice_df)
        assert df.loc[[0, 1, 2], "missing"].values.tolist() == [0, 1, 0]


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
