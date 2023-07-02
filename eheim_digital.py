"""Custom eheim_digital Integration"""
import os
import sys
import yaml
import asyncio
import logging
import websockets
import json
import time
from datetime import datetime, timedelta
import paho.mqtt.client as paho_mqtt_client

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
    WEBSOCKET_SEND_REQUEST_FREQUENCY = gen.get('request_frequency')
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
    WEBSOCKET_SEND_REQUEST_FREQUENCY = os.getenv('REQUEST_FREQUENCY', 10)
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

version = '0.0.1'
mqtt_client = paho_mqtt_client.Client(BASE_TOPIC)
FILTER_RECEIVED_MESSAGES = {
    "filter": {"FILTER_DATA"},
    "heater": {"HEATER_DATA"},
    "led_control": {"CCV", "ACCLIMATE", "DYCL", "MOON", "CLOUD", "DSCRPTN"}
}
FILTER_REQUEST_MESSAGES = {
    "filter": {"GET_FILTER_DATA"},
    "heater": {"GET_EHEATER_DATA"},
    "led_control": {"REQ_CCV", "GET_ACCL", "GET_DYCL", "GET_MOON", "GET_CLOUD", "GET_DSCRPTN"}
}
LAST_SEEN_TIMESTAMP = {
    "filter": 0,
    "heater": 0,
    "led_control": 0
}
MQTT_RECONNECT_DELAY = 10  # in s


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


def convert_string_to_int(string) -> int:
    if string == 'ON':
        return 1
    return 0


def convert_values(value, left_min, left_max, right_min, right_max):
    left_span = left_max - left_min
    right_span = right_max - right_min
    value_scaled = float(value - left_min) / float(left_span)
    return int(right_min + (value_scaled * right_span))


def convert_hours_to_date(hours):
    return (datetime.now() + timedelta(hours=hours)).strftime("%Y-%m-%d")


def mqtt_connect():
    def on_mqtt_connect(client, userdata, flags, rc):
        if rc == 0:
            logging.info("Connected to MQTT Broker!")
        else:
            logging.error("Failed to connect, return code %d\n", rc)

    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.will_set(f'{BASE_TOPIC}/status', 'offline', 1, True)
    mqtt_client.on_disconnect = on_mqtt_disconnect
    mqtt_client.on_message = on_mqtt_message
    mqtt_client.on_connect = on_mqtt_connect
    mqtt_client.connect(MQTT_HOST, MQTT_PORT)
    mqtt_client.subscribe(f'{BASE_TOPIC}/set/#')
    mqtt_client.publish(f'{BASE_TOPIC}/status', 'online', 1, True)
    for device in DEVICES:
        mqtt_client.publish(f'{BASE_TOPIC}/{device["type"]}/status', 'offline', 1, True)

    return mqtt_client


def on_mqtt_disconnect(client, userdata, rc):
    logging.info("Disconnected with result code: %s", rc)
    reconnect_count = 0
    while True:
        logging.info("Reconnecting in %d seconds...", MQTT_RECONNECT_DELAY)
        time.sleep(MQTT_RECONNECT_DELAY)

        try:
            client.reconnect()
            logging.info("Reconnected successfully!")
            return
        except Exception as err:
            logging.error("%s. Reconnect failed. Retrying...", err)

        reconnect_count += 1
        logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)


def on_mqtt_message(client, userdata, msg):
    device_type = msg.topic.split("/")[2]
    command = msg.topic.split("/")[3]
    payload = msg.payload.decode()
    messages = []
    for device in DEVICES:
        if device['type'] == device_type:
            if device_type == 'filter':
                match command:
                    case 'filter_running':
                        messages.append('{"title": "SET_FILTER_PUMP", "to": "%s", "active": "%s", "from": "USER"}' % (
                            device['mac'], convert_string_to_int(payload)))
                    case 'pump_mode':
                        if payload == 'constant':
                            messages.append(
                                '{"title":"START_FILTER_NORMAL_MODE_WITH_COMP","to":"%s","from":"USER"}' % device[
                                    'mac'])
                        if payload == 'bio':
                            messages.append('{"title":"START_NOCTURNAL_MODE","to":"%s","from":"USER"}' % device['mac'])
                        if payload == 'pulse':
                            messages.append(
                                '{"title":"START_FILTER_PULSE_MODE","to":"%s","from":"USER"}' % device['mac'])
                        if payload == 'manual':
                            messages.append(
                                '{"title":"START_FILTER_NORMAL_MODE_WITHOUT_COMP","to":"%s","from":"USER"}' % device[
                                    'mac'])
                    case 'target_speed':
                        if pump_mode == 'constant':
                            messages.append(
                                '{"title":"START_FILTER_NORMAL_MODE_WITH_COMP","to":"%s","flow_rate":"%s","from":"USER"}' % (
                                    device['mac'], convert_values(int(payload), 44, 100, 0, 10)))
                        if pump_mode == 'manual':
                            messages.append(
                                '{"title":"START_FILTER_NORMAL_MODE_WITHOUT_COMP","to":"%s","frequency":"%s","from":"USER"}' % (
                                    device['mac'], int(8000 * int(payload) / 100)))

            if device_type == 'heater':
                match command:
                    case 'is_active':
                        messages.append('{"title":"SET_EHEATER_PARAM","to":"%s","active": "%s","from":"USER"}' % (
                            device['mac'], convert_string_to_int(payload)))
                    case 'target_temperature':
                        messages.append(
                            '{"title":"SET_EHEATER_PARAM","to":"%s","sollTemp":"%s","active": 1,"from":"USER"}' % (
                                device['mac'], int(float(payload) * 10)))

    for message in messages:
        asyncio.run(userdata.send(message))


async def websocket_connect():
    url = f"ws://{DEVICE_HOST}/ws"
    async with websockets.connect(url, ping_interval=None) as websocket:
        mqtt_client.user_data_set(websocket)
        task_listen = asyncio.create_task(websocket_listen(websocket))
        task_send_data_request_messages = asyncio.create_task(websocket_send_data_request_messages(websocket))

        await asyncio.gather(task_listen, task_send_data_request_messages)


async def websocket_send_data_request_messages(websocket):
    messages = []
    for device in DEVICES:
        for request_message in FILTER_REQUEST_MESSAGES[device['type']]:
            messages.append('{"title":"%s","from":"USER","to":"%s"}' % (request_message, device['mac']))

    while True:
        await asyncio.sleep(WEBSOCKET_SEND_REQUEST_FREQUENCY)
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


def websocket_handle_message(data):
    for device in DEVICES:
        for received_message in FILTER_RECEIVED_MESSAGES[device['type']]:
            if data['title'] == received_message:
                if device['type'] == 'heater':
                    LAST_SEEN_TIMESTAMP["heater"] = int(datetime.now().timestamp())

                    is_active = convert_boolean_to_string(bool(data['active']))  # active / inactive
                    alert = convert_boolean_to_string(bool(data['alertState']))  # active / inactive
                    is_heating = convert_boolean_to_string(bool(data['isHeating']))  # heating / waiting
                    current_temperature = round((int(data['isTemp']) / 10), 1)  # in °C
                    target_temperature = round((int(data['sollTemp']) / 10), 1)  # in °C

                    mqtt_client.publish(f'{BASE_TOPIC}/heater/is_active', is_active)
                    mqtt_client.publish(f'{BASE_TOPIC}/heater/alert', alert)
                    mqtt_client.publish(f'{BASE_TOPIC}/heater/is_heating', is_heating)
                    mqtt_client.publish(f'{BASE_TOPIC}/heater/current_temperature', current_temperature)
                    mqtt_client.publish(f'{BASE_TOPIC}/heater/target_temperature', target_temperature)

                    mqtt_client.publish(f'{BASE_TOPIC}/heater/status', 'online', 1, True)

                if device['type'] == 'filter':
                    LAST_SEEN_TIMESTAMP["filter"] = int(datetime.now().timestamp())
                    global pump_mode
                    operating_time = round(int(data['actualTime']) / 60)  # in hours
                    end_time_night_mode = int(data['end_time_night_mode'])  # minutes after 00:00
                    start_time_night_mode = int(data['start_time_night_mode'])  # minutes after 00:00
                    filter_running = convert_boolean_to_string(bool(data['filterActive']))  # running / not running
                    current_speed = round(
                        (int(data['freq']) / int(data['maxFreqRglOff']) if data['maxFreqRglOff'] else 0) * 100)  # in %
                    target_speed = round(
                        (int(data['freqSoll']) / int(data['maxFreqRglOff']) if data[
                            'maxFreqRglOff'] else 0) * 100)  # in %
                    pump_mode = convert_filter_pump_mode_to_string(int(data['pumpMode']))
                    next_service = convert_hours_to_date(int(data['serviceHour']))  # in hours
                    turn_off_time = int(data['turnOffTime'])  # in seconds

                    mqtt_client.publish(f'{BASE_TOPIC}/filter/operating_time', operating_time)
                    mqtt_client.publish(f'{BASE_TOPIC}/filter/end_time_night_mode', end_time_night_mode)
                    mqtt_client.publish(f'{BASE_TOPIC}/filter/start_time_night_mode', start_time_night_mode)
                    mqtt_client.publish(f'{BASE_TOPIC}/filter/filter_running', filter_running)
                    mqtt_client.publish(f'{BASE_TOPIC}/filter/current_speed', current_speed)
                    mqtt_client.publish(f'{BASE_TOPIC}/filter/target_speed', target_speed)
                    mqtt_client.publish(f'{BASE_TOPIC}/filter/pump_mode', pump_mode)
                    mqtt_client.publish(f'{BASE_TOPIC}/filter/next_service', next_service)
                    mqtt_client.publish(f'{BASE_TOPIC}/filter/turn_off_time', turn_off_time)

                    mqtt_client.publish(f'{BASE_TOPIC}/filter/status', 'online', 1, True)

                if device['type'] == 'led_control':
                    LAST_SEEN_TIMESTAMP["led_control"] = int(datetime.now().timestamp())

                    match received_message:
                        case 'CCV':
                            ccv_current_brightness = data['currentValues']

                            mqtt_client.publish(f'{BASE_TOPIC}/led_control/ccv/ccv_current_brightness_white', ccv_current_brightness[0])
                            mqtt_client.publish(f'{BASE_TOPIC}/led_control/ccv/ccv_current_brightness_plants_gold', ccv_current_brightness[1])
                            mqtt_client.publish(f'{BASE_TOPIC}/led_control/ccv/ccv_current_brightness_royal_blue', ccv_current_brightness[2])
                            mqtt_client.publish(f'{BASE_TOPIC}/led_control/ccv/ccv_current_brightness', int(ccv_current_brightness[0] + ccv_current_brightness[1] + ccv_current_brightness[2] / 3))

                        case 'MOON':
                            max_moon_light = int(data['maxmoonlight'])
                            min_moon_light = int(data['minmoonlight'])
                            moon_color = data['moonColor']
                            moonlight_active = convert_boolean_to_string(bool(data['moonlightActive']))
                            moonlight_cycle = convert_boolean_to_string(bool(data['moonlightCycle']))

                            mqtt_client.publish(f'{BASE_TOPIC}/led_control/moon/max_moon_light', max_moon_light)
                            mqtt_client.publish(f'{BASE_TOPIC}/led_control/moon/min_moon_light', min_moon_light)
                            # mqtt_client.publish(f'{BASE_TOPIC}/led_control/moon/moon_color', moon_color)
                            mqtt_client.publish(f'{BASE_TOPIC}/led_control/moon/moonlight_active', moonlight_active)
                            mqtt_client.publish(f'{BASE_TOPIC}/led_control/moon/moonlight_cycle', moonlight_cycle)

                        case 'CLOUD':
                            cloud_probability = int(data['probability'])
                            cloud_max_amount = int(data['maxAmount'])
                            cloud_min_intensity = int(data['minIntensity'])
                            cloud_max_intensity = int(data['maxIntensity'])
                            cloud_min_duration = int(data['minDuration'])
                            cloud_max_duration = int(data['maxDuration'])
                            cloud_active = convert_boolean_to_string(bool(data['cloudActive']))
                            cloud_mode = int(data['mode'])  # TODO: What is that?

                            mqtt_client.publish(f'{BASE_TOPIC}/led_control/cloud/cloud_probability', cloud_probability)
                            mqtt_client.publish(f'{BASE_TOPIC}/led_control/cloud/cloud_max_amount', cloud_max_amount)
                            mqtt_client.publish(f'{BASE_TOPIC}/led_control/cloud/cloud_min_intensity', cloud_min_intensity)
                            mqtt_client.publish(f'{BASE_TOPIC}/led_control/cloud/cloud_max_intensity', cloud_max_intensity)
                            mqtt_client.publish(f'{BASE_TOPIC}/led_control/cloud/cloud_min_duration', cloud_min_duration)
                            mqtt_client.publish(f'{BASE_TOPIC}/led_control/cloud/cloud_max_duration', cloud_max_duration)
                            mqtt_client.publish(f'{BASE_TOPIC}/led_control/cloud/cloud_active', cloud_active)

                        case 'ACCLIMATE':
                            acclimate_duration = int(data['duration'])
                            acclimate_intensity_reduction = int(data['intensityReduction'])
                            acclimate_current_accl_day = int(data['currentAcclDay'])
                            acclimate_active = convert_boolean_to_string(bool(data['acclActive']))
                            acclimate_pause = convert_boolean_to_string(bool(data['duration']))

                            mqtt_client.publish(f'{BASE_TOPIC}/led_control/acclimate/acclimate_duration',
                                                acclimate_duration)
                            mqtt_client.publish(f'{BASE_TOPIC}/led_control/acclimate/acclimate_intensity_reduction',
                                                acclimate_intensity_reduction)
                            mqtt_client.publish(f'{BASE_TOPIC}/led_control/acclimate/acclimate_current_accl_day',
                                                acclimate_current_accl_day)
                            mqtt_client.publish(f'{BASE_TOPIC}/led_control/acclimate/acclimate_active',
                                                acclimate_active)
                            mqtt_client.publish(f'{BASE_TOPIC}/led_control/acclimate/acclimate_pause', acclimate_pause)

                        # case 'DSCRPTN':
                        # TODO
                        # case 'DYCL':
                        # TODO

                    mqtt_client.publish(f'{BASE_TOPIC}/led_control/status', 'online', 1, True)


async def websocket_last_seen():
    while True:
        await asyncio.sleep(5)
        for device, timestamp in LAST_SEEN_TIMESTAMP.items():
            current_timestamp = int(datetime.now().timestamp())
            diff = current_timestamp - timestamp

            if diff > 30:
                mqtt_client.publish(f'{BASE_TOPIC}/{device}/status', 'offline', 1, True)
                logging.info("device %s is offline" % device)


async def main():
    loop = asyncio.get_event_loop()

    global mqtt_client
    mqtt_client = mqtt_connect()
    mqtt_client.loop_start()

    websocket_task = loop.create_task(websocket_connect())

    last_seen_task = loop.create_task(websocket_last_seen())

    await asyncio.gather(websocket_task, last_seen_task)


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
