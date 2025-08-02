from models import Config, AlertList, AuroraAlert
from util import send_email

import aiocron
import aiohttp
import aiosmtplib
from pydantic import ValidationError
from datetime import datetime
from tzlocal import get_localzone

local_tz = get_localzone()
local_time = lambda: datetime.now(local_tz).isoformat()

class App:
    def __init__(self, service_name, config: Config):
        self._service_name = service_name
        self._config = config
        self._smtp_client = aiosmtplib.SMTP(
            hostname=config.smtp_url,
            port=config.smtp_port,
            use_tls=config.smtp_use_tls,
            username=config.smtp_username,
            password=config.smtp_password
        )

    async def _send_email(
        self,
        subject,
        body
    ):
        await send_email(
            smtp_client= self._smtp_client,
            frm = self._config.smtp_send_from,
            to = self._config.smtp_send_to,
            subject= subject,
            body= body
        )

    async def send_alert_message(
        self,
        data: AlertList,
    ):
        AuroraAlert.model_validate_json(data)

        body = (
            f"Dear {self._config.smtp_send_to}\n"
            f"There are aurora alerts:\n"
        )
        for d in data:
            d: AuroraAlert
            body += (
                f"Description: {d.description}\n"
                f"Between: {d.start_time} and : {d.valid_until}\n"
                f"K-index: {d.k_aus}, Latitude band: {d.lat_band}\n\n"
             )

        body += (
            f"{body}\n\n"
            f"Sent at {local_time()} by {self._service_name}"
        )

        await self._send_email(
            subject=f"{self._service_name} - Aurora Alert!",
            body=body
        )

    async def send_wake_up_msg(
        self,
    ):
        await self._send_email(
            subject=f"{self._service_name} - Service Started",
            body = (
                f"Dear {self._config.smtp_send_to}\n\n"
                f"AuroraWatch Service has started at {local_time()}"
            )
        )

    async def run(self):
        await self.send_wake_up_msg()

        async with aiohttp.ClientSession() as session:
            while True:
                await aiocron.crontab('*/10 * * * *').next()

                async with (
                    session.post(
                        self._config.bom_aurora_url,
                        json={
                            "api_key": self._config.bom_api_key
                        }
                    ) as response
                ):
                    t = await response.text()
                    try:
                        parsed = AlertList.validate_json(t)
                    except ValidationError as e:
                        print(f"Validation Error {e}")
                        continue

                await self.send_alert_message(
                    parsed,
                )