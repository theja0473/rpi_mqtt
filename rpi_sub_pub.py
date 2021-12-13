#!/usr/bin/env python
# python 3.6
import os
import json
import random
import time
import logging
import logging.config
import yaml
import requests
from paho.mqtt import client as mqtt_client
import setup_logging

try:
    BROKER = os.getenv('BROKER', '15.206.172.147')
    PORT = int(os.getenv('PORT', 1883))
    SUB_TOPIC = os.getenv('SUB_TOPIC', 'TopicDeviceVersionURL')
    PUB_TOPIC = os.getenv('PUB_TOPIC', 'TopicCurrentDeviceVerison')
    localfile = os.getenv('localfile',"data.txt")
except:
    sys.exit(1)

FLAG_CONNECTED = 0
setup_logging.setup_logging(default_level=logging.DEBUG)
logger = logging.getLogger(__name__)

def readlocalfile(filename):
    with open(filename, 'r') as file:
        data = file.read().rstrip()
        data = data.split('=')
    return data[1]

def on_connect(client, userdata, flags, rc):
    global FLAG_CONNECTED
    if rc == 0:
        FLAG_CONNECTED = 1
        logger.info("Connected to MQTT Broker!")
        client.subscribe(SUB_TOPIC)
    else:
        logger.error("Failed to connect, return code {rc}".format(rc=rc), )


def on_message(client, userdata, msg):
    logger.info("Received `{payload}` from `{topic}` topic".format(payload=msg.payload.decode(), topic=msg.topic))
    try:
        message = json.loads(msg.payload.decode())
        URL = message['url']
    except:
        logger.error("JSON loading and saparating URL is failed...")
    try:
        r = requests.get(URL, allow_redirects=True)
        logger.info("Downloading `{file}` to local sucessfull".format(file=URL))
    except:
        logger.error("Failed to download file using `{url}`".format(url=URL))

    try:
        open(localfile, 'wb').write(r.content)
        logger.info("Writing `{content}` to `{file}` sucessfull".format(content=r.content, file=localfile))
    except:
        logger.error("Failed to write `{content}` to `{file}` sucessfull".format(content=r.content, file=localfile))

def connect_mqtt():
    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT)
    return client


def publish(client):
    while True:
        version=readlocalfile(localfile)
        msg="{deviceVersion: "+str(version)+" }"
        result = client.publish(PUB_TOPIC, msg)
        status = result[0]
        if status == 0:
            logger.info("Send `{msg}` to topic `{topic}` successfull".format(msg=msg, topic=PUB_TOPIC))
        else:
            logger.error("Failed to send message to topic {topic}".format(topic=PUB_TOPIC))
        time.sleep(5)

def main():
    client = connect_mqtt()
    client.loop_start()
    time.sleep(1)
    if FLAG_CONNECTED:
        publish(client)
    else:
        client.loop_stop()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.error('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
