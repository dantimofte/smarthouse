from fastapi import FastAPI, Request, HTTPException
import structlog
from smarthouse.automations.dogshed.temp_control import DogshedTempControl
from smarthouse.log import initlog
from smarthouse.sensors.ewelink_client.ewelink_controller import get_ewelink_client
from dotenv import load_dotenv
import logging
import io
import traceback

load_dotenv(".env")
app = FastAPI()
initlog(logging.INFO, True)
log = structlog.get_logger(name=__name__)


ELECTRIC_HEATING_CLIENT = get_ewelink_client()
TEMP_CONTROL_CLIENT = DogshedTempControl(ELECTRIC_HEATING_CLIENT)


def get_exception_traceback_str(exc: Exception) -> str:
    file = io.StringIO()
    traceback.print_exception(exc, file=file)
    return file.getvalue().rstrip()


@app.on_event("startup")
async def startup_event():
    await ELECTRIC_HEATING_CLIENT.login()
    device = ELECTRIC_HEATING_CLIENT.get_device('1000ce120a')
    params: dict = device.raw_data["params"]
    switch = params["switch"]
    main_switch = params["mainSwitch"]
    device_type = params["deviceType"]
    current_temperature = params["currentTemperature"]
    targets = params["targets"]

    log.info(f"Current temperature: {current_temperature}")
    log.info(f"switch: {switch}")
    log.info(f"main_switch: {main_switch}")
    log.info(f"device_type: {device_type}")
    log.info(f"targets: {targets}")
    ELECTRIC_HEATING_CLIENT.ws.listeners.append(log.info)


@app.on_event("shutdown")
async def shutdown_event():
    # Add dispose logic here.
    await ELECTRIC_HEATING_CLIENT.dispose()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/switch_bot")
async def switchbot_webhook(request: Request):
    try:
        message = await request.json()
        TEMP_CONTROL_CLIENT.cb_switchbot_update(message)
    except Exception as e:
        error = get_exception_traceback_str(e)
        log.error(f"Error: {error}")
        raise HTTPException(status_code=404, detail=e)
    log.info(f"received request: {message}")
    return {"status": "ok"}
