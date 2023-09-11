"""
Functions for interacting with the Barentswatch database
"""

import requests
import os
import pandas as pd
import io


def create_token(client_id, client_secret):
    # Return token immediately if it exists
    if 'BARENTSWATCH_ACCESS_TOKEN' in os.environ:
        return os.environ['BARENTSWATCH_ACCESS_TOKEN']

    print(os.getenv('BARENTSWATCH_CLIENT_ID'))
    print(os.getenv('BARENTSWATCH_CLIENT_SECRET'))

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

    print(response.text)

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


def lice_count(year: int) -> pd.DataFrame:
    """
    Returns the reported lice counts for each farm, week by week.

    There are several columns in the returned table, including:

    "År": year
    "Uke": week
    "Lokalitetsnavn": site name
    "Lokalitetsnummer": site ID number
    "Lat": latitude of site
    "Lon": longitude of site
    "Fastsittende lus": attached lice per fish
    "Lus i bevegelige stadier": mobile lice per fish
    "Voksne hunnlus": adult female lice per fish
    "Sjøtemperatur": ocean temperature

    :param year: The report year
    :return: A table of all reported lice counts
    """

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
