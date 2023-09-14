import pytest
import requests

from lucy import fiskeridir
import numpy as np
import responses
import json


FISKDIR_TEST_DATA = """
{"content":[
 {"referenceId":"38957-1682892000-930367931-930367931",
  "reportReceipt":"AR557485954",
  "reportee":{"organization":"930367931"},
  "period":{"reportTime":"2023-06-21T12:48:14Z","startTime":"2023-04-30T22:00:00Z","endTime":"2023-05-31T22:00:00Z","resolution":"MONTH","resolutionValue":"MÅNED","registeredTime":"2023-06-21T12:48:14Z"},
  "site":{"siteNr":38957,"siteName":"Låderskjera","sourceSystem":"AKVA group Fishtalk"},
  "fallowing":{"startTime":"2023-06-14T02:00:00Z","endTime":"9999-12-30T00:00:00Z","productionMovedToSiteNr":null},
  "status":{"validFrom":"2023-06-22T04:50:10Z","validUntil":"9999-12-30T00:00:00Z","registeredTime":"2023-06-21T12:48:14Z","registeredBy":"service-account-saga-system","status":"AUTO_BIOMASS_CHECK_APPROVED","statusValue":"AUTOMATISK GODKJENT AV BIOMASSEVALIDERINGEN","note":"Automatisk sjekk avdekket ingen avvik."},
  "production":[
   {"productionUnitForeignId":"0002","species":[{"specieCode":"1691","cohorts":[{"year":2022,"originReference":"2022-1-1691-?","operator":"930367931","sumProduction":{"inventory":41,"averageWeight":0.0,"weightUnit":"G"},"sumLoss":{"deceased":0,"discarded":0,"escaped":0,"unspecified":0},"sumSold":null,"sumMoved":null,"sumReleased":0,"sumLivestockCountError":0,"sumFeedConsumption":[],"sumHarvest":[],"details":[]}]},{"specieCode":"1694","cohorts":[{"year":2022,"originReference":"2022-1-1694-?","operator":"930367931","sumProduction":{"inventory":2807,"averageWeight":0.0,"weightUnit":"G"},"sumLoss":{"deceased":0,"discarded":0,"escaped":0,"unspecified":0},"sumSold":null,"sumMoved":null,"sumReleased":0,"sumLivestockCountError":0,"sumFeedConsumption":[{"type":"UNSPECIFIED","typeValue":"USPESIFISERT","amount":2.0,"unit":"KG"}],"sumHarvest":[],"details":[]}]},{"specieCode":"222130","cohorts":[{"year":2022,"originReference":"2022-1-222130-?","operator":"930367931","sumProduction":{"inventory":366,"averageWeight":0.0,"weightUnit":"G"},"sumLoss":{"deceased":40,"discarded":0,"escaped":0,"unspecified":0},"sumSold":null,"sumMoved":null,"sumReleased":0,"sumLivestockCountError":0,"sumFeedConsumption":[],"sumHarvest":[],"details":[]}]}]},
   {"productionUnitForeignId":"0003","species":[{"specieCode":"1694","cohorts":[{"year":2022,"originReference":"2022-1-1694-?","operator":"930367931","sumProduction":{"inventory":2601,"averageWeight":0.0,"weightUnit":"G"},"sumLoss":{"deceased":0,"discarded":0,"escaped":0,"unspecified":0},"sumSold":null,"sumMoved":null,"sumReleased":0,"sumLivestockCountError":0,"sumFeedConsumption":[{"type":"UNSPECIFIED","typeValue":"USPESIFISERT","amount":4.0,"unit":"KG"}],"sumHarvest":[],"details":[]}]}]},
   {"productionUnitForeignId":"0004","species":[{"specieCode":"1694","cohorts":[{"year":2022,"originReference":"2022-1-1694-?","operator":"930367931","sumProduction":{"inventory":1720,"averageWeight":0.0,"weightUnit":"G"},"sumLoss":{"deceased":0,"discarded":0,"escaped":0,"unspecified":0},"sumSold":null,"sumMoved":null,"sumReleased":0,"sumLivestockCountError":0,"sumFeedConsumption":[{"type":"UNSPECIFIED","typeValue":"USPESIFISERT","amount":4.0,"unit":"KG"}],"sumHarvest":[],"details":[]}]},{"specieCode":"222130","cohorts":[{"year":2022,"originReference":"2022-1-222130-?","operator":"930367931","sumProduction":{"inventory":262,"averageWeight":0.0,"weightUnit":"G"},"sumLoss":{"deceased":161,"discarded":0,"escaped":0,"unspecified":0},"sumSold":null,"sumMoved":null,"sumReleased":0,"sumLivestockCountError":0,"sumFeedConsumption":[{"type":"UNSPECIFIED","typeValue":"USPESIFISERT","amount":1.0,"unit":"KG"}],"sumHarvest":[],"details":[]}]}]},
   {"productionUnitForeignId":"0005","species":[{"specieCode":"071101","cohorts":[{"year":2022,"originReference":"2022-1-071101-22.05.001","operator":"930367931","sumProduction":{"inventory":138486,"averageWeight":5728.0,"weightUnit":"G"},"sumLoss":{"deceased":12776,"discarded":64,"escaped":0,"unspecified":0},"sumSold":null,"sumMoved":null,"sumReleased":0,"sumLivestockCountError":0,"sumFeedConsumption":[{"type":"UNSPECIFIED","typeValue":"USPESIFISERT","amount":53233.0,"unit":"KG"}],"sumHarvest":[{"amount":18181,"weightInKg":96809.0,"type":"GUTTED","typeValue":"SLØYD"}],"details":[]}]},{"specieCode":"1691","cohorts":[{"year":2022,"originReference":"2022-1-1691-?","operator":"930367931","sumProduction":{"inventory":479,"averageWeight":0.0,"weightUnit":"G"},"sumLoss":{"deceased":0,"discarded":0,"escaped":0,"unspecified":0},"sumSold":null,"sumMoved":null,"sumReleased":0,"sumLivestockCountError":0,"sumFeedConsumption":[],"sumHarvest":[],"details":[]}]},{"specieCode":"1694","cohorts":[{"year":2022,"originReference":"2022-1-1694-?","operator":"930367931","sumProduction":{"inventory":9407,"averageWeight":0.0,"weightUnit":"G"},"sumLoss":{"deceased":51,"discarded":0,"escaped":0,"unspecified":0},"sumSold":null,"sumMoved":null,"sumReleased":0,"sumLivestockCountError":0,"sumFeedConsumption":[{"type":"UNSPECIFIED","typeValue":"USPESIFISERT","amount":4.0,"unit":"KG"}],"sumHarvest":[],"details":[]}]},{"specieCode":"222130","cohorts":[{"year":2022,"originReference":"2022-1-222130-?","operator":"930367931","sumProduction":{"inventory":5145,"averageWeight":0.0,"weightUnit":"G"},"sumLoss":{"deceased":994,"discarded":0,"escaped":0,"unspecified":0},"sumSold":null,"sumMoved":null,"sumReleased":0,"sumLivestockCountError":0,"sumFeedConsumption":[{"type":"UNSPECIFIED","typeValue":"USPESIFISERT","amount":3.0,"unit":"KG"}],"sumHarvest":[],"details":[]}]}]},
   {"productionUnitForeignId":"0006","species":[{"specieCode":"1691","cohorts":[{"year":2022,"originReference":"2022-1-1691-?","operator":"930367931","sumProduction":{"inventory":102,"averageWeight":0.0,"weightUnit":"G"},"sumLoss":{"deceased":1,"discarded":0,"escaped":0,"unspecified":0},"sumSold":null,"sumMoved":null,"sumReleased":0,"sumLivestockCountError":0,"sumFeedConsumption":[],"sumHarvest":[],"details":[]}]},{"specieCode":"1694","cohorts":[{"year":2022,"originReference":"2022-1-1694-?","operator":"930367931","sumProduction":{"inventory":5383,"averageWeight":0.0,"weightUnit":"G"},"sumLoss":{"deceased":56,"discarded":0,"escaped":0,"unspecified":0},"sumSold":null,"sumMoved":null,"sumReleased":0,"sumLivestockCountError":0,"sumFeedConsumption":[{"type":"UNSPECIFIED","typeValue":"USPESIFISERT","amount":3.0,"unit":"KG"}],"sumHarvest":[],"details":[]}]},{"specieCode":"222130","cohorts":[{"year":2022,"originReference":"2022-1-222130-?","operator":"930367931","sumProduction":{"inventory":5812,"averageWeight":0.0,"weightUnit":"G"},"sumLoss":{"deceased":686,"discarded":0,"escaped":0,"unspecified":0},"sumSold":null,"sumMoved":null,"sumReleased":0,"sumLivestockCountError":0,"sumFeedConsumption":[{"type":"UNSPECIFIED","typeValue":"USPESIFISERT","amount":4.0,"unit":"KG"}],"sumHarvest":[],"details":[]}]}]},
   {"productionUnitForeignId":"0007","species":[{"specieCode":"071101","cohorts":[{"year":2022,"originReference":"2022-1-071101-22.11.009","operator":"930367931","sumProduction":{"inventory":38546,"averageWeight":5645.0,"weightUnit":"G"},"sumLoss":{"deceased":3193,"discarded":0,"escaped":0,"unspecified":0},"sumSold":null,"sumMoved":null,"sumReleased":0,"sumLivestockCountError":0,"sumFeedConsumption":[{"type":"UNSPECIFIED","typeValue":"USPESIFISERT","amount":18748.0,"unit":"KG"}],"sumHarvest":[],"details":[]}]}]},
   {"productionUnitForeignId":"0008","species":[{"specieCode":"1691","cohorts":[{"year":2022,"originReference":"2022-1-1691-?","operator":"930367931","sumProduction":{"inventory":29,"averageWeight":0.0,"weightUnit":"G"},"sumLoss":{"deceased":0,"discarded":0,"escaped":0,"unspecified":0},"sumSold":null,"sumMoved":null,"sumReleased":0,"sumLivestockCountError":0,"sumFeedConsumption":[],"sumHarvest":[],"details":[]}]},{"specieCode":"1694","cohorts":[{"year":2022,"originReference":"2022-1-1694-?","operator":"930367931","sumProduction":{"inventory":8271,"averageWeight":0.0,"weightUnit":"G"},"sumLoss":{"deceased":0,"discarded":0,"escaped":0,"unspecified":0},"sumSold":null,"sumMoved":null,"sumReleased":0,"sumLivestockCountError":0,"sumFeedConsumption":[],"sumHarvest":[],"details":[]}]}]},
   {"productionUnitForeignId":"Gen-1","species":[{"specieCode":"071101","cohorts":[{"year":2022,"originReference":"2022-1-071101-22.11.001","operator":"930367931","sumProduction":{"inventory":0,"averageWeight":0.0,"weightUnit":"G"},"sumLoss":{"deceased":404,"discarded":1088,"escaped":0,"unspecified":0},"sumSold":null,"sumMoved":null,"sumReleased":0,"sumLivestockCountError":-2753,"sumFeedConsumption":[{"type":"UNSPECIFIED","typeValue":"USPESIFISERT","amount":8346.0,"unit":"KG"}],"sumHarvest":[{"amount":77484,"weightInKg":389163.0,"type":"GUTTED","typeValue":"SLØYD"}],"details":[]}]}]},
   {"productionUnitForeignId":"Gen-2","species":[{"specieCode":"071101","cohorts":[{"year":2022,"originReference":"2022-1-071101-22.04.001","operator":"930367931","sumProduction":{"inventory":0,"averageWeight":0.0,"weightUnit":"G"},"sumLoss":{"deceased":125,"discarded":272,"escaped":0,"unspecified":0},"sumSold":null,"sumMoved":null,"sumReleased":0,"sumLivestockCountError":-2194,"sumFeedConsumption":[],"sumHarvest":[{"amount":49622,"weightInKg":302701.0,"type":"GUTTED","typeValue":"SLØYD"}],"details":[]}]}]},
   {"productionUnitForeignId":"Gen-3","species":[{"specieCode":"071101","cohorts":[{"year":2022,"originReference":"2022-1-071101-22.07.006","operator":"930367931","sumProduction":{"inventory":0,"averageWeight":0.0,"weightUnit":"G"},"sumLoss":{"deceased":1289,"discarded":2113,"escaped":0,"unspecified":0},"sumSold":null,"sumMoved":null,"sumReleased":0,"sumLivestockCountError":-6791,"sumFeedConsumption":[{"type":"UNSPECIFIED","typeValue":"USPESIFISERT","amount":18516.0,"unit":"KG"}],"sumHarvest":[{"amount":79677,"weightInKg":463705.0,"type":"GUTTED","typeValue":"SLØYD"}],"details":[]}]}]},
   {"productionUnitForeignId":"Gen-5","species":[{"specieCode":"071101","cohorts":[{"year":2022,"originReference":"2022-1-071101-22.06.001","operator":"930367931","sumProduction":{"inventory":0,"averageWeight":0.0,"weightUnit":"G"},"sumLoss":{"deceased":7186,"discarded":1735,"escaped":0,"unspecified":0},"sumSold":null,"sumMoved":null,"sumReleased":0,"sumLivestockCountError":731,"sumFeedConsumption":[{"type":"UNSPECIFIED","typeValue":"USPESIFISERT","amount":49213.0,"unit":"KG"}],"sumHarvest":[{"amount":140457,"weightInKg":788776.0,"type":"GUTTED","typeValue":"SLØYD"}],"details":[]}]}]}]}],
"number":0,
"size":100,
"totalElements":1,
"last":true,
"totalPages":1,
"first":true,
"numberOfElements":1}
"""


class Test_date2str:
    def test_converts_stringdate_to_correct_format(self):
        assert fiskeridir.date2str('2020-01-01') == '2020-01-01T00:00:00Z'

    def test_converts_numpydate_to_correct_format(self):
        dt = np.datetime64('2020-01-01T12')
        assert fiskeridir.date2str(dt) == '2020-01-01T12:00:00Z'


class Test_get_url:
    def test_returns_valid_url(self):
        url = fiskeridir.get_url(start_date='2020-01-01', stop_date='2021-01-01')
        assert url.startswith('https://')


class Test_repeated_request:
    @responses.activate
    def test_returns_response_if_success(self):
        responses.add(method=responses.GET, url='https://test.url/', body='Payload')
        response = fiskeridir.repeated_request(url='https://test.url/', user='', passwd='')
        assert response.text == 'Payload'

    @responses.activate
    def test_fails_after_number_of_attempts(self):
        num_attempts = [0]

        def callback(_):
            num_attempts[0] += 1
            return 500, {}, "Error"

        responses.add_callback(
            method=responses.GET,
            url='https://test.url/',
            callback=callback,
        )

        with pytest.raises(requests.HTTPError):
            fiskeridir.repeated_request(
                url='https://test.url/', user='', passwd='', attempts=2, retry_time=0)

        assert num_attempts[0] == 2


class Test_paginated_request:
    @responses.activate
    def test_returns_paginated_data(self):
        responses.add(responses.GET, 'https://test.url/q?r%26page=0', '{"last": false}')
        responses.add(responses.GET, 'https://test.url/q?r%26page=1', '{"last": false}')
        responses.add(responses.GET, 'https://test.url/q?r%26page=2', '{"last": true}')

        p = fiskeridir.paginated_request(url='https://test.url/q?r', user='', passwd='')
        assert len(p) == 3


class Test_pages2dataframes:
    def test_returns_dataframe(self):
        p = json.loads(FISKDIR_TEST_DATA)
        pages = [p]
        df = fiskeridir.pages2dataframes(pages)
        assert 'numFish' in df.columns


class Test_biomass:
    @responses.activate
    def test_returns_dataset(self):
        responses.add(
            responses.GET,
            'https://fiskeridirektoratet-bio-api.hi.no/apis/nmdapi/fiskeridirektoratet-bio-api/v1/report?url=https://api.fiskeridir.no/bio-api/api/v1/reports?size=100%26start-time=2023-01-01T00:00:00Z%26end-time=2024-01-01T00:00:00Z%26page=0',
            body=FISKDIR_TEST_DATA,
        )
        df = fiskeridir.biomass(2023, "nmd", "")
        assert list(df.columns) == [
            'referenceId', 'reportReceipt', 'organization', 'reportTime', 'startTime',
            'endTime', 'siteNr', 'siteName', 'sourceSystem', 'productionUnitForeignId',
            'specieCode', 'numFish', 'avgWeight', 'weightUnit'
        ]
