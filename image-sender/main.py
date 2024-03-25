import json
import logging
import time
import os
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from test.test_monitoring import ExceptionRecorder

from input_controller import InputController, InvalidSourceException
import log_config

memory_handler = log_config.setup_logging()
logger = logging.getLogger(__name__)
logger.info("Image-Sender Started")

class MQTTConfigException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

mqtt_broker = os.getenv("MQTT_BROKER")
if mqtt_broker is None:
    raise MQTTConfigException("Missing MQTT_BROKER evironment variable")
mqtt_port = os.getenv("MQTT_PORT")
if mqtt_port is None:
    raise MQTTConfigException("Missing MQTT_PORT evironment variable")
mqtt_topic = os.getenv("MQTT_TOPIC")
if mqtt_topic is None:
    raise MQTTConfigException("Missing MQTT_TOPIC evironment variable")

port_num = int(mqtt_port)
mqtt_keepalive_interval = 45
mqtt_availability_topic = f"{mqtt_topic}/availability"
mqtt_online_payload = "online"
mqtt_offline_payload = "offline"

default_source = os.getenv("DEFAULT_SOURCE")
if default_source is None:
    default_source = "Clock"
controller = InputController(default_source)

def message_handler(command: dict, topic: str | None = None):
    if command["Command"] == "ChangeMode":
        target_mode = command["TargetMode"]
        try:
            controller.set_source(target_mode)
            client.publish(f"{mqtt_topic}/stat", json.dumps({
                "CurrentMode": target_mode
            }))
        except InvalidSourceException as e:
            logger.warn(f"Requested source name {target_mode} is invalid")
        
def on_connect(client: mqtt.Client, userData, flags: dict, rc: int, properties=None):
    logger.info(f"Connected to MQTT Broker with result code: {rc}")    
    logger.info(f"Subscribing to MQTT topic: '{mqtt_topic}/cmnd'")
    client.subscribe(f"{mqtt_topic}/cmnd")
    client.publish(mqtt_availability_topic, payload=mqtt_online_payload, qos=1, retain=True)

def on_message(client: mqtt.Client, userData, msg: mqtt.MQTTMessage):
    logger.info(f"Received message: '{msg.payload.decode()} on topic '{msg.topic}' with QoS {msg.qos}")

    if msg.topic == f"{mqtt_topic}/cmnd":
        command_str = msg.payload.decode()
        try:
            command = json.loads(command_str)
            message_handler(command, msg.topic)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid command format: {command_str}")

client = mqtt.Client(CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

client.will_set(mqtt_availability_topic, payload=mqtt_offline_payload, qos=1, retain=True)

logger.info("Connecting to MQTT Broker...")
client.connect(mqtt_broker, port_num, mqtt_keepalive_interval)
logger.info("Starting MQTT client loop")
client.loop_start()

run = True
try:
    controller.start()
    client.publish(f"{mqtt_topic}/stat", json.dumps({
        "CurrentMode": controller.current_source
    }))
    while(run):
        time.sleep(1)
except KeyboardInterrupt:
    logger.info("Interrupt received, stopping...")
    run = False
except Exception as e:
    logger.exception("Caught an exception")
finally:
    controller.stop()
    logger.info("Released all controller resources")
    client.publish(mqtt_availability_topic, payload=mqtt_offline_payload, qos=1, retain=True)
    client.disconnect()
    client.loop_stop()
    logger.info("Disconnected from MQTT")
    logger.info("Image-Sender exiting")
    memory_handler.flush()