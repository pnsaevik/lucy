"""
Functions for interacting with the Barentswatch database
"""

import requests
import os
import pandas as pd
import io
from . import schema
import datetime


def create_token(client_id: str, client_secret: str):
    """
    Create temporary token used for interacting with the online database.

    The function puts the token into the environment variable
    ``BARENTSWATCH_ACCESS_TOKEN`` for later use. It also returns the token
    as a string.

    :param client_id: Username
    :param client_secret: Password
    :return: The access token
    """

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


def lice(year: int) -> schema.Lice:
    """
    Returns the reported lice counts for each farm, week by week.

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
    df = df.rename(columns={
        'Fastsittende lus': 'nch',
        'Lus i bevegelige stadier': 'npa',
        'Voksne hunnlus': 'naf',
        'Sjøtemperatur': 'temp',
        'Lokalitetsnummer': 'farmid',
    })
    df.index.name = 'id'
    datestr = [f'{yr}-{wk}-1' for yr, wk in zip(df['År'], df['Uke'])]
    df['date'] = [datetime.datetime.strptime(s, "%G-%V-%u") for s in datestr]
    return df
