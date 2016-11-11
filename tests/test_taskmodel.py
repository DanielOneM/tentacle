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

    def test_crontab_serializing(self):
        """Correct serialization."""
        crtab = {
            'minute': '1',
            'hour': '1',
            'day_of_week': '1',
            'day_of_month': '1',
            'month_of_year': '1'
        }

        sch = Crontab.from_dict(crtab)
        self.assertEqual(sch.to_dict(), crtab)

    def test_crontab_deserializing(self):
        """Correct deserialization."""
        crtab = {
            'minute': '1',
            'hour': '1',
            'day_of_week': '1',
            'day_of_month': '1',
            'month_of_year': '1'
        }

        sch = Crontab.from_dict(crtab)
        self.assertIsInstance(sch, Crontab)
        self.assertEqual(sch.minute, crtab['minute'])


class TestTaskModel(unittest.TestCase):
    """Used to test the TaskModel object."""

    def setUp(self):
        """Initializing common objects."""
        self.task = {
            'name': 'something',
            'worker_type': 'kraken',
            'task': 'something',
            'interval': {'every': 7, 'period': 'days'},
            'crontab': None
        }

    def test_init(self):
        """Correct initialization."""
        tsk = TaskModel(**self.task)

        self.assertEqual(tsk.name, 'something')
        self.assertEqual(tsk.worker_type, 'kraken')
        self.assertIsNone(tsk.description)
        self.assertIsNone(tsk.crontab)
        self.assertIsNotNone(tsk.interval)
        self.assertEqual(tsk.run_immediately, False)

    def test_init_no_name(self):
        """Initializing without a name."""
        self.task['name'] = None
        tsk = TaskModel(**self.task)
        self.task.pop('name')
        tsk2 = TaskModel(**self.task)

        self.assertIsNotNone(tsk.name)
        self.assertIsNotNone(tsk2.name)
        self.assertNotEqual(tsk.name, tsk2.name)

    def test_invalid_no_attribs(self):
        """Exception when there's no interval and no crontab."""
        self.task['interval'] = None

        self.assertRaisesRegexp(ValueError,
                                'Must define either interval or crontab schedule.',
                                TaskModel, **self.task)

    def test_invalid_too_many_attribs(self):
        """Exception when there's both interval and crontab."""
        self.task['crontab'] = {}

        self.assertRaisesRegexp(ValueError,
                                'Cannot define both interval and crontab schedule.',
                                TaskModel, **self.task)

    def test_schedule(self):
        """Correct schedule is used."""
        tsk = TaskModel(**self.task)

        self.assertIsInstance(tsk.schedule, celery.schedules.schedule)
