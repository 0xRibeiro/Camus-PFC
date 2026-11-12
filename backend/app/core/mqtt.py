from fastapi_mqtt import FastMQTT, MQTTConfig

from app.core.config import settings

# config da conexao com o mosquitto, reconecta sozinho se o broker cair
mqtt_config = MQTTConfig(host=settings.mqtt_host, port=settings.mqtt_port)

# objeto cliente mqtt universal, os dominios usam pra assinar topico e publicar
mqtt = FastMQTT(config=mqtt_config)
