import unittest

from pyramid import testing


def dummy_request(dbsession):
    return testing.DummyRequest(dbsession=dbsession)


class BaseTest(unittest.TestCase):
    def setUp(self):
        pass

    def init_database(self):
        pass

    def tearDown(self):
        pass


class TestMyViewSuccessCondition(BaseTest):

    def setUp(self):
        super(TestMyViewSuccessCondition, self).setUp()
        pass

    def test_passing_view(self):
        pass


class TestMyViewFailureCondition(BaseTest):

    def test_failing_view(self):
        pass
