from lucy import barentswatch
import os


class Test_create_token:
    def test_returns_valid_token(self):
        token = barentswatch.create_token(
            client_id=os.getenv('BARENTSWATCH_CLIENT_ID'),
            client_secret=os.getenv('BARENTSWATCH_CLIENT_SECRET'),
        )
        assert isinstance(token, str)
        assert len(token) > 0

    def test_puts_token_into_environment(self):
        assert 'BARENTSWATCH_ACCESS_TOKEN' in os.environ


class Test_site_names:
    def test_returns_pandas_dataframe(self):
        df = barentswatch.site_names()
        assert set(df.columns) == {
            'aquaCultureRegistryVersion',
            'localityNo',
            'name',
            'municipalityNo',
            'municipality',
        }


class Test_lice_count:
    def test_returns_pandas_dataframe(self):
        df = barentswatch.lice_count(2020)
        assert set(df.columns) == {
            'Fastsittende lus',
            'Fylke',
            'Fylkesnummer',
            'Har telt lakselus',
            'Kommune',
            'Kommunenummer',
            'Lat',
            'Lokalitetsnavn',
            'Lokalitetsnummer',
            'Lon',
            'Lus i bevegelige stadier',
            'Lusegrense uke',
            'Over lusegrense uke',
            'Produksjonsområde',
            'ProduksjonsområdeId',
            'Sjøtemperatur',
            'Trolig uten fisk',
            'Uke',
            'Voksne hunnlus',
            'År',
        }
