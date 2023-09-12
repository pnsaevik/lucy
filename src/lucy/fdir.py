"""
Functions for interacting with the Fisheries Directorate database
"""

import numpy as np
import requests
import pandas as pd
import time


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


def biomass(year: int, user: str, passwd: str):
    """
    Return biomass data using the fiskdir API

    The function returns data for a whole year, for all farms.

    :param year: The year
    :param user: Username
    :param passwd: Password
    :return: A table of biomass data
    """
    start = f'{year}-01-01'
    stop = f'{year+1}-01-01'
    pages = paginated_request(url=get_url(start, stop), user=user, passwd=passwd)
    table = pages2dataframes(pages)
    return table
