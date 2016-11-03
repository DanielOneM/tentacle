"""Unit tests for various helper objects."""

import unittest

from tentacle.tentacle.taskmodel import (Interval, Crontab, TaskModel)


class TestHelperObjects(unittest.TestCase):
    """Used to test Interval and Crontab objects."""

    def test_interval_init(self):
        pass

    def test_interval_wrong_data(self):
        pass

    def test_interval_serializing(self):
        pass

    def test_interval_deserializing(self):
        pass

    def test_crontab_init(self):
        pass

    def test_crontab_serializing(self):
        pass

    def test_crontab_deserializing(self):
        pass


class TestTaskModel(unittest.TestCase):
    """Used to test the TaskModel object."""

    def test_init(self):
        pass

    def test_validate(self):
        pass

    def test_no_period(self):
        pass

    def test_invalid_period(self):
        pass

    def test_schedule(self):
        pass

    def test_no_schedule_period(self):
        pass
