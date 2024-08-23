import pytest
import requests

from lucy.data import fiskeridir
import numpy as np
import responses
import json
import os


username = os.getenv('FDIR_USERNAME')
password = os.getenv('FDIR_PASSWORD')


CSV_TEST_DATA = """AKVAKULTURTILLATELSER PR. 23-06-2023 ;;;;;;;;;;;;;;;;;;;;;;;;;;
TILL_NR;ORG.NR/PERS.NR;NAVN;ADRESSE;POSTNR;POSTSTED;TILDELINGSTIDSPUNKT;TIDSBEGRENSET;TILL_KOMNR;TILL_KOM;FORMÅL;PRODUKSJONSFORM;ART;ART_KODE;TILL_KAP;TILL_ENHET;LOK_NR;LOK_NAVN;LOK_KOMNR;LOK_KOM;LOK_PLASS;VANNMILJØ;LOK_KAP;LOK_ENHET;UTGÅR_DATO;N_GEOWGS84;Ø_GEOWGS84;PROD_OMR
A A 0001;969159570;NORGES MILJØ- OG BIOVITENSKAPELIGE UNIVERSITET (NMBU);POSTBOKS 5003;1432;ÅS;03-10-1991;;3021;ÅS;KOMMERSIELL;MATFISK;Laks;0711;1.000;TN;10362;NMBU FISKELABORATORIET;3021;ÅS;LAND;FERSKVANN;1.000;TN;;59.669233;10.757967;
A A 0001;969159570;NORGES MILJØ- OG BIOVITENSKAPELIGE UNIVERSITET (NMBU);POSTBOKS 5003;1432;ÅS;03-10-1991;;3021;ÅS;KOMMERSIELL;MATFISK;Ørret;0713;0.000;TN;10362;NMBU FISKELABORATORIET;3021;ÅS;LAND;FERSKVANN;1.000;TN;;59.669233;10.757967;
A A 0001;969159570;NORGES MILJØ- OG BIOVITENSKAPELIGE UNIVERSITET (NMBU);POSTBOKS 5003;1432;ÅS;03-10-1991;;3021;ÅS;KOMMERSIELL;MATFISK;Regnbueørret;0714;0.000;TN;10362;NMBU FISKELABORATORIET;3021;ÅS;LAND;FERSKVANN;1.000;TN;;59.669233;10.757967;
A F 0001;855869942;NORSK INSTITUTT FOR VANNFORSKNING;ØKERNVEIEN 94;0579;OSLO;05-02-1991;31-10-2028;3022;FROGN;FORSKNING;MATFISK;Laks;0711;3.800;TN;10173;SOLBERGSTRAND;3022;FROGN;LAND;FERSKVANN/SALTVANN;7.500;TN;31-10-2028;59.615783;10.652650;
A F 0001;855869942;NORSK INSTITUTT FOR VANNFORSKNING;ØKERNVEIEN 94;0579;OSLO;05-02-1991;31-10-2028;3022;FROGN;FORSKNING;MATFISK;Ørret;0713;0.000;TN;10173;SOLBERGSTRAND;3022;FROGN;LAND;FERSKVANN/SALTVANN;7.500;TN;31-10-2028;59.615783;10.652650;
A F 0001;855869942;NORSK INSTITUTT FOR VANNFORSKNING;ØKERNVEIEN 94;0579;OSLO;05-02-1991;31-10-2028;3022;FROGN;FORSKNING;MATFISK;Regnbueørret;0714;0.000;TN;10173;SOLBERGSTRAND;3022;FROGN;LAND;FERSKVANN/SALTVANN;7.500;TN;31-10-2028;59.615783;10.652650;
A F 0002;855869942;NORSK INSTITUTT FOR VANNFORSKNING;ØKERNVEIEN 94;0579;OSLO;31-03-2017;;3022;FROGN;KOMMERSIELL;SETTEFISK;Rognkjeks (felles);2221;3.000;TN;10173;SOLBERGSTRAND;3022;FROGN;LAND;FERSKVANN/SALTVANN;7.500;TN;31-10-2028;59.615783;10.652650;"""


WFS_TEST_DATA = """
<wfs:FeatureCollection xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:wfs="http://www.opengis.net/wfs/2.0" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:FiskeridirWFS="https://megrim12.fiskeridirektoratet.no:6443/arcgis/services/FiskeridirWFS/MapServer/WFSServer" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" timeStamp="2023-06-23T09:10:17Z" numberMatched="2895" numberReturned="2895" xsi:schemaLocation="http://www.opengis.net/wfs/2.0 http://schemas.opengis.net/wfs/2.0/wfs.xsd http://www.opengis.net/gml/3.2 http://schemas.opengis.net/gml/3.2.1/gml.xsd https://megrim12.fiskeridirektoratet.no:6443/arcgis/services/FiskeridirWFS/MapServer/WFSServer https://gis.fiskeridir.no/server/services/FiskeridirWFS/MapServer/WFSServer?service=wfs%26version=2.0.0%26request=DescribeFeatureType">
    <wfs:member>
        <FiskeridirWFS:Akvakultur_-_Slettede_lokaliteter gml:id="Akvakultur_-_Slettede_lokaliteter.10025">
        <FiskeridirWFS:loknr>10025</FiskeridirWFS:loknr>
        <FiskeridirWFS:navn>KLEPPSKJER Ø</FiskeridirWFS:navn>
        <FiskeridirWFS:kommune_akvareg>KARMØY</FiskeridirWFS:kommune_akvareg>
        <FiskeridirWFS:fylkesnr2020>11</FiskeridirWFS:fylkesnr2020>
        <FiskeridirWFS:kommunenr>1149</FiskeridirWFS:kommunenr>
        <FiskeridirWFS:akvakulturregister__intern_>https://sikker.fiskeridir.no/aquareg/web/sites/10025</FiskeridirWFS:akvakulturregister__intern_>
        <FiskeridirWFS:created_user>SDE</FiskeridirWFS:created_user>
        <FiskeridirWFS:last_edited_user>SDE</FiskeridirWFS:last_edited_user>
        <FiskeridirWFS:last_edited_date>2023-06-18T00:30:57</FiskeridirWFS:last_edited_date>
        <FiskeridirWFS:shape>
        <gml:Point gml:id="Akvakultur_-_Slettede_lokaliteter.10025.pn.0" srsName="urn:ogc:def:crs:EPSG::4326">
        <gml:pos>59.26178000 5.16283900</gml:pos>
        </gml:Point>
        </FiskeridirWFS:shape>
        <FiskeridirWFS:versionvalidfrom>2006-05-30T22:00:00</FiskeridirWFS:versionvalidfrom>
        </FiskeridirWFS:Akvakultur_-_Slettede_lokaliteter>
    </wfs:member>
    <wfs:member>
        <FiskeridirWFS:Akvakultur_-_Slettede_lokaliteter gml:id="Akvakultur_-_Slettede_lokaliteter.10027">
        <FiskeridirWFS:loknr>10027</FiskeridirWFS:loknr>
        <FiskeridirWFS:navn>SÆVELANDSVIK</FiskeridirWFS:navn>
        <FiskeridirWFS:kommune_akvareg>KARMØY</FiskeridirWFS:kommune_akvareg>
        <FiskeridirWFS:fylkesnr2020>11</FiskeridirWFS:fylkesnr2020>
        <FiskeridirWFS:kommunenr>1149</FiskeridirWFS:kommunenr>
        <FiskeridirWFS:akvakulturregister__intern_>https://sikker.fiskeridir.no/aquareg/web/sites/10027</FiskeridirWFS:akvakulturregister__intern_>
        <FiskeridirWFS:created_user>SDE</FiskeridirWFS:created_user>
        <FiskeridirWFS:last_edited_user>SDE</FiskeridirWFS:last_edited_user>
        <FiskeridirWFS:last_edited_date>2023-06-18T00:30:57</FiskeridirWFS:last_edited_date>
        <FiskeridirWFS:shape>
        <gml:Point gml:id="Akvakultur_-_Slettede_lokaliteter.10027.pn.0" srsName="urn:ogc:def:crs:EPSG::4326">
        <gml:pos>59.26982300 5.19178800</gml:pos>
        </gml:Point>
        </FiskeridirWFS:shape>
        <FiskeridirWFS:versionvalidfrom>2014-05-04T22:00:00</FiskeridirWFS:versionvalidfrom>
        </FiskeridirWFS:Akvakultur_-_Slettede_lokaliteter>
    </wfs:member>
</wfs:FeatureCollection>
"""


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
            'https://fiskeridirektoratet-bio-api.hi.no/apis/nmdapi/'
            'fiskeridirektoratet-bio-api/v1/report?'
            'url=https://api.fiskeridir.no/bio-api/api/v1/reports?'
            'size=100%26start-time=2022-12-31T00:00:00Z%26'
            'end-time=2024-01-01T00:00:00Z%26page=0',
            body=FISKDIR_TEST_DATA,
        )
        df = fiskeridir.biomass(2023, "nmd", "")
        assert len(df) > 0
        assert list(df.columns) == [
            'referenceId', 'reportReceipt', 'organization', 'reportTime', 'startTime',
            'endTime', 'siteNr', 'siteName', 'sourceSystem', 'productionUnitForeignId',
            'specieCode', 'numFish', 'avgWeight', 'weightUnit'
        ]

    @pytest.mark.skipif(
        condition=username is None or password is None,
        reason="Username and/or password for Fiskeridirektoratet is not set",
    )
    def test_actual_response(self):
        df = fiskeridir.biomass(
            2023, username, password, '2022-12-31', '2023-02-01')
        assert len(df) > 0
        assert list(df.columns) == [
            'referenceId', 'reportReceipt', 'organization', 'reportTime', 'startTime',
            'endTime', 'siteNr', 'siteName', 'sourceSystem', 'productionUnitForeignId',
            'specieCode', 'numFish', 'avgWeight', 'weightUnit'
        ]


class Test_active_farms:
    @responses.activate
    def test_returns_dataset(self):
        responses.add(
            responses.GET,
            'https://api.fiskeridir.no/pub-aqua/api/v1/dump/new-legacy-csv',
            body=CSV_TEST_DATA,
        )

        df = fiskeridir.active_farms()
        assert list(df.columns) == ['farmid', 'name', 'lon', 'lat']

    @pytest.mark.skipif(
        condition=username is None or password is None,
        reason="Username and/or password for Fiskeridirektoratet is not set",
    )
    def test_actual_response(self):
        df = fiskeridir.active_farms()
        assert len(df) > 0
        assert list(df.columns) == ['farmid', 'name', 'lon', 'lat']


class Test_deleted_farms:
    @responses.activate
    def test_returns_dataset(self):
        responses.add(
            responses.GET,
            'https://gis.fiskeridir.no/server/services/FiskeridirWFS/MapServer/WFSServer',
            body=WFS_TEST_DATA,
        )

        df = fiskeridir.deleted_farms()
        assert list(df.columns) == ['farmid', 'name', 'lon', 'lat']


class Test_farms:
    @responses.activate
    def test_returns_dataset(self):
        responses.add(
            responses.GET,
            'https://gis.fiskeridir.no/server/services/FiskeridirWFS/MapServer/WFSServer',
            body=WFS_TEST_DATA,
        )
        responses.add(
            responses.GET,
            'https://api.fiskeridir.no/pub-aqua/api/v1/dump/new-legacy-csv',
            body=CSV_TEST_DATA,
        )

        df = fiskeridir.farms()
        assert list(df.columns) == ['farmid', 'name', 'lon', 'lat', 'deleted']
