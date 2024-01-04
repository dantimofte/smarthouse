import dataclasses
from typing import List


@dataclasses.dataclass
class SensorRule:
    rule_id: int
    condition: str
    target_value: int
    action: str
    action_target: str
    activated: bool = False

    def triggered(self, value: int):
        if self.condition == "GREATER_THEN":
            self.activated = value > self.target_value


@dataclasses.dataclass
class SensorConfig:
    sensor_id: str
    sensor_weight: int
    rules: List[SensorRule]
