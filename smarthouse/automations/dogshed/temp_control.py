"""
temperature rules:
    1. if outside temperature > 10 Celsius stop the heating
    2. if  0 Celsius <=  outside temperature <= 10 Celsius > maintain heat in floor between 20 and 40 degrees
    3. if outside temperature <= 0 Celsius maintain heat in floor between 50 and 60 degrees
    4. if inside temperature >= 20 Celsius set floor temperature between 20 and 40 degrees

"""
from smarthouse.sensors.common.models import SensorConfig
import structlog
import ewelink
import asyncio

log = structlog.get_logger(name=__name__)

OUTSIDE_SENSOR_CONFIG = SensorConfig(
    sensor_id="C74F39E75800",
    sensor_weight=1,
    rules=[]
)

DOGSHED_SENSOR_CONFIG = SensorConfig(
    sensor_id="FE536C4C976F",
    sensor_weight=1,
    rules=[]
)

UPPER_OUTSIDE_TEMPERATURE = 10  # no heating above this value
LOWER_OUTSIDE_TEMPERATURE = 0  # high heating bellow this
INSIDE_TEMPERATURE_LIMIT = 20  # maintain temperature
FLOOR_TEMPERATURE_RANGES = [
    (20, 40),
    (50, 60)
]


class DogshedTempControl:
    def __init__(self, electric_heating_client: ewelink):
        self.electric_heating_client = electric_heating_client
        self.outside_temperature = None
        self.inside_temperature = None

    def cb_switchbot_update(self, message):
        # 1 update relevant properties
        log.info("message: {}".format(message))
        sensor_id = message["context"]["deviceMac"]

        # only call state updated if we get a notification from the sensors we are interested in
        state_changed = False
        if sensor_id == OUTSIDE_SENSOR_CONFIG.sensor_id:
            state_changed = True
            self.outside_temperature = message["context"]["temperature"]

        if sensor_id == DOGSHED_SENSOR_CONFIG.sensor_id:
            state_changed = True
            self.inside_temperature = message["context"]["temperature"]

        # check if we need to change settings
        if state_changed:
            asyncio.create_task(self._on_state_updated())

    async def _on_state_updated(self) -> None:
        if self.outside_temperature is None:
            return

        if self.outside_temperature > UPPER_OUTSIDE_TEMPERATURE + 0.5:
            log.info(f"Outside temperature: {self.outside_temperature} => stop heating")
            await self.stop_heating()

        if 0 < self.outside_temperature <= 10:
            # maintain heat in floor between 20 and 40 degrees
            log.info(f"Outside temperature: {self.outside_temperature} => set heat range [20, 40]")
            await self.set_heating_range(20, 40)

        if self.outside_temperature <= 0:
            # maintain heat in floor between 40 and 60 degrees
            log.info(f"Outside temperature: {self.outside_temperature} => set heat range [40, 60]")
            await self.set_heating_range(40, 60)

        # exit here if there are no readings from the inside sensor
        if self.inside_temperature is None:
            return

        # this might need a bit more thought
        if self.inside_temperature >= INSIDE_TEMPERATURE_LIMIT:
            # set floor temperature between 20 and 40 degrees
            log.info(f"Inside temperature: {self.inside_temperature} => set heat range [20, 40] ")
            await self.set_heating_range(20, 40)

    async def stop_heating(self):
        params = {
            "switch": "off",
            "mainSwitch": "off",
            "deviceType": "normal",
        }
        resp = await self.electric_heating_client.ws.update_device_status("1000ce120a", **params)
        log.info(f"update targets resp {resp}")

    async def set_heating_range(self, min_temp, max_temp):
        params = {
            "switch": "on",
            "deviceType": "temperature",
            "mainSwitch": "on",
            "controlType": 9,
            "targets": [
                {"targetHigh": "63", "reaction": {"switch": "off"}},
                {"targetLow": "53", "reaction": {"switch": "on"}}
            ]
        }
        resp = await self.electric_heating_client.ws.update_device_status("1000ce120a", **params)
        print(f"update targets resp {resp}")

    def dispose(self):
        pass
