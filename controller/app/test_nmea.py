import unittest

import nmea
from nmea import split_sentence
from nmea import split_body
from nmea import compute_checksum
from nmea import create_sentence
from nmea import parse_int
from nmea import parse_float
from nmea import parse_degrees
from nmea import parse_date
from nmea import parse_lat_lon
from nmea import parse_gpgga_args
from nmea import parse_gprmc_args
from nmea import parse_sentence

class TestNMEA(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_split_sentence(self):
        params = [
            ("", ("", "")),
            ("$", ("", "")),
            ("$*", ("", "")),
            ("$CMD", ("CMD", "")),
            ("$CMD,1,2,3*FF", ("CMD,1,2,3","FF")),
        ]
        for sentence, expected in params:
            with self.subTest(sentence=sentence, expected=expected):
                self.assertEqual(split_sentence(sentence), expected)

    def test_split_body(self):
        params = [
            ("", ("", [])),
            ("CMD", ("CMD", [])),
            ("CMD,1,2,3", ("CMD", ["1", "2", "3"])),
        ]
        for body, expected in params:
            with self.subTest(body=body, expected=expected):
                self.assertEqual(split_body(body), expected)

    def test_compute_checksum(self):
        params = [
            ("", "00"),
            ("CMD", "4A"),
        ]
        for body, expected in params:
            with self.subTest(body=body, expected=expected):
                self.assertEqual(compute_checksum(body), expected)

    def test_create_sentence(self):
        params = [
            ("", "$*00"),
            ("CMD", "$CMD*4A"),
        ]
        for body, expected in params:
            with self.subTest(body=body, expected=expected):
                self.assertEqual(create_sentence(body), expected)

    def test_parse_int(self):
        params = [
            ("", None),
            ("A", None),
            ("2", 2),
        ]
        for value, expected in params:
            with self.subTest(value=value, expected=expected):
                self.assertEqual(parse_int(value), expected)

    def test_parse_float(self):
        params = [
            ("", None),
            ("A", None),
            ("2", 2.0),
        ]
        for value, expected in params:
            with self.subTest(value=value, expected=expected):
                self.assertEqual(parse_float(value), expected)

    def test_parse_degrees(self):
        params = [
            ("", None),
            ("A", None),
            ("1230.00", 12.5),
        ]
        for value, expected in params:
            with self.subTest(value=value, expected=expected):
                self.assertEqual(parse_degrees(value), expected)

    def test_parse_date(self):
        params = [
            ("", (None, None, None)),
            ("0112", (None, 12, 1)),
            ("221133", (2033, 11, 22)),
        ]
        for value, expected in params:
            with self.subTest(value=value, expected=expected):
                self.assertEqual(parse_date(value), expected)

    def test_parse_lat_lon(self):
        params = [
            ("", "", None),
            ("A", "A",  None),
            ("1230.00", "E", 12.5),
            ("1230.00", "W", -12.5),
        ]
        for degree, hemisphere, expected in params:
            with self.subTest(degree=degree, hemisphere=hemisphere, expected=expected):
                self.assertEqual(parse_lat_lon(degree, hemisphere), expected)

    def test_parse_gpgga_args(self):
        params = [
            ("235317.000,4003.9039,N,10512.5793,W,1,08,1.6,1577.9,M,-20.7,M,,0000",
             {'height_geoid': -20.7, 'utc_seconds': 235317, 'horizontal_dilution': 1.6, 'longitude': -105.209655,
              'satellites': 8, 'fix_quality': 1, 'altitude_m': 1577.9, 'latitude': 40.065065}),
        ]
        for args, expected in params:
            with self.subTest(args=args, expected=expected):
                args = dict(zip(nmea.SENTENCE_TYPES['GPGGA'], args.split(',')))
                actual = parse_gpgga_args(args)
                for k in expected.keys():
                    self.assertEqual(actual[k], expected[k])

    def test_parse_gprmc_args(self):
        params = [
            ("235316.000,A,4003.9040,N,10512.5792,W,0.09,144.75,141112,,",
             {'utc_seconds': 235316,'status': 'A', 'latitude': 40.065067,
              'speed_knots': 0.09, 'date': (2012, 11, 14)}
             ),
        ]
        for args, expected in params:
            with self.subTest(args=args, expected=expected):
                args = dict(zip(nmea.SENTENCE_TYPES['GPRMC'], args.split(',')))
                actual = parse_gprmc_args(args)
                for k in expected.keys():
                    self.assertEqual(actual[k], expected[k])

    def test_parse_sentence(self):
        params = [
            ("$GPGGA,BAD_DATA,0000*5F",
             {'error': 'Invalid checksum'}),
            ("$GPRMC,235316.000,A,4003.9040,N,10512.5792,W,0.09,144.75,141112,,*19",
             {'utc_seconds': 235316,'status': 'A', 'latitude': 40.065067,
              'speed_knots': 0.09, 'date': (2012, 11, 14)}),
            ("$GPGGA,235317.000,4003.9039,N,10512.5793,W,1,08,1.6,1577.9,M,-20.7,M,,0000*5E",
             {'utc_seconds': 235317, 'sentence_type': 'GPGGA'}),
            ("$GPGSA,A,3,22,18,21,06,03,09,24,15,,,,,2.5,1.6,1.9*3E",
             {'sentence_type': 'GPGSA', 'field1': 'A'}),

        ]
        for sentence, expected in params:
            with self.subTest(sentence=sentence, expected=expected):
                actual = parse_sentence(sentence)
                self.assertEqual(actual['sentence'], sentence)
                for k in expected.keys():
                    self.assertEqual(actual[k], expected[k])


if __name__ == '__main__':
    unittest.main()