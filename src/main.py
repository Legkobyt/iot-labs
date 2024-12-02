import json

from apprise import Apprise
from loguru import logger
import paho.mqtt.client as mqtt

from Model import Notification, Settings

settings  = Settings()
logger.debug(settings)

def on_connect(client: mqtt.Client, userdata, flags, reason_code, properties):
    logger.debug(f"Connected with result code {reason_code}")
    client.subscribe(settings.base_topic)
    client.subscribe(settings.base_topic + '/cmd')

    client.publish(settings.base_topic + '/status', json.dumps({"status": "online"}), retain=True)


def handle_commands(client: mqtt.Client, payload: dict):
    if payload['cmd'] == 'shutdown':
        logger.info('Going to shutdown')
        client.publish(settings.base_topic + 'status', json.dumps({"status": "offline"}), retain=True)
        client.disconnect()
        client.loop_stop()


def notify(payload: dict):
    logger.info('Notifying client')
    notification =  Notification(**payload)
    apprise = Apprise()
    apprise.add(str(notification.urls))
    apprise.notify(
        body=notification.body,
        title=notification.title,
    )


def on_message(client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
    logger.debug(f'{msg.topic}: {msg.payload}')

    payload = json.loads(msg.payload)

    if msg.topic.endswith('/cmd'):
        handle_commands(client, payload)
    else:
        notify(payload)



def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(settings.user, settings.password)
    client.will_set(settings.base_topic + 'status', json.dumps({"status": "offline"}), retain=True)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(settings.broker, settings.port, 60)

    logger.info('Waiting for messages.')
    client.loop_forever()
    logger.info('Good bye.')


if __name__ == '__main__':
    main()