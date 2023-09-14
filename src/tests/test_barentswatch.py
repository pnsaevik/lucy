from lucy import barentswatch
import os
import responses


CSV_FIXTURE = """Uke,År,Lokalitetsnummer,Lokalitetsnavn,Voksne hunnlus,Lus i bevegelige stadier,Fastsittende lus,Trolig uten fisk,Har telt lakselus,Kommunenummer,Kommune,Fylkesnummer,Fylke,Lat,Lon,Lusegrense uke,Over lusegrense uke,Sjøtemperatur,ProduksjonsområdeId,Produksjonsområde
4,2020,13035,Sauaneset I,1.79,3.63,0.78,Nei,Ja,4625,AUSTEVOLL,46,Vestland,60.089085,5.267967,0.5,Ja,7.75,3,Karmøy til Sotra
3,2020,13035,Sauaneset I,1.03,5.12,2.53,Nei,Ja,4625,AUSTEVOLL,46,Vestland,60.089085,5.267967,0.5,Ja,8,3,Karmøy til Sotra
2,2020,13035,Sauaneset I,0.94,2.78,1.6,Nei,Ja,4625,AUSTEVOLL,46,Vestland,60.089085,5.267967,0.5,Ja,8.07,3,Karmøy til Sotra
1,2020,13035,Sauaneset I,1.22,4.56,0.97,Nei,Ja,4625,AUSTEVOLL,46,Vestland,60.089085,5.267967,0.5,Ja,8.6,3,Karmøy til Sotra
"""


class Test_create_token:
    @responses.activate
    def test_returns_valid_token(self):
        responses.add(
            method=responses.POST,
            url="https://id.barentswatch.no/connect/token",
            body='{"access_token": "dummytoken"}',
        )

        token = barentswatch.create_token(
            client_id='my_client',
            client_secret='my_secret',
        )
        assert isinstance(token, str)
        assert len(token) > 0

    def test_puts_token_into_environment(self):
        assert 'BARENTSWATCH_ACCESS_TOKEN' in os.environ


class Test_lice_count:
    @responses.activate
    def test_returns_pandas_dataframe(self):
        os.environ['BARENTSWATCH_ACCESS_TOKEN'] = 'dummytoken'
        responses.add(
            method=responses.GET,
            url="https://www.barentswatch.no/bwapi/v1/geodata/download/fishhealth",
            body=CSV_FIXTURE,
        )

        df = barentswatch.lice(2020)
        assert set(df.columns) == {
            'date',
            'Fylke',
            'Fylkesnummer',
            'Har telt lakselus',
            'Kommune',
            'Kommunenummer',
            'Lat',
            'Lokalitetsnavn',
            'Lon',
            'Lusegrense uke',
            'Over lusegrense uke',
            'Produksjonsområde',
            'ProduksjonsområdeId',
            'Trolig uten fisk',
            'Uke',
            'farmid',
            'naf',
            'nch',
            'npa',
            'temp',
            'År',
        }
