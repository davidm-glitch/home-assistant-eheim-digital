# !!! WORK IN PROGRESS !!!
!!! NOT YET FULLY FUNCTIONAL !!!


# EHEIM Digital integration for Home Assistant (unofficial) 

![Alt Productfamily](https://eheim.com/media/image/2d/b5/2c/EHEIM-digital_banner-collage-alle-produkte_1980x1100.jpg)


## Installation

### Step 1
Install MQTT Broker in Home Assistant

### Step 2
Install "Advanced SSH & Web Terminal" from the Add-On Store.
Set a password inside configuration tab of the Add-On and save.
Disable safe mode, enable show in sidebar and start the Add-On.

### Step 3
Inside your config folder create a new folder "eheim_digital".
Copy the "eheim_digital.py" file into it. 

### Step 4
Adjust configuration part of the eheim_digital.py file.

### Step 5
Add this to your Home Assistant configuration.yaml

Remove or change the entities to suit your setup.

```yaml
mqtt:
  switch:
    # HEATER
    - command_topic: "eheim_digital/set/heater/is_active"
      name: EHEIM heater active
      icon: mdi:heat-wave
      device_class: switch
      state_topic: "eheim_digital/heater/is_active"
      <<: &eheim_heater_availability
        availability:
          - topic: "eheim_digital/status"
            payload_available: "online"
            payload_not_available: "offline"
          - topic: "eheim_digital/heater/status"
            payload_available: "online"
            payload_not_available: "offline"
        availability_mode: all

    # FILTER
    - command_topic: "eheim_digital/set/filter/filter_running"
      name: EHEIM filter running
      icon: mdi:air-filter
      device_class: switch
      state_topic: "eheim_digital/filter/filter_running"
      <<: &eheim_filter_availability
        availability:
          - topic: "eheim_digital/status"
            payload_available: "online"
            payload_not_available: "offline"
          - topic: "eheim_digital/filter/status"
            payload_available: "online"
            payload_not_available: "offline"
        availability_mode: all

    # LED CONTROL
    - command_topic: "eheim_digital/set/led_control/moon/moonlight_active"
      name: EHEIM LED Control moonlight acitve
      icon: mdi:weather-night
      device_class: switch
      state_topic: "eheim_digital/led_control/moon/moonlight_active"
      <<: &eheim_led_control_availability
        availability:
          - topic: "eheim_digital/status"
            payload_available: "online"
            payload_not_available: "offline"
          - topic: "eheim_digital/led_control/status"
            payload_available: "online"
            payload_not_available: "offline"
        availability_mode: all
    - command_topic: "eheim_digital/set/led_control/moon/moonlight_cycle"
      name: EHEIM LED Control moonlight cycle
      icon: mdi:chart-bell-curve-cumulative
      device_class: switch
      state_topic: "eheim_digital/led_control/moon/moonlight_cycle"
      <<: *eheim_led_control_availability
    - command_topic: "eheim_digital/set/led_control/cloud/cloud_active"
      name: EHEIM LED Control cloud active
      icon: mdi:cloud
      device_class: switch
      state_topic: "eheim_digital/led_control/cloud/cloud_active"
      <<: *eheim_led_control_availability
    - command_topic: "eheim_digital/set/led_control/acclimate/acclimate_active"
      name: EHEIM LED Control acclimate active
      icon: mdi:flower
      device_class: switch
      state_topic: "eheim_digital/led_control/acclimate/acclimate_active"
      <<: *eheim_led_control_availability
    - command_topic: "eheim_digital/set/led_control/acclimate/acclimate_pause"
      name: EHEIM LED Control acclimate pause
      icon: mdi:pause
      device_class: switch
      state_topic: "eheim_digital/led_control/acclimate/acclimate_pause"
      <<: *eheim_led_control_availability

  binary_sensor:
    # HEATER
    - name: EHEIM Heater alert
      state_topic: "eheim_digital/heater/alert"
      device_class: problem
      icon: mdi:thermometer-alert
      <<: *eheim_heater_availability
    - name: EHEIM Heater is heating
      state_topic: "eheim_digital/heater/is_heating"
      device_class: running
      icon: mdi:heat-wave
      <<: *eheim_heater_availability

    # PH CONTROL
    - name: EHEIM pH control acclimatization
      state_topic: "eheim_digital/ph_control/acclimatization"
      device_class: running
      icon: mdi:sun-clock
      <<: &eheim_ph_control_availability
        availability:
          - topic: "eheim_digital/status"
            payload_available: "online"
            payload_not_available: "offline"
          - topic: "eheim_digital/ph_control/status"
            payload_available: "online"
            payload_not_available: "offline"
        availability_mode: all
    - name: EHEIM pH control active
      state_topic: "eheim_digital/ph_control/is_active"
      device_class: running
      icon: mdi:toggle-switch
      <<: *eheim_ph_control_availability
    - name: EHEIM pH control alert
      state_topic: "eheim_digital/ph_control/alert"
      device_class: problem
      icon: mdi:water-alert
      <<: *eheim_ph_control_availability
    - name: EHEIM pH control valve active
      state_topic: "eheim_digital/ph_control/is_active_valve"
      device_class: running
      icon: mdi:pipe-valve
      <<: *eheim_ph_control_availability


  sensor:
    # HEATER
    - name: EHEIM Heater current temperature
      state_topic: "eheim_digital/heater/current_temperature"
      device_class: temperature
      unit_of_measurement: °C
      <<: *eheim_heater_availability

    # FILTER
    - name: EHEIM Filter operating time
      state_topic: "eheim_digital/filter/operating_time"
      unit_of_measurement: "h"
      icon: mdi:timer
      <<: *eheim_filter_availability
    - name: EHEIM Filter end time night mode
      state_topic: "eheim_digital/filter/end_time_night_mode"
      icon: mdi:clock-time-eight
      <<: *eheim_filter_availability
    - name: EHEIM Filter start time night mode
      state_topic: "eheim_digital/filter/start_time_night_mode"
      icon: mdi:clock-time-six
      <<: *eheim_filter_availability
    - name: EHEIM Filter current speed
      state_topic: "eheim_digital/filter/current_speed"
      unit_of_measurement: "%"
      icon: mdi:speedometer
      <<: *eheim_filter_availability
    - name: EHEIM Filter next service
      state_topic: "eheim_digital/filter/next_service"
      device_class: date
      icon: mdi:wrench-clock
      <<: *eheim_filter_availability
    - name: EHEIM Filter turn off time
      state_topic: "eheim_digital/filter/turn_off_time"
      unit_of_measurement: "s"
      icon: mdi:timer
      <<: *eheim_filter_availability

    # LED CONTROL
    - name: EHEIM LED Control white brightness
      state_topic: "eheim_digital/led_control/ccv/ccv_current_brightness_white"
      unit_of_measurement: "%"
      icon: mdi:format-color-fill
      <<: *eheim_led_control_availability
    - name: EHEIM LED Control plants gold brightness
      state_topic: "eheim_digital/led_control/ccv/ccv_current_brightness_plants_gold"
      unit_of_measurement: "%"
      icon: mdi:format-color-fill
      <<: *eheim_led_control_availability
    - name: EHEIM LED Control royal blue brightness
      state_topic: "eheim_digital/led_control/ccv/ccv_current_brightness_royal_blue"
      unit_of_measurement: "%"
      icon: mdi:format-color-fill
      <<: *eheim_led_control_availability
    - name: EHEIM LED Control brightness
      state_topic: "eheim_digital/led_control/ccv/ccv_current_brightness"
      unit_of_measurement: "%"
      icon: mdi:format-color-fill
      <<: *eheim_led_control_availability

    # PH CONTROL
    - name: EHEIM pH control current ph
      state_topic: "eheim_digital/ph_control/current_ph"
      icon: mdi:ph
      <<: *eheim_ph_control_availability
    - name: EHEIM pH control set kh
      state_topic: "eheim_digital/ph_control/set_kh"
      <<: *eheim_ph_control_availability
    - name: EHEIM pH control target ph
      state_topic: "eheim_digital/ph_control/target_ph"
      icon: mdi:ph
      <<: *eheim_ph_control_availability

  select:
    # HEATER

    # FILTER
    - command_topic: "eheim_digital/set/filter/pump_mode"
      state_topic: "eheim_digital/filter/pump_mode"
      icon: mdi:pump
      <<: *eheim_filter_availability
      name: "EHEIM filter pump mode"
      options:
        - "constant"
        - "bio"
        - "pulse"
        - "manual"

  number:
    # HEATER
    - command_topic: "eheim_digital/set/heater/target_temperature"
      state_topic: "eheim_digital/heater/target_temperature"
      name: EHEIM Heater target temperature
      unit_of_measurement: °C
      icon: mdi:thermometer
      min: 18
      max: 32
      step: 0.5
      availability:
        - topic: "eheim_digital/heater/is_active"
          payload_available: "ON"
          payload_not_available: "OFF"
        - topic: "eheim_digital/status"
          payload_available: "online"
          payload_not_available: "offline"
        - topic: "eheim_digital/heater/status"
          payload_available: "online"
          payload_not_available: "offline"
      availability_mode: all

    # FILTER
    - command_topic: "eheim_digital/set/filter/target_speed"
      state_topic: "eheim_digital/filter/target_speed"
      name: EHEIM Filter target speed
      unit_of_measurement: "%"
      icon: mdi:speedometer
      availability:
        - topic: "eheim_digital/filter/filter_running"
          payload_available: "ON"
          payload_not_available: "OFF"
        - topic: "eheim_digital/status"
          payload_available: "online"
          payload_not_available: "offline"
        - topic: "eheim_digital/filter/status"
          payload_available: "online"
          payload_not_available: "offline"
      availability_mode: all
      min: 44
      max: 100
      step: 1
```

### Step 6
Restart Home Assistant

### Step 7
Open Terminal from the sidebar. Enter the following commands.

`docker exec -it homeassistant bash`

`cd eheim_digital`

`python3 -m venv eheim_digital`

`source eheim_digital/bin/activate`

`pip install asyncio websockets paho-mqtt`

`python eheim_digital.py`


### Step 8
Make sure that you enable safe mode of Terminal Add-On!

### Step 9
Script should run now and send data to Home Assistant


--------------------------


## Compatible devices
### External filters
| Name | Integrated | Tested | Version Website | Version Server |
| --- | --- | --- | --- | --- |
| professionel 5e 350 | Yes | No | 1.01.3 | 1.00.8 |
| professionel 5e 450 | Yes | No | | |
| professionel 5e 600T | Yes | No | | |
| professionel 5e 700 | Yes | Yes | 1.01.3 | 1.00.8 |

### Heaters
| Name | Integrated | Tested | Version Website | Version Server |
| --- | --- | --- | --- | --- |
| thermocontrol+ e 150 | Yes | No | | |
| thermocontrol+ e 200 | Yes | No | | |
| thermocontrol+ e 250 | Yes | No | | |
| thermocontrol+ e 300 | Yes | Yes | 1.01.3 | 1.00.8 |

### Lighting control
<sub>v2 can be identified by the yellow stripe on the device</sub>
| Name | Integrated | Tested | Version Website | Version Server |
| --- | --- | --- | --- | --- |
| LEDcontrol+e | No | No | | |
| LEDcontrol+e v2 | partially | Yes | 2.01.6 | 2.01.6 |


### CO2
| Name | Integrated | Tested | Version Website | Version Server |
| --- | --- | --- | --- | --- |
| pHcontrol+e | partially | No | 2.01.6 | 2.01.6 |

### Feeding
| Name | Integrated | Tested | Version Website | Version Server |
| --- | --- | --- | --- | --- |
| autofeeder+ | No | No | | |

### Climate control 
| Name | Integrated | Tested | Version Website | Version Server |
| --- | --- | --- | --- | --- |
| climacontrol+ S | No | No | | |
| climacontrol+ M | No | No | | |
| climacontrol+ L | No | No | | |

### UV-Sterilizer
| Name | Integrated | Tested | Version Website | Version Server |
| --- | --- | --- | --- | --- |
| reeflexUV+e 500 | No | No | | |
| reeflexUV+e 800 | No | No | | |
| reeflexUV+e 1500 | No | No | | |
| reeflexUV+e 2000 | No | No | | |
