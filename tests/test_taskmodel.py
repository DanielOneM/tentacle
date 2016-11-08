"""Unit tests for various helper objects."""

import unittest

from tentacle.taskmodel import (Interval, Crontab, TaskModel)


class TestHelperObjects(unittest.TestCase):
    """Used to test Interval and Crontab objects."""

    def setUp(self):
        """Initialize common objects."""
        pass

    def test_interval_init(self):
        """Correct initialization."""
        pass

    def test_interval_bad_data(self):
        """Exception when initializing with bad data."""
        pass

    def test_interval_serializing(self):
        """Correct serialization."""
        pass

    def test_interval_deserializing(self):
        """Correct deserialization."""
        pass

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
