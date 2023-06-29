"""Custom eheim_digital Integration"""
import os
import sys
import yaml
import asyncio
import logging
import websockets
import json
import time
import paho.mqtt.client as paho_mqtt_client
from functools import partial

config_file = os.path.exists('config.yaml')

if config_file:
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        mqtt = config['mqtt']
        gen = config['general']
    MQTT_HOST = mqtt.get('host')
    MQTT_PORT = mqtt.get('port', 1883)
    MQTT_USER = mqtt.get('user')
    MQTT_PASSWORD = mqtt.get('password')
    MQTT_QOS = mqtt.get('qos', 1)
    BASE_TOPIC = mqtt.get('base_topic', 'eheim_digital')
    HOME_ASSISTANT = mqtt.get('home_assistant', True)
    DEVICE_HOST = gen.get('host')
    DEVICES = gen.get('devices')
    LOG_LEVEL = gen.get('log_level', 'INFO').upper()
else:
    MQTT_HOST = os.getenv('MQTT_HOST')
    MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
    MQTT_USER = os.getenv('MQTT_USER')
    MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
    MQTT_QOS = int(os.getenv('MQTT_QOS', 1))
    BASE_TOPIC = os.getenv('BASE_TOPIC', 'eheim_digital')
    HOME_ASSISTANT = os.getenv('HOME_ASSISTANT', True)
    DEVICE_HOST = os.getenv('DEVICE_HOST')
    DEVICES = os.getenv('DEVICES')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

version = '0.0.1'
FILTER_RECEIVED_MESSAGES = {"filter": "FILTER_DATA", "heater": "HEATER_DATA"}
FILTER_REQUEST_MESSAGES = {"filter": "GET_FILTER_DATA", "heater": "GET_EHEATER_DATA"}
mqtt_client = paho_mqtt_client.Client(BASE_TOPIC)


def convert_filter_pump_mode_to_string(pump_mode) -> str:
    match pump_mode:
        case 1:
            return 'constant'
        case 4:
            return 'bio'
        case 8:
            return 'pulse'
        case 16:
            return 'manual'
        case 24577:
            return 'calibrating'
        case 8193:
            return 'calibrating'
        case _:
            return 'unknown'


def convert_boolean_to_string(boolean) -> str:
    return 'ON' if boolean else 'OFF'


async def mqtt_connect(loop):
    """Connect to MQTT broker and set LWT"""
    try:
        mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
        mqtt_client.will_set(f'{BASE_TOPIC}/status', 'offline', 1, True)
        mqtt_client.on_message = on_mqtt_message
        mqtt_client.on_connect = on_mqtt_connect
        mqtt_client.connect(MQTT_HOST, MQTT_PORT)
        await asyncio.sleep(1)  # Wait for MQTT connection to establish
        await asyncio.get_event_loop().run_in_executor(None, mqtt_client.loop_forever)
    except Exception as e:
        logging.error(f'Unable to connect to MQTT broker: {e}')
        sys.exit(1)

    # Add a return statement to explicitly return a coroutine
    return


def on_mqtt_connect(mqtt_client):

    logging.info('Connected to MQTT broker')

    mqtt_client.publish(f'{BASE_TOPIC}/status', 'online', 1, True)


def on_mqtt_message(mqtt_client, userdata, msg):
    """Listen for MQTT payloads"""



async def websocket_connect():
    url = f"ws://{DEVICE_HOST}/ws"
    async with websockets.connect(url) as websocket:
        task_listen = asyncio.create_task(websocket_listen(websocket))
        task_send_messages = asyncio.create_task(websocket_send_messages(websocket))

        await asyncio.gather(task_listen, task_send_messages)


async def websocket_send_messages(websocket):
    messages = []
    for device in DEVICES:
        messages.append(
            '{"title":"%s","from":"USER","to":"%s"}' % (FILTER_REQUEST_MESSAGES[device['type']], device['mac']))

    while True:
        await asyncio.sleep(2)
        for message in messages:
            await websocket.send(message)


async def websocket_listen(websocket):
    while True:
        messages = await websocket.recv()
        messages = json.loads(messages)
        if isinstance(messages, list):
            for message in messages:
                websocket_handle_message(message)
        elif isinstance(messages, dict):
            websocket_handle_message(messages)


def websocket_publish(topic, message, qos: int = 0, retain: bool = False):
    if not mqtt_client.is_connected():
        try:
            mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
            mqtt_client.connect(MQTT_HOST, MQTT_PORT)
            mqtt_client.loop_start()
            time.sleep(1)  # Wait for MQTT connection to establish
        except Exception as e:
            logging.error(f'Unable to connect to MQTT broker: {e}')
            return

    result = mqtt_client.publish(BASE_TOPIC + topic, message, qos, retain)
    status = result[0]
    if status != 0:
        print(f'Failed to send message to topic {BASE_TOPIC + topic}')


def websocket_handle_message(data):
    # TODO: check why next line is needed
    websocket_publish('/status', 'online', 1, True)
    for device in DEVICES:
        if data['title'] == FILTER_RECEIVED_MESSAGES[device['type']]:
            if device['type'] == 'heater':
                is_active = convert_boolean_to_string(bool(data['active']))  # active / inactive
                alert = convert_boolean_to_string(bool(data['alertState']))  # active / inactive
                is_heating = convert_boolean_to_string(bool(data['isHeating']))  # heating / waiting
                current_temperature = round((int(data['isTemp']) / 10), 1)  # in °C
                target_temperature = round((int(data['sollTemp']) / 10), 1)  # in °C

                websocket_publish('/heater/is_active', is_active)
                websocket_publish('/heater/alert', alert)
                websocket_publish('/heater/is_heating', is_heating)
                websocket_publish('/heater/current_temperature', current_temperature)
                websocket_publish('/heater/target_temperature', target_temperature)

                websocket_publish('/heater/status', 'online', 1, True)

            if device['type'] == 'filter':
                operating_time = round(int(data['actualTime']) / 60)  # in hours
                end_time_night_mode = int(data['end_time_night_mode'])  # minutes after 00:00
                start_time_night_mode = int(data['start_time_night_mode'])  # minutes after 00:00
                filter_running = convert_boolean_to_string(bool(data['filterActive']))  # running / not running
                current_speed = round((int(data['freq']) / int(data['maxFreqRglOff']) if data['maxFreqRglOff'] else 0) * 100)  # in %
                target_speed = round((int(data['freqSoll']) / int(data['maxFreqRglOff']) if data['maxFreqRglOff'] else 0) * 100)  # in %
                pump_mode = convert_filter_pump_mode_to_string(int(data['pumpMode']))
                next_service = int(data['serviceHour'])  # in hours
                turn_off_time = int(data['turnOffTime'])  # in seconds

                websocket_publish('/filter/operating_time', operating_time)
                websocket_publish('/filter/end_time_night_mode', end_time_night_mode)
                websocket_publish('/filter/start_time_night_mode', start_time_night_mode)
                websocket_publish('/filter/filter_running', filter_running)
                websocket_publish('/filter/current_speed', current_speed)
                websocket_publish('/filter/target_speed', target_speed)
                websocket_publish('/filter/pump_mode', pump_mode)
                websocket_publish('/filter/next_service', next_service)
                websocket_publish('/filter/turn_off_time', turn_off_time)

                websocket_publish('/filter/status', 'online', 1, True)


async def main():
    loop = asyncio.get_event_loop()

    # Start the MQTT connection in a separate task
    mqtt_task = partial(mqtt_connect, loop=loop)
    mqtt_task = loop.run_in_executor(None, mqtt_task)

    # Run the WebSocket connection
    websocket_task = loop.create_task(websocket_connect())

    # Wait for both tasks to complete
    await asyncio.gather(mqtt_task, websocket_task)


if __name__ == '__main__':
    if LOG_LEVEL.lower() not in ['debug', 'info', 'warning', 'error']:
        logging.warning(f'Selected log level "{LOG_LEVEL}" is not valid; using default (info)')
    else:
        logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s %(levelname)s: %(message)s')

    logging.info(f'=== eheim_digital version {version} started ===')

    if config_file:
        logging.info('Configuration file found.')
    else:
        logging.info('No configuration file found; loading environment variables.')

    if DEVICES is None:
        logging.error('Please specify the devices in your config file.')
        logging.error('Exiting...')
        sys.exit(1)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
