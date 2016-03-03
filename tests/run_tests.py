# =================================================================
#
# Terms and Conditions of Use
#
# Unless otherwise noted, computer program source code of this
# distribution # is covered under Crown Copyright, Government of
# Canada, and is distributed under the MIT License.
#
# The Canada wordmark and related graphics associated with this
# distribution are protected under trademark law and copyright law.
# No permission is granted to use them outside the parameters of
# the Government of Canada's corporate identity program. For
# more information, see
# http://www.tbs-sct.gc.ca/fip-pcim/index-eng.asp
#
# Copyright title to all 3rd party software distributed with this
# software is held by the respective copyright holders as noted in
# those files. Users are asked to read the 3rd Party Licenses
# referenced with those assets.
#
# Copyright (c) 2015 Government of Canada
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

import datetime
import unittest

from owslib.feature.wfs110 import WebFeatureService_1_1_0

from pywoudc import WoudcClient, date2string


def load_test_data_file(filename):
    """helper function to open test file regardless of invocation"""

    try:
        with open('data/{}'.format(filename)) as ff:
            return ff.read()
    except IOError:
        with open('tests/data/{}'.format(filename)) as ff:
            return ff.read()


class WoudcClientTest(unittest.TestCase):
    """Test suite for package pywoudc.WoudcClient"""

    def setUp(self):
        """bootstrap"""

        self.client = WoudcClient()

    def tearDown(self):
        """destroy"""
        pass

    def test_smoke_test(self):
        """test basic properties"""

        self.assertEqual(self.client.url, 'http://geo.woudc.org/ows',
                         'Expected specific URL')

        self.assertEqual(self.client.about,
                         'http://woudc.org/about/data-access.php',
                         'Expected specific about URL')
        self.assertEqual(self.client.outputformat,
                         'application/json; subtype=geojson',
                         'Expected specific default outputformat')

        self.assertEqual(self.client.maxfeatures, 25000,
                         'Expected specific default maxfeatures')

        self.assertEqual(self.client.timeout, 30,
                         'Expected specific default timeout')

        self.assertTrue(isinstance(self.client.server,
                                   WebFeatureService_1_1_0),
                        'Expected specific instance')

    def test_get_metadata(self):
        """test get various requests for metadata"""

        for typename in ['stations', 'contributors']:
            data = self.client._get_metadata(typename)

            self.assertTrue(isinstance(data, dict),
                            'Expected specific instance')

            self.assertTrue('type' in data,
                            'Expected GeoJSON header')

            self.assertEqual(data['type'], 'FeatureCollection',
                             'Expected GeoJSON header')

            self.assertTrue('features' in data,
                            'Expected GeoJSON header')

            self.assertTrue(len(data['features']) > 0,
                            'Expected non-empty %s list' % typename)

            raw_data = self.client._get_metadata(typename, raw=True)

            self.assertTrue(isinstance(raw_data, str),
                            'Expected specific instance')

            self.assertTrue('"type": "FeatureCollection"' in raw_data,
                            'Expected raw GeoJSON response')

    def test_get_data(self):
        """test get data handling"""

        dataset = 'totalozone'
        bad_bbox = [42, -52, 84]

        self.assertRaises(ValueError, self.client.get_data,
                          dataset, bbox=bad_bbox)

        self.assertRaises(ValueError, self.client.get_data,
                          dataset, bbox='-142,42,-53,84')

        self.assertRaises(ValueError, self.client.get_data,
                          dataset, temporal='2000-11-11/2001-10-30')

        self.assertRaises(ValueError, self.client.get_data,
                          dataset, temporal=['2000-11-11'])

        self.assertRaises(ValueError, self.client.get_data,
                          dataset, sort_order='bad')

        self.assertRaises(ValueError, self.client.get_data,
                          dataset, variables='foo')

    def test_date2string(self):
        """test date handling"""

        self.assertEqual(date2string('2000-10-10', 'begin'),
                         '2000-10-10 00:00:00',
                         'Expected specific date string from date string')

        self.assertEqual(date2string('2001-11-11', 'end'),
                         '2001-11-11 23:59:59',
                         'Expected specific date string from date string')

        self.assertEqual(date2string('2000-10-10 02:22:28'),
                         '2000-10-10 02:22:28',
                         'Expected specific date string from datetime string')

        self.assertEqual(date2string('2001-11-11 11:33:24'),
                         '2001-11-11 11:33:24',
                         'Expected specific date string from datetime string')

        self.assertEqual(date2string(datetime.date(2000, 11, 30), 'begin'),
                         '2000-11-30 00:00:00',
                         'Expected specific date string from date object')

        self.assertEqual(date2string(datetime.date(2011, 11, 30), 'end'),
                         '2011-11-30 23:59:59',
                         'Expected specific date string from date object')

        self.assertEqual(date2string(
                         datetime.datetime(2002, 10, 30, 11, 11, 11)),
                         '2002-10-30 11:11:11',
                         'Expected specific date string from datetime object')

        self.assertEqual(date2string(
                         datetime.datetime(2011, 11, 30, 12, 12, 12)),
                         '2011-11-30 12:12:12',
                         'Expected specific date string from datetime object')

    def test_validation_services(self):
        """test WOUDC WPS processes"""

        # test Extended CSV format validation -- bad input
        data_value = 'bad data'
        self.assertRaises(ValueError, self.client.data_extcsv, data_value)

        # test Extended CSV format validation -- good input
        data_value = load_test_data_file(
            '19980114.dial.lotard.001.crestech.csv')
        self.assertTrue(self.client.data_extcsv(data_value),
                        'Expected valid result')

        # test Data Quality Assessment -- bad input
        data_value = 'bad data'
        self.assertRaises(ValueError, self.client.data_qa, data_value)

        # test Data Quality Assessment -- Lidar (unsupported)
        data_value = load_test_data_file(
            '19980114.dial.lotard.001.crestech.csv')
        self.assertRaises(ValueError, self.client.data_qa, data_value)

        # test Extended CSV format validation -- good input
        data_value = load_test_data_file('19830601.ECC.na.na.MSC.csv')
        self.assertTrue(self.client.data_qa(data_value),
                        'Expected successful Qa to be performed')

if __name__ == '__main__':
    unittest.main()
