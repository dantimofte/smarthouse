import unittest
from unittest import mock
from smarthouse.automations.dogshed.temp_control import DogshedTempControl


SB_UPDATES = [
    {'eventType': 'changeReport', 'eventVersion': '1', 'context': {'deviceType': 'WoIOSensor', 'deviceMac': 'C74F39E75800', 'temperature': 4.9, 'humidity': 89, 'battery': 100, 'scale': 'CELSIUS', 'timeOfSample': 1704180107274}},
    {'eventType': 'changeReport', 'eventVersion': '1', 'context': {'deviceType': 'WoIOSensor', 'deviceMac': 'FE536C4C976F', 'temperature': 14.8, 'humidity': 53, 'battery': 100, 'scale': 'CELSIUS', 'timeOfSample': 1704178690656}}
]


class TestDogShedTempControl(unittest.TestCase):
    def setUp(self):
        self.temp_control = DogshedTempControl()

    def tearDown(self):
        self.temp_control.dispose()

    def test_new_instance(self):
        assert isinstance(self.temp_control, DogshedTempControl)

    def test_cb_switchbot_update(self):
        message = SB_UPDATES[0]
        self.temp_control.cb_switchbot_update(message)
        assert self.temp_control.outside_temperature == message["context"]["temperature"]
