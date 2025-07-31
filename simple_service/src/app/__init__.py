from email.message import EmailMessage
from typing import Annotated

import asyncio
import aiocron
import aiohttp
import aiosmtplib
import json
from pydantic import BaseModel, TypeAdapter, ValidationError
from datetime import datetime

class AuroraAlert(BaseModel):
    start_time: datetime
    valid_until: datetime
    k_aus: float
    lat_band: str
    description: str

AlertList = TypeAdapter(list[AuroraAlert])

def make_alert_message(to, data: AlertList, frm="aurora-alert@gmail.com"):
    AuroraAlert.model_validate_json(data)
    message = EmailMessage()
    message["From"] = frm
    message["To"] = to
    message["Subject"] = "Aurora Alert!"

    body = ""
    for d in data:
        d: AuroraAlert
        body += (
            f"Description: {d.description}\n"
            f"Between: {d.start_time} and : {d.valid_until}\n"
            f"K-index: {d.k_aus}, Latitude band: {d.lat_band}\n\n"
         )
    message.set_content(
        f"""
        Dear {frm}
        There are aurora alerts:
        {body}
        """)
    return message

async def app(
    api_key,
    send_to="",
    send_from="",
    smtp_username="",
    smtp_password="",
    smtp_url="smtp.gmail.com",
    smtp_port=465,
    use_tls=True,
    aurora_url='https://sws-data.sws.bom.gov.au/api/v1/get-aurora-alert',
):
    async with aiohttp.ClientSession() as session:
        smtp_client = aiosmtplib.SMTP(
            hostname=smtp_url,
            port=smtp_port,
            use_tls=use_tls,
            username=smtp_username,
            password=smtp_password
        )

        while True:
            await aiocron.crontab('* * * * *').next()

            async with (
                session.post(
                    aurora_url,
                    json={
                        "api_key": api_key
                    }
                ) as response
            ):
                t = await response.text()
                try:
                    parsed = AlertList.validate_json(t)
                except ValidationError as e:
                    print(f"Validation Error {e}")
                    continue

                async with smtp_client:
                    await smtp_client.send_message(
                        make_alert_message(
                            data=parsed,
                            to = send_to,
                            frm = send_from,
                        )
                    )


if __name__ == "__main__":
    asyncio.run(app(...))