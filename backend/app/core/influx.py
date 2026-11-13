from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync

from app.core.config import settings


# abre um por uso, o cliente async precisa do loop rodando
def cliente_influx() -> InfluxDBClientAsync:
    return InfluxDBClientAsync(url=settings.influx_url, token=settings.influx_token, org=settings.influx_org)
