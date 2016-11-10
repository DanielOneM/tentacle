"""Unit tests for various helper objects."""

import unittest

import celery.schedules

from tentacle.taskmodel import (Interval, Crontab, TaskModel)


class TestHelperObjects(unittest.TestCase):
    """Used to test Interval and Crontab objects."""

    def test_interval_correct_period_init(self):
        """Using getter with correct data set."""
        i = Interval()
        i.period = 'days'

        self.assertEqual(i.period, 'days')

    def test_interval_get_period_no_data(self):
        """Using getter with no data set."""
        i = Interval()

        self.assertRaisesRegexp(ValueError,
                                "'period' attribute cannot be None.",
                                getattr, i, 'period')

    def test_interval_set_period_bad_data(self):
        """Exception when initializing with bad data."""
        i = Interval()

        self.assertRaises(ValueError,
                          setattr, i, 'period', 'something')

    def test_interval_correct_every_init(self):
        """Using getter with correct data set."""
        i = Interval()

        i.every = '7'
        self.assertEqual(i.every, 7)

        i.every = 7
        self.assertEqual(i.every, 7)

    def test_interval_set_every_no_data(self):
        """Every is set to zero."""
        i = Interval()

        i.every = None
        self.assertEqual(i.every, 0)

    def test_interval_set_every_bad_data(self):
        """Exception when initializing with bad data."""
        i = Interval()

        self.assertRaisesRegexp(ValueError,
                                "Value must be a positive integer.",
                                setattr, i, 'every', -12)
        self.assertRaisesRegexp(ValueError,
                                "Value must be a positive integer.",
                                setattr, i, 'every', 'something')

    def test_interval_serializing(self):
        """Correct serialization."""
        i = Interval()
        i.period = 'days'
        i.every = 7

        self.assertEqual(i.to_dict(), {'every': 7, 'period': 'days'})

    def test_interval_deserializing(self):
        """Correct deserialization."""
        data = {'every': 7, 'period': 'days'}

        i = Interval.from_dict(data)
        self.assertEqual(i.period, 'days')
        self.assertEqual(i.every, 7)

    def test_interval_deserializing_no_data(self):
        """No data when deserializing."""
        i = Interval.from_dict(None)

        self.assertIsNone(i)

    def test_interval_has_schedule(self):
        """Interval schedule property is valid."""
        i = Interval()
        i.period = 'days'
        i.every = 7

        self.assertIsInstance(i.schedule, celery.schedules.schedule)

    def test_crontab_init(self):
        """Correct initialization."""
        pass

    def test_crontab_bad_data(self):
        """Exception when initializing with bad data."""
        pass

    def test_crontab_serializing(self):
        """Correct serialization."""
        pass

    def test_crontab_deserializing(self):
        """Correct deserialization."""
        pass


class TestTaskModel(unittest.TestCase):
    """Used to test the TaskModel object."""

    def test_init(self):
        """Correct initialization."""
        pass

    def test_validate(self):
        """All attributes must validate."""
        pass

    def test_invalid_no_attribs(self):
        """Exception when there's no interval and no crontab."""
        pass

    def test_invalid_too_many_attribs(self):
        """Exception when there's both interval and crontab."""
        pass

    def test_schedule(self):
        """Correct schedule is used."""
        pass
