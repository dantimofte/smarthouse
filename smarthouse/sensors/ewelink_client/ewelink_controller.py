import asyncio
import os
import structlog
from smarthouse.log import initlog
import logging
import ewelink

log = structlog.get_logger(name=__name__)


def get_ewelink_client():
    username = os.getenv("EWELINK_USERNAME")
    password = os.getenv("EWELINK_PASSWORD")
    client = ewelink.Client(password, username, region="eu")
    return client


async def main():
    initlog(logging.INFO, True)
    client: ewelink.Client = get_ewelink_client()
    await client.login()
    device = client.get_device('1000ce120a')

    try:
        await device.on()
    except ewelink.DeviceOffline:
        print("Device is offline!")

    await client.http.session.close()

if __name__ == '__main__':
    asyncio.run(main())
