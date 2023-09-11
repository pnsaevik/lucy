import requests
import os
import pandas as pd
import io


def create_token(client_id, client_secret):
    # Return token immediately if it exists
    if 'BARENTSWATCH_ACCESS_TOKEN' in os.environ:
        return os.environ['BARENTSWATCH_ACCESS_TOKEN']

    response = requests.request(
        method="POST",
        url="https://id.barentswatch.no/connect/token",
        headers={'content-type': 'application/x-www-form-urlencoded'},
        data={
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'api',
        },
    )

    response.raise_for_status()
    response_dict = response.json()

    os.environ['BARENTSWATCH_ACCESS_TOKEN'] = response_dict["access_token"]
    return response_dict["access_token"]


def site_names():
    token = os.environ['BARENTSWATCH_ACCESS_TOKEN']

    response = requests.request(
        method="GET",
        url="https://www.barentswatch.no/bwapi/v1/geodata/fishhealth/localities",
        headers={
            "authorization": f"bearer {token}",
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": "IMR Lucy",
        }
    )
    response.raise_for_status()
    response_list = response.json()
    return pd.DataFrame(response_list)


def lice_count(year):
    token = os.environ['BARENTSWATCH_ACCESS_TOKEN']

    response = requests.request(
        method="GET",
        url="https://www.barentswatch.no/bwapi/v1/geodata/download/fishhealth",
        headers={
            "authorization": f"bearer {token}",
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": "IMR Lucy",
        },
        params={
            "filetype": "csv",
            "reporttype": "lice",
            "localityno": "undefined",
            "fromyear": str(year),
            "toyear": str(year),
            "fromweek": "1",
            "toweek": "52",
        },
    )
    response.raise_for_status()
    csv_text = response.content.decode('utf-8')
    # noinspection PyTypeChecker
    df = pd.read_csv(io.StringIO(csv_text))
    return df
