"""
Functions for interacting with the Fisheries Directorate database
"""

import numpy as np
import requests
import pandas as pd
import time
import re
import io
from .. import schema


def date2str(dt) -> str:
    """
    Convert date to string format accepted by the fiskdir api

    :param dt: Input date
    :return: Output date, ISO-formatted with 'Z' at the end
    """
    return np.datetime64(dt).astype('datetime64[s]').astype(str) + 'Z'


def get_url(start_date, stop_date):
    """
    Get url for accessing the fiskdir biomass data

    :param start_date: Start date
    :param stop_date: Stop date
    :return: Correctly formatted url
    """
    return (
        'https://fiskeridirektoratet-bio-api.hi.no/apis/nmdapi/' +
        'fiskeridirektoratet-bio-api/v1/report?' +
        'url=https://api.fiskeridir.no/bio-api/api/v1/reports?' +
        'size=100' +
        '%26start-time=' + date2str(start_date) +
        '%26end-time=' + date2str(stop_date)
    )


def repeated_request(
        url: str, user: str, passwd: str, timeout=30, attempts=5, retry_time=1,
        continue_codes=(200, 400, 404),
):
    """
    Try reconnecting multiple times

    :param url: Url to connect to
    :param user: Username
    :param passwd: Password
    :param timeout: Timeout (in seconds) for each individual request
    :param attempts: Maximal number of attempts before giving up
    :param retry_time: Number of seconds to wait after each failed attempt
    :param continue_codes: HTTP return codes indicating that we should not attempt a reconnection
    :return:
    """
    r = requests.get(url, timeout=timeout, auth=(user, passwd))
    num_trials = 1

    while (r.status_code not in continue_codes) & (num_trials < attempts):
        time.sleep(retry_time)
        r = requests.get(url, timeout=timeout, auth=(user, passwd))
        num_trials += 1

    r.raise_for_status()
    return r


def paginated_request(url: str, user: str, passwd: str) -> list:
    """
    Requests new data from the API until the last page is reached

    :param url: The API url
    :param user: Username
    :param passwd: Password
    :return: A list of data pages, one dict per page
    """
    p = []
    is_last = False
    pagenum = 0
    while not is_last:
        r = repeated_request(url + f"%26page={pagenum}", user, passwd).json()
        is_last = r['last']
        p.append(r)
        pagenum += 1
    return p


def pages2dataframes(p: list) -> pd.DataFrame:
    """
    Convert pages to dataframe

    Given a list of pages (dict items) returned from fiskdir api, convert to
    a single dataframe

    :param p: A list of pages (dict items)
    :return: A table containing all the fiskdir data
    """
    report_dfs = []
    cage_dfs = []

    for page in p:
        for report in page['content']:
            report_data = {}
            for k in ['referenceId', 'reportReceipt']:
                report_data[k] = report[k]
            report_data['organization'] = report['reportee']['organization']
            for k in ['reportTime', 'startTime', 'endTime']:
                report_data[k] = report['period'][k]
            for k in ['siteNr', 'siteName', 'sourceSystem']:
                report_data[k] = report['site'][k]
            report_dfs.append(report_data)

            for cage in report['production']:
                for species in cage['species']:
                    for cohort in species['cohorts']:
                        cage_data = dict(
                            referenceId=report['referenceId'],
                            productionUnitForeignId=cage['productionUnitForeignId'],
                            specieCode=species['specieCode'],
                            numFish=cohort['sumProduction']['inventory'],
                            avgWeight=cohort['sumProduction']['averageWeight'],
                            weightUnit=cohort['sumProduction']['weightUnit'],
                        )
                        cage_dfs.append(cage_data)

    report_df = pd.DataFrame(report_dfs)
    cage_df = pd.DataFrame(cage_dfs)
    return pd.merge(left=report_df, right=cage_df, on='referenceId', how='right')


def biomass(year: int, user: str, passwd: str, start=None, stop=None):
    """
    Return biomass data using the fiskdir API

    The function returns data for a whole year, for all farms.

    :param year: The year
    :param user: Username
    :param passwd: Password
    :param start: If given, use this as the start date instead of 1st
        January of the given year
    :param stop: If given, use this as the stop date instead of 31st
        December of the given year
    :return: A table of biomass data
    """
    if start:
        start = np.datetime64(start, 'D').astype(str)
    else:
        start = f'{year - 1}-12-31'
    if stop:
        stop = np.datetime64(stop, 'D').astype(str)
    else:
        stop = f'{year + 1}-01-01'

    pages = paginated_request(url=get_url(start, stop), user=user, passwd=passwd)
    table = pages2dataframes(pages)
    return table


def active_farms() -> schema.Farms:
    """
    Download data on active fish farms

    :return: A table with fish farm data
    """
    url = 'https://api.fiskeridir.no/pub-aqua/api/v1/dump/new-legacy-csv'
    r = requests.get(url, timeout=10)
    r.raise_for_status()

    # noinspection PyTypeChecker
    df = pd.read_csv(
        filepath_or_buffer=io.StringIO(r.text),
        sep=';',
        header=1,
        usecols=['LOK_NR', 'LOK_NAVN', 'N_GEOWGS84', 'Ø_GEOWGS84']
    )
    df = df.rename(columns=dict(
        LOK_NR='farmid',
        LOK_NAVN='name',
        N_GEOWGS84='lat',
        Ø_GEOWGS84='lon',
    ))

    df = df.groupby('farmid').first().reset_index()
    df = df[['farmid', 'name', 'lon', 'lat']]
    return df


def deleted_farms() -> schema.Farms:
    """
    Download data on deleted fish farms

    :return: A table with fish farm data
    """
    url = 'https://gis.fiskeridir.no/server/services/FiskeridirWFS/MapServer/WFSServer'
    args = dict(
        service='WFS',
        request='GetFeature',
        typename='FiskeridirWFS:Akvakultur_-_Slettede_lokaliteter',
        propertyName='loknr,navn,shape',
    )

    r = requests.get(url, params=args, timeout=30)
    r.raise_for_status()
    txt = r.text

    # Interpret the xml output
    pattern = re.compile(
        '<wfs:member>.*?<FiskeridirWFS:loknr>(.*?)</FiskeridirWFS:loknr>.*?'
        '<FiskeridirWFS:navn>(.*?)</FiskeridirWFS:navn>.*?'
        '<gml:pos>(.*?) (.*?)</gml:pos>.*?</wfs:member>',
        flags=re.DOTALL,
    )
    data = pattern.findall(txt)

    # Encapsulate as pandas.DataFrame
    df = pd.DataFrame(data, columns=['farmid', 'name', 'lat', 'lon'])
    df = df[['farmid', 'name', 'lon', 'lat']]
    return df


def farms() -> schema.Farms:
    """
    Download data on active and deleted fish farms

    :return: A table with fish farm data
    """
    df_a = active_farms()
    df_b = deleted_farms()

    df_a['deleted'] = False
    df_b['deleted'] = True

    return pd.concat([df_a, df_b])  # type: ignore
