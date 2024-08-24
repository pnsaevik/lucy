"""
Functions for interacting with the Kystverket AIS database
"""

import datetime
import numpy as np


_AIS_CREDENTIALS = dict()


def ais(user: str, passwd: str, mmsi: int | list[int],
        start, stop):
    """
    Retrieve AIS data from Kystdatahuset

    The function makes requests to kystdatahuset using the specified
    username and password. Subsequent calls uses a login token
    for more efficient access.

    :param user: Username
    :param passwd: Password
    :param mmsi: Either a single MMSI number, or a list of numbers
    :param start: Start date of AIS track (UTC)
    :param stop: Stop date of AIS track (UTC)
    :return: Data frame containing AIS data
    """
    if _AIS_CREDENTIALS.get('user', '') == user:
        token = _AIS_CREDENTIALS.get('token', '')
    else:
        token = _ais_get_token(user, passwd)
        _AIS_CREDENTIALS['user'] = user
        _AIS_CREDENTIALS['token'] = token

    if isinstance(mmsi, int):
        mmsi = [mmsi]

    data = _ais_get_data(token, mmsi, start, stop)

    return data


def _ais_get_token(user: str, passwd: str) -> str:
    """
    Login to kystdatahuset using username and password

    Return token that can be used with subsequent calls.

    :param user: Username
    :param passwd: Password
    :return: Token
    """
    import json
    import requests

    reqUrl = "https://kystdatahuset.no/ws/api/auth/login"
    headersList = {
        "accept": "*/*",
        "Content-Type": "application/json"
    }
    payload = json.dumps({
        "username": user,
        "password": passwd,
    })
    response = requests.request("POST", reqUrl, data=payload, headers=headersList)
    response.raise_for_status()
    token = response.json()['data']['JWT']
    return token


def _ais_get_data(token: str, mmsi: list[int],
                  start: datetime.datetime, stop: datetime.datetime):
    """
    Retrieve AIS data from Kystdatahuset

    The function makes requests to kystdatahuset using the specified
    token. The token is obtained by a previous login
    to kystdatahuset

    :param token: Token
    :param mmsi: List of MMSI numbers
    :param start: Start date of AIS track (UTC)
    :param stop: Stop date of AIS track (UTC)
    :return: Data frame containing AIS data
    """
    import json
    import requests
    import pandas as pd

    reqUrl = "https://kystdatahuset.no/ws/api/ais/positions/for-mmsis-time"
    headersList = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    # A bug in the API leads us to require this conversion
    start = np.datetime64(start, 'us').astype(object)
    stop = np.datetime64(stop, 'us').astype(object)
    corr_start = start - datetime.timedelta(hours=2)
    corr_stop = stop + datetime.timedelta(days=1, hours=2)

    payload = json.dumps({
        "mmsiIds": [int(v) for v in mmsi],
        "start": f'{corr_start:%Y%m%d}',
        "end": f'{corr_stop:%Y%m%d}',
    })

    response = requests.request("POST", reqUrl, data=payload, headers=headersList)
    df = pd.DataFrame(
        data=response.json()['data'],
        columns=[
            'mmsi', 'datetime_utc', 'longitude', 'latitude', 'course_over_ground',
            'speed_over_ground', 'message_number', 'calc_speed',
            'sec_to_previous', 'dist_to_previous',
        ],
    )

    # Filter out times outside interval
    dt = df.datetime_utc.values.astype('datetime64')
    too_early = dt < np.datetime64(start)
    too_late = dt > np.datetime64(stop)
    bad_idx = too_early | too_late
    df = df.loc[~bad_idx]

    # Filter out messages that are unlikely to be correct
    bad_idx = df.calc_speed.values < 0
    bad_idx |= df.calc_speed.values > 90
    df = df.loc[~bad_idx]

    return df.copy(deep=True)


def utc_to_norwegian(t):
    import pytz
    tz_nor = pytz.timezone('Europe/Oslo')
    tz_utc = pytz.utc
    utc_datetime = tz_utc.localize(t)
    nor_datetime = utc_datetime.astimezone(tz_nor)
    return nor_datetime.replace(tzinfo=None)


def norwegian_to_utc(t):
    import pytz
    tz_nor = pytz.timezone('Europe/Oslo')
    tz_utc = pytz.utc
    nor_datetime = tz_nor.localize(t)
    utc_datetime = nor_datetime.astimezone(tz_utc)
    return utc_datetime.replace(tzinfo=None)
