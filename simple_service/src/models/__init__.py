import datetime
from pydantic import BaseModel, TypeAdapter


class AuroraAlert(BaseModel):
    start_time: datetime.datetime
    valid_until: datetime.datetime
    k_aus: float
    lat_band: str
    description: str

AlertList = TypeAdapter(list[AuroraAlert])

class Config(BaseModel):
    bom_api_key: str = ""
    smtp_send_to: str = ""
    smtp_send_from: str = ""
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_url: str = "smtp.gmail.com"
    smtp_port: int = 465
    smtp_use_tls: bool = True
    bom_aurora_url: str = 'https://sws-data.sws.bom.gov.au/api/v1/get-aurora-alert'

if __name__ == "__main__":
    # if we run this build a config template file
    with open( "./config_template.conf", "w" ) as cf:
        c = Config()
        cf.write(c.model_dump_json(indent=2))
