from unittest import TestCase
from ThreatPlaybook import ThreatPlaybook
import unittest


class TestThreatPlaybook(TestCase):
    def setUp(self):
        self.tp = ThreatPlaybook("test project")

    def test_load_entity_file(self):
        self.tp.load_entity_file(filepath = "/Users/abhaybhargav/Documents/Code/Python/ThreatPlaybook/example/entities/new_entities.yml")
        self.assertTrue(self.tp.entity_info)

    # def test_find_or_create_entities(self):
    #     self.tp.find_or_create_entities()
    #
    # def test_find_or_connect_entities(self):
    #     self.tp.find_or_connect_entities()
    #
    # # def test_process_test_cases(self):
    # #     self.fail()


if __name__ == '__main__':
    unittest.main()