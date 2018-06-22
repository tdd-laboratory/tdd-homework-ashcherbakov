import unittest

import library

NUM_CORPUS = '''
On the 5th of May every year, Mexicans celebrate Cinco de Mayo. This tradition
began in 1845 (the twenty-second anniversary of the Mexican Revolution), and
is the 1st example of a national independence holiday becoming popular in the
Western Hemisphere. (The Fourth of July didn't see regular celebration in the
US until 15-20 years later.) It is celebrated by 77.9% of the population--
trending toward 80.                                                                
'''


class TestCase(unittest.TestCase):
    # Helper function
    def assert_extract(self, text, extractors, *expected):
        actual = [x[1].group(0) for x in library.scan(text, extractors)]
        self.assertEquals(str(actual), str([x for x in expected]))

    # First unit test; prove that if we scan NUM_CORPUS looking for mixed_ordinals,
    # we find "5th" and "1st".
    def test_mixed_ordinals(self):
        self.assert_extract(NUM_CORPUS, library.mixed_ordinals, '5th', '1st')

    # Second unit test; prove that if we look for integers, we find four of them.
    def test_integers(self):
        self.assert_extract(NUM_CORPUS, library.integers, '1845', '15', '20', '80')

    def test_integers_with_grouping(self):
        self.assert_extract('aaa 123,456,789 bbb', library.integers, '123,456,789')
        self.assert_extract('123,456,789', library.integers, '123,456,789')
        self.assert_extract('aaa 123,456,789 456,678 bbb', library.integers, '123,456,789', '456,678')
        self.assert_extract('123,456,789 456,678', library.integers, '123,456,789', '456,678')
        self.assert_extract('aaa 123,456,789 456,678 456 bbb', library.integers, '123,456,789', '456,678', '456')
        self.assert_extract('123,456,789 456', library.integers, '123,456,789', '456')

    # Third unit test; prove that if we look for integers where there are none, we get no results.
    def test_no_integers(self):
        self.assert_extract("no integers", library.integers)

    # prove that if we look for dates, we find them.
    def test_dates_iso8601(self):
        self.assert_extract('I was born on 2015-07-25.', library.dates_iso8601, '2015-07-25')

    def test_dates_iso8601_timestamp_millisec(self):
        self.assert_extract('I was born on 2015-07-25 18:22:19.123.', library.dates_iso8601, '2015-07-25 18:22:19.123')

    def test_dates_iso8601_timestamp_sec(self):
        self.assert_extract('I was born on 2015-07-25 18:22:19.', library.dates_iso8601, '2015-07-25 18:22:19')

    def test_dates_iso8601_timestamp_min(self):
        self.assert_extract('I was born on 2015-07-25 18:22.', library.dates_iso8601, '2015-07-25 18:22')

    def test_dates_iso8601_timestamp_delimiter(self):
        self.assert_extract('I was born on 2015-07-25T18:22:19.123.', library.dates_iso8601, '2015-07-25T18:22:19.123')
        self.assert_extract('I was born on 2015-07-25T18:22:19.', library.dates_iso8601, '2015-07-25T18:22:19')
        self.assert_extract('I was born on 2015-07-25T18:22.', library.dates_iso8601, '2015-07-25T18:22')

    def test_dates_iso8601_timezone_3letter(self):
        self.assert_extract('I was born on 2015-07-25 18:22:19.123MDT.', library.dates_iso8601,
                            '2015-07-25 18:22:19.123MDT')
        self.assert_extract('I was born on 2015-07-25T18:22:19.123MDT.', library.dates_iso8601,
                            '2015-07-25T18:22:19.123MDT')
        self.assert_extract('I was born on 2015-07-25 18:22:19MDT.', library.dates_iso8601, '2015-07-25 18:22:19MDT')
        self.assert_extract('I was born on 2015-07-25 18:22MDT.', library.dates_iso8601, '2015-07-25 18:22MDT')

    def test_dates_iso8601_timezone_1letter(self):
        self.assert_extract('I was born on 2015-07-25 18:22:19.123Z.', library.dates_iso8601,
                            '2015-07-25 18:22:19.123Z')
        self.assert_extract('I was born on 2015-07-25T18:22:19.123Z.', library.dates_iso8601,
                            '2015-07-25T18:22:19.123Z')
        self.assert_extract('I was born on 2015-07-25 18:22:19Z.', library.dates_iso8601, '2015-07-25 18:22:19Z')
        self.assert_extract('I was born on 2015-07-25 18:22Z.', library.dates_iso8601, '2015-07-25 18:22Z')

    def test_dates_iso8601_timezone_offset(self):
        self.assert_extract('I was born on 2015-07-25 18:22:19.123-0800.',
                            library.dates_iso8601, '2015-07-25 18:22:19.123-0800')
        self.assert_extract('I was born on 2015-07-25T18:22:19.123-0800.', library.dates_iso8601,
                            '2015-07-25T18:22:19.123-0800')
        self.assert_extract('I was born on 2015-07-25 18:22:19-0800.', library.dates_iso8601,
                            '2015-07-25 18:22:19-0800')
        self.assert_extract('I was born on 2015-07-25 18:22-0800.', library.dates_iso8601,
                            '2015-07-25 18:22-0800')

    # prove that if we look for dates, then the month must be in the interval [1,12]
    def test_dates_iso8601_incorrect_month(self):
        self.assert_extract('I was born on 2015-13-25.', library.dates_iso8601)
        self.assert_extract('I was born on 2015-00-25.', library.dates_iso8601)
        self.assert_extract('I was born on 2015-99-25.', library.dates_iso8601)

    # prove that if we look for dates, then the day must be in the interval [1,31]
    def test_dates_iso8601_incorrect_day(self):
        self.assert_extract('I was born on 2015-07-00.', library.dates_iso8601)
        self.assert_extract('I was born on 2015-07-32.', library.dates_iso8601)
        self.assert_extract('I was born on 2015-07-99.', library.dates_iso8601)

    def test_dates_fmt2(self):
        self.assert_extract('I was born on 25 Jan 2017.', library.dates_fmt2, '25 Jan 2017')

    def test_dates_fmt2_with_comma(self):
        self.assert_extract('I was born on 25 Jan, 2017.', library.dates_fmt2, '25 Jan, 2017')

    def test_dates_fmt2_multiple(self):
        self.assert_extract('I was born on 25 Jan 2017 and you were born on 01 Dec 1901.', library.dates_fmt2,
                            '25 Jan 2017', '01 Dec 1901')

    def test_dates_iso8601_multiple(self):
        self.assert_extract('I was born on 2015-07-27 and you were born on 1900-07-01.', library.dates_iso8601,
                            '2015-07-27', '1900-07-01')

    def test_dates_fmt2_no_year(self):
        self.assert_extract('I was born on 25 Jan and you were born on 01 Dec.', library.dates_fmt2)

    def test_dates_iso8601_no_year(self):
        self.assert_extract('I was born on 01-25 and you were born on 01-01.', library.dates_fmt2)


if __name__ == '__main__':
    unittest.main()
