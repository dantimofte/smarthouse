import json
import asyncio
import time
import hashlib
import hmac
import base64
import uuid
import aiohttp
from dotenv import load_dotenv
import os
import structlog
from smarthouse.log import initlog
import logging


load_dotenv(".env")
API_TOKEN = os.getenv("SWITCHBOT_API_KEY")
API_SECRET = os.getenv("SWITCHBOT_API_SECRET")
REST_API_URL = "https://api.switch-bot.com/"


log = structlog.get_logger(name=__name__)


def get_auth_headers(token, secret):
    generated_uuid4 = uuid.uuid4()
    mts = int(round(time.time() * 1000))
    string_to_sign = '{}{}{}'.format(token, mts, generated_uuid4)

    string_to_sign = bytes(string_to_sign, 'utf-8')
    secret = bytes(secret, 'utf-8')
    sign = base64.b64encode(hmac.new(secret, msg=string_to_sign, digestmod=hashlib.sha256).digest())

    api_headers: dict = {
        "Authorization": token,
        "Content-Type": "application/json",
        "charset": "utf8",
        "t": str(mts),
        "sign": str(sign, 'utf-8'),
        "nonce": str(generated_uuid4)
    }
    return api_headers


async def send_request(session, method, endpoint, headers, data):
    response = await session.request(method, f"{REST_API_URL}{endpoint}", headers=headers, data=json.dumps(data))
    try:
        response.raise_for_status()
        return await response.json()
    except Exception as e:
        log.exception(e)


async def get_devices(session, headers):
    devices = await send_request(session, "GET", "v1.1/devices", headers, "")
    return devices


async def get_temperature(session, headers):
    devices_data = await get_devices(session, headers)
    # print(f"devices found: {devices_data}")

    dog_sensor_id = [
        entry["deviceId"]
        for entry in devices_data["body"]["deviceList"]
        if entry["deviceName"] == "Cusca Bacsi si Desi"
    ][0]
    dog_sensor_status = await send_request(session, "GET", f"v1.1/devices/{dog_sensor_id}/status", headers, "")
    log.info(f"dog sensor status: {dog_sensor_status}")


async def set_webhook_url(session, headers, webhook_url):
    endpoint = "v1.1/webhook/setupWebhook"
    body = {
        "action": "setupWebhook",
        "url": webhook_url,
        "deviceList": "ALL"
    }
    set_wh_status = await send_request(session, "POST", endpoint, headers, body)
    log.info(f"webhook status: {set_wh_status}")


async def get_webhook_configuration(session, headers):
    endpoint = "v1.1/webhook/queryWebhook"
    body = {
        "action": "queryUrl"
    }
    get_wh_status = await send_request(session, "POST", endpoint, headers, body)
    log.info(f"webhook configuration: {get_wh_status}")


async def main():
    session = aiohttp.ClientSession()
    headers = get_auth_headers(API_TOKEN, API_SECRET)
    # await get_temperature(session, headers)
    # await set_webhook_url(session, headers, "https://sb.qal.io/switch_bot")
    await get_webhook_configuration(session, headers)
    await session.close()


if __name__ == "__main__":
    initlog(logging.INFO, True)
    if API_TOKEN is None or API_SECRET is None:
        log.error("API token or secret not set")
        exit(1)
    asyncio.run(main())
